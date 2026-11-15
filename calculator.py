"""Pure-Python ideal mass-balance calculator for master-alloy additions."""

class CalculationError(ValueError):
    """Raised when the requested blend cannot be solved safely."""


def _solve_linear_system(matrix, rhs, tolerance=1e-10):
    """Solve a square system using Gauss-Jordan elimination with pivoting."""
    n = len(rhs)
    if n == 0 or len(matrix) != n or any(len(row) != n for row in matrix):
        raise CalculationError(
            "For this first version, select the same number of master alloys as controlled elements."
        )
    augmented = [list(map(float, matrix[i])) + [float(rhs[i])] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < tolerance:
            raise CalculationError(
                "The selected master alloys cannot independently achieve these targets. "
                "Try a different combination of master alloys."
            )
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        divisor = augmented[col][col]
        augmented[col] = [value / divisor for value in augmented[col]]
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            augmented[row] = [
                augmented[row][j] - factor * augmented[col][j]
                for j in range(n + 1)
            ]
    return [augmented[i][-1] for i in range(n)]


def calculate_blend(batch_kg, elements, target, base, master_alloys):
    """Calculate master-alloy and base-metal masses for an ideal final batch.

    All compositions are weight percent. The final batch mass includes the
    base metal and all additions. No process losses or element recoveries
    are applied.
    """
    if batch_kg <= 0:
        raise CalculationError("Batch weight must be greater than zero.")
    if not elements:
        raise CalculationError("At least one controlled element is required.")
    if len(master_alloys) != len(elements):
        raise CalculationError(
            "For this first version, select exactly one master alloy per controlled element."
        )

    for label, composition in [("Target", target), ("Base metal", base)]:
        for element in elements:
            value = float(composition.get(element, 0.0))
            if not 0 <= value <= 100:
                raise CalculationError(f"{label} {element} must be between 0 and 100 wt.%.")

    names = [str(item.get("name", "")).strip() for item in master_alloys]
    if any(not name for name in names):
        raise CalculationError("Every master alloy must have a name.")
    if len(set(names)) != len(names):
        raise CalculationError("Master alloy names must be unique.")

    matrix = []
    rhs = []
    for element in elements:
        row = []
        for item in master_alloys:
            value = float(item["composition"].get(element, 0.0))
            if not 0 <= value <= 100:
                raise CalculationError(
                    f"{item['name']} {element} must be between 0 and 100 wt.%."
                )
            row.append(value - float(base.get(element, 0.0)))
        matrix.append(row)
        rhs.append(batch_kg * (float(target[element]) - float(base.get(element, 0.0))))

    additions = _solve_linear_system(matrix, rhs)
    if any(value < -1e-8 for value in additions):
        raise CalculationError(
            "The selected master alloys would require a negative addition. "
            "Choose different master alloys or revise the target composition."
        )
    additions = [max(0.0, value) for value in additions]
    base_kg = batch_kg - sum(additions)
    if base_kg < -1e-8:
        raise CalculationError(
            "The calculated additions exceed the final batch weight. "
            "The selected materials cannot make this batch as specified."
        )
    base_kg = max(0.0, base_kg)

    achieved = {}
    for element in elements:
        element_mass = base_kg * float(base.get(element, 0.0)) / 100.0
        for item, addition in zip(master_alloys, additions):
            element_mass += addition * float(item["composition"].get(element, 0.0)) / 100.0
        achieved[element] = 100.0 * element_mass / batch_kg

    return {
        "batch_kg": float(batch_kg),
        "base_metal_kg": base_kg,
        "master_alloys": [
            {"name": item["name"], "kg": addition}
            for item, addition in zip(master_alloys, additions)
        ],
        "achieved_wt_pct": achieved,
    }
