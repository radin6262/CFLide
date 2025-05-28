from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QCheckBox
)
from core.settings import load_settings, save_settings, list_themes, load_theme

class SettingsUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = load_settings()
        self.parent_window = parent

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Theme selector
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        themes = list_themes()
        if not themes:
            themes = ["default"]
        self.theme_combo.addItems(themes)

        current_theme = self.settings.get("theme", "dark")
        if current_theme in themes:
            self.theme_combo.setCurrentText(current_theme)
        else:
            self.theme_combo.setCurrentIndex(0)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Autosave checkbox
        self.autosave_checkbox = QCheckBox("Enable Autosave")
        self.autosave_checkbox.setChecked(self.settings.get("autosave", False))
        layout.addWidget(self.autosave_checkbox)

        # Signals
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.autosave_checkbox.stateChanged.connect(self.on_autosave_toggled)

    def on_theme_changed(self, theme_name):
        stylesheet = load_theme(theme_name)
        if self.parent_window:
            if stylesheet:
                self.parent_window.setStyleSheet(stylesheet)
            else:
                self.parent_window.setStyleSheet("")

        self.settings["theme"] = theme_name
        save_settings(self.settings)

    def on_autosave_toggled(self, state):
        enabled = bool(state)
        self.settings["autosave"] = enabled
        save_settings(self.settings)
