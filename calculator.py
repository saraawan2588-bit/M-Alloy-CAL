"""Pure-Python ideal mass-balance calculator for master-alloy additions."""

from itertools import combinations


class CalculationError(ValueError):
    """Raised when the requested blend cannot be solved safely."""


def _solve_linear_system(matrix, rhs, tolerance=1e-10):
    """Solve a square system using Gauss-Jordan elimination with pivoting."""
    n = len(rhs)
    if n == 0 or len(matrix) != n or any(len(row) != n for row in matrix):
        raise CalculationError("The selected system is not square.")
    augmented = [list(map(float, matrix[i])) + [float(rhs[i])] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < tolerance:
            raise CalculationError("The selected master alloys are compositionally dependent.")
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
    """Calculate additions for an ideal final batch.

    The engine searches combinations of selected master alloys and uses the
    first exact, non-negative solution that leaves a non-negative base-metal
    mass. This supports selecting more master alloys than controlled elements.
    Compositions are wt.%; masses are kg.
    """
    if batch_kg <= 0:
        raise CalculationError("Batch weight must be greater than zero.")
    if not elements:
        raise CalculationError("At least one controlled element is required.")
    if len(master_alloys) < len(elements):
        raise CalculationError(
            "Select at least as many master alloys as controlled elements. "
            "A future version will support underdetermined optimized solutions."
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

    for item in master_alloys:
        for element in elements:
            value = float(item["composition"].get(element, 0.0))
            if not 0 <= value <= 100:
                raise CalculationError(
                    f"{item['name']} {element} must be between 0 and 100 wt.%."
                )

    rhs = [
        batch_kg * (float(target[element]) - float(base.get(element, 0.0)))
        for element in elements
    ]
    last_reason = "No feasible combination of the selected master alloys was found."

    for chosen_indices in combinations(range(len(master_alloys)), len(elements)):
        matrix = []
        for element in elements:
            matrix.append([
                float(master_alloys[i]["composition"].get(element, 0.0))
                - float(base.get(element, 0.0))
                for i in chosen_indices
            ])
        try:
            additions = _solve_linear_system(matrix, rhs)
        except CalculationError:
            continue
        if any(value < -1e-8 for value in additions):
            last_reason = "A candidate combination requires a negative master-alloy addition."
            continue
        additions = [max(0.0, value) for value in additions]
        base_kg = batch_kg - sum(additions)
        if base_kg < -1e-8:
            last_reason = "The candidate additions exceed the final batch weight."
            continue

        all_additions = [0.0] * len(master_alloys)
        for index, value in zip(chosen_indices, additions):
            all_additions[index] = value
        base_kg = max(0.0, base_kg)

        achieved = {}
        for element in elements:
            element_mass = base_kg * float(base.get(element, 0.0)) / 100.0
            for item, addition in zip(master_alloys, all_additions):
                element_mass += addition * float(item["composition"].get(element, 0.0)) / 100.0
            achieved[element] = 100.0 * element_mass / batch_kg

        return {
            "batch_kg": float(batch_kg),
            "base_metal_kg": base_kg,
            "master_alloys": [
                {"name": item["name"], "kg": addition}
                for item, addition in zip(master_alloys, all_additions)
            ],
            "achieved_wt_pct": achieved,
            "unused_master_alloys": [
                item["name"] for item, addition in zip(master_alloys, all_additions)
                if addition <= 1e-10
            ],
        }

    raise CalculationError(
        last_reason + " Try different master-alloy compositions or target values."
    )



def calculate_blend_actual(
    final_batch_kg, elements, target, base, master_alloys,
    metal_yield_pct, element_recovery_pct,
):
    """Calculate gross charge masses for a specified recovered-metal batch.

    metal_yield_pct is recovered liquid/solid metal mass divided by total
    charge mass. element_recovery_pct is the fraction of each selected
    element's charged mass retained in the final metal. Both must be based
    on validated process data. This is not a predictive melt-loss model.
    """
    if final_batch_kg <= 0:
        raise CalculationError("Required final metal batch must be greater than zero.")
    if not 0 < float(metal_yield_pct) <= 100:
        raise CalculationError("Measured metal yield must be greater than 0 and at most 100%.")
    if not elements:
        raise CalculationError("At least one controlled element is required.")
    if len(master_alloys) < len(elements):
        raise CalculationError(
            "Select at least as many master alloys as controlled elements."
        )

    yield_fraction = float(metal_yield_pct) / 100.0
    for element in elements:
        recovery = float(element_recovery_pct.get(element, 0.0))
        if not 0 < recovery <= 100:
            raise CalculationError(
                f"{element} recovery must be greater than 0 and at most 100%."
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

    for item in master_alloys:
        for element in elements:
            value = float(item["composition"].get(element, 0.0))
            if not 0 <= value <= 100:
                raise CalculationError(
                    f"{item['name']} {element} must be between 0 and 100 wt.%."
                )

    total_charge_kg = float(final_batch_kg) / yield_fraction
    rhs = []
    for element in elements:
        recovery = float(element_recovery_pct[element]) / 100.0
        base_assay = float(base.get(element, 0.0))
        target_assay = float(target[element])
        rhs.append(
            (float(final_batch_kg) * target_assay / recovery)
            - (total_charge_kg * base_assay)
        )

    last_reason = "No feasible combination of the selected master alloys was found."
    for chosen_indices in combinations(range(len(master_alloys)), len(elements)):
        matrix = [
            [
                float(master_alloys[i]["composition"].get(element, 0.0))
                - float(base.get(element, 0.0))
                for i in chosen_indices
            ]
            for element in elements
        ]
        try:
            additions = _solve_linear_system(matrix, rhs)
        except CalculationError:
            continue
        if any(value < -1e-8 for value in additions):
            last_reason = "A candidate combination requires a negative master-alloy addition."
            continue
        additions = [max(0.0, value) for value in additions]
        base_charge_kg = total_charge_kg - sum(additions)
        if base_charge_kg < -1e-8:
            last_reason = "The candidate additions exceed the total charge mass."
            continue

        all_additions = [0.0] * len(master_alloys)
        for index, value in zip(chosen_indices, additions):
            all_additions[index] = value
        base_charge_kg = max(0.0, base_charge_kg)

        achieved = {}
        for element in elements:
            recovery = float(element_recovery_pct[element]) / 100.0
            charged_element_kg = (
                base_charge_kg * float(base.get(element, 0.0)) / 100.0
                + sum(
                    addition * float(item["composition"].get(element, 0.0)) / 100.0
                    for item, addition in zip(master_alloys, all_additions)
                )
            )
            retained_element_kg = recovery * charged_element_kg
            achieved[element] = 100.0 * retained_element_kg / float(final_batch_kg)

        return {
            "batch_kg": float(final_batch_kg),
            "final_metal_kg": float(final_batch_kg),
            "total_charge_kg": total_charge_kg,
            "base_metal_kg": base_charge_kg,
            "master_alloys": [
                {"name": item["name"], "kg": addition}
                for item, addition in zip(master_alloys, all_additions)
            ],
            "achieved_wt_pct": achieved,
            "unused_master_alloys": [
                item["name"] for item, addition in zip(master_alloys, all_additions)
                if addition <= 1e-10
            ],
            "metal_yield_pct": float(metal_yield_pct),
            "element_recovery_pct": {
                element: float(element_recovery_pct[element]) for element in elements
            },
            "calculation_basis": "actual_process_adjusted",
        }

    raise CalculationError(
        last_reason + " Try different master-alloy compositions or target values."
    )
