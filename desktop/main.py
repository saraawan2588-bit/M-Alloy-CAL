"""Offline desktop entry point for M-Alloy-CAL.

The desktop interface is intentionally separate from the Streamlit web app.
Both interfaces import the same root-level calculation engine and local data.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPushButton, QStackedWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

APP_NAME = "M-Alloy-CAL"
APP_VERSION = "0.1.0"


def resource_path(relative: str) -> Path:
    """Resolve bundled resources in development and PyInstaller builds."""
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    return bundle_root / relative


def load_alloy_database() -> dict:
    database_path = resource_path("data/aluminium_cast_alloys.json")
    with database_path.open("r", encoding="utf-8") as database_file:
        return json.load(database_file)


class StatCard(QFrame):
    def __init__(self, heading: str, value: str, detail: str = "") -> None:
        super().__init__()
        self.setObjectName("statCard")
        layout = QVBoxLayout(self)
        title = QLabel(heading)
        title.setObjectName("muted")
        number = QLabel(value)
        number.setObjectName("statValue")
        note = QLabel(detail)
        note.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(number)
        layout.addWidget(note)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.database = load_alloy_database()
        self.setWindowTitle(f"{APP_NAME} — Engineering Edition")
        self.resize(1180, 760)
        self.setMinimumSize(940, 620)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(224)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(18, 22, 18, 18)

        brand = QLabel("M-ALLOY-CAL")
        brand.setObjectName("brand")
        subtitle = QLabel("METALLURGICAL TOOLS")
        subtitle.setObjectName("brandSubtitle")
        side_layout.addWidget(brand)
        side_layout.addWidget(subtitle)
        side_layout.addSpacing(28)

        self.navigation = QListWidget()
        self.navigation.setObjectName("navigation")
        for label in ("Overview", "Alloy database", "Calculator", "About"):
            QListWidgetItem(label, self.navigation)
        self.navigation.setCurrentRow(0)
        side_layout.addWidget(self.navigation, 1)

        offline = QLabel("●  LOCAL DATABASE\nOffline-ready foundation")
        offline.setObjectName("offlineStatus")
        side_layout.addWidget(offline)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_overview_page())
        self.pages.addWidget(self.create_database_page())
        self.pages.addWidget(self.create_calculator_page())
        self.pages.addWidget(self.create_about_page())

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)

        self.setStyleSheet("""
            QMainWindow, QWidget { background: #f4f6f9; color: #172334; }
            #sidebar { background: #142235; }
            #brand { color: white; font-size: 21px; font-weight: 800; letter-spacing: 1px; }
            #brandSubtitle { color: #91a5bc; font-size: 9px; letter-spacing: 2px; }
            #navigation { background: transparent; border: 0; color: #c6d2df; }
            #navigation::item { padding: 13px 12px; border-radius: 7px; margin: 3px 0; }
            #navigation::item:selected { background: #29435f; color: white; }
            #offlineStatus { color: #a9d9bd; font-size: 11px; padding: 12px 4px; }
            #pageTitle { font-size: 27px; font-weight: 750; }
            #muted { color: #6b7a8d; }
            #statCard, #panel { background: white; border: 1px solid #e1e7ee; border-radius: 12px; }
            #statValue { font-size: 26px; font-weight: 750; color: #173b60; }
            #panelTitle { font-size: 16px; font-weight: 700; }
            QTableWidget { background: white; border: 1px solid #e1e7ee; gridline-color: #edf0f4; }
            QHeaderView::section { background: #edf2f7; padding: 8px; border: 0; font-weight: 650; }
            QPushButton { background: #1d5b8f; color: white; border: 0; border-radius: 7px; padding: 10px 16px; font-weight: 650; }
            QPushButton:hover { background: #174a75; }
        """)

    def page_container(self, title: str, description: str) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(18)
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        description_label = QLabel(description)
        description_label.setObjectName("muted")
        description_label.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(description_label)
        return page, layout

    def create_overview_page(self) -> QWidget:
        page, layout = self.page_container(
            "Engineering workspace",
            "A local-first desktop interface for aluminium casting-alloy calculations."
        )
        cards = QHBoxLayout()
        alloys = self.database.get("alloys", [])
        cards.addWidget(StatCard("REGISTERED STARTER GRADES", str(len(alloys)), "Local JSON database"))
        cards.addWidget(StatCard("DATABASE VERSION", self.database.get("database_version", "—"), "Bundled with the application"))
        cards.addWidget(StatCard("CALCULATION ENGINE", "Shared", "Same Python core as the web app"))
        layout.addLayout(cards)

        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        title = QLabel("Project status")
        title.setObjectName("panelTitle")
        panel_layout.addWidget(title)
        for line in (
            "The original Streamlit web application remains unchanged.",
            "This branch introduces a separate PySide6 desktop interface.",
            "The desktop application reads the same alloy database and imports the same calculation engine.",
            "Next implementation step: bring the complete multi-element charge workflow into the desktop UI.",
        ):
            item = QLabel("•  " + line)
            item.setWordWrap(True)
            panel_layout.addWidget(item)
        layout.addWidget(panel)
        layout.addStretch(1)
        return page

    def create_database_page(self) -> QWidget:
        page, layout = self.page_container(
            "Alloy database",
            "Starter aluminium casting grades bundled locally. Source and verification status remain visible."
        )
        alloys = self.database.get("alloys", [])
        table = QTableWidget(len(alloys), 4)
        table.setHorizontalHeaderLabels(["Designation", "Family", "Series", "Chemistry status"])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        for row, alloy in enumerate(alloys):
            values = [
                alloy.get("designation", ""),
                alloy.get("family", ""),
                alloy.get("series", ""),
                alloy.get("chemistry_status", "Not specified"),
            ]
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(str(value)))
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeColumnsToContents()
        layout.addWidget(table, 1)

        warning = QLabel(
            "Reference-data notice: the starter records are not yet certified against every applicable "
            "current ASTM product specification. Verify the governing standard and footnotes before production use."
        )
        warning.setWordWrap(True)
        warning.setObjectName("muted")
        layout.addWidget(warning)
        return page

    def create_calculator_page(self) -> QWidget:
        page, layout = self.page_container(
            "Charge calculator",
            "The shared calculation engine is retained. The complete multi-element desktop workflow is the next build milestone."
        )
        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        title = QLabel("Desktop calculator integration")
        title.setObjectName("panelTitle")
        panel_layout.addWidget(title)
        details = QLabel(
            "The existing calculation functions are available from the shared project module: "
            "calculate_blend() and calculate_blend_actual(). This first desktop commit establishes "
            "the offline application shell and local database loading. We will now port the web "
            "calculator's multi-element inputs, registered-grade constraints, process-adjusted mode, "
            "calculation audit and PDF export into this interface."
        )
        details.setWordWrap(True)
        panel_layout.addWidget(details)
        button = QPushButton("Check calculation engine")
        button.clicked.connect(self.check_engine)
        panel_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(panel)
        layout.addStretch(1)
        return page

    def check_engine(self) -> None:
        try:
            from calculator import calculate_blend
            result = calculate_blend(
                100.0, ["Si"], {"Si": 10.0}, {"Si": 0.0},
                [{"name": "Al-100Si test", "composition": {"Si": 100.0}}],
            )
            QMessageBox.information(
                self, "Engine check passed",
                "The shared calculation engine loaded successfully.\n\n"
                f"Test addition: {result['master_alloys'][0]['kg']:.2f} kg"
            )
        except Exception as exc:  # Show a useful diagnostic to the user.
            QMessageBox.critical(self, "Engine check failed", str(exc))

    def create_about_page(self) -> QWidget:
        page, layout = self.page_container(
            "About M-Alloy-CAL",
            "An engineering calculation tool for aluminium casting-alloy charge design."
        )
        panel = QFrame()
        panel.setObjectName("panel")
        panel_layout = QVBoxLayout(panel)
        for text in (
            f"Version: {APP_VERSION}",
            "Platform target: Windows 10/11 (64-bit)",
            "Interface: PySide6 / Qt",
            "Operation: local-first; no network service is required for calculations.",
            "Web edition: existing Streamlit application remains available separately.",
        ):
            label = QLabel(text)
            label.setWordWrap(True)
            panel_layout.addWidget(label)
        layout.addWidget(panel)
        layout.addStretch(1)
        return page


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setFont(QFont("Segoe UI", 10))
    try:
        window = MainWindow()
    except Exception as exc:
        QMessageBox.critical(None, "M-Alloy-CAL startup error", str(exc))
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
