from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QToolBar,
    QMessageBox, QCheckBox, QComboBox, QStatusBar, QMenu, QMenuBar, QLabel,
    QFileDialog # 🆕 NEW: Import QFileDialog for file/folder selection
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QStyle
from PySide6.QtCore import Qt, QTimer, Signal 
from core.settings import load_theme

# --- Core Logic Imports (UNCHANGED) ---
from core.plugins import download_plugin_list, install_plugin
from core.editor import Editor
from core.file_manager import FileManager
from core.terminal import TerminalWidget
from core.settings import load_settings, save_settings
from core.settings_ui import SettingsUI 
import sys

class CFL(QMainWindow):
    # ... (init and show_startup_alert methods remain unchanged)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CFL IDE - Professional Edition")
        self.setGeometry(100, 100, 1400, 900) 

        self.settings = load_settings()
        self.autosave_enabled = self.settings.get("autosave", False)

        self.init_ui()
        self.apply_theme(self.settings.get("theme", "dark"))

        # Autosave timer (UNCHANGED CORE LOGIC)
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30000)
        
        self.fullscreen = False
        self.show_startup_alert()
        
    def show_startup_alert(self):
        QMessageBox.information(
            self,
            "WARNING!",
            "if something goes wrong, Please read the README in GitHub."
        )
# 🎨 New: Status Bar
    def init_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Example permanent widgets for a professional look (right side)
        self.lang_label = QLabel("Language: Auto")
        self.encoding_label = QLabel("Encoding: UTF-8")
        self.status_bar.addPermanentWidget(self.lang_label)
        self.status_bar.addPermanentWidget(self.encoding_label)
        
        # Initial status message
        self.status_bar.showMessage("Ready. Welcome to CFL IDE!")
    # 🎨 UI Initialization (UNCHANGED)
    def init_ui(self):
        # 1. Main widget setup
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # 2. IDE Components setup (UNCHANGED CORE INSTANTIATION)
        self.splitter_top = QSplitter(Qt.Horizontal)
        self.file_manager = FileManager()
        self.editor = Editor()
        
        self.splitter_top.addWidget(self.file_manager)
        self.splitter_top.addWidget(self.editor)
        self.splitter_top.setSizes([280, 1120]) 

        # Terminal setup
        self.terminal = TerminalWidget()
        self.terminal.setFixedHeight(250) 

        # 3. Add widgets to main layout (UNCHANGED STRUCTURE)
        self.main_layout.addWidget(self.splitter_top)
        self.main_layout.addWidget(self.terminal)

        # 4. Connect file open request (UNCHANGED CORE LOGIC)
        self.file_manager.file_open_requested.connect(self.editor.load_file)

        # 5. Settings page (UNCHANGED CORE INSTANTIATION)
        self.settings_ui = SettingsUI(self)
        self.settings_ui.hide()

        # 6. Bar Setup
        self.init_menu_bar()
        self.init_toolbar()
        self.init_status_bar()

    # 🎨 Menu Bar (UPDATED with Open File/Folder)
    def init_menu_bar(self):
        menu_bar = QMenuBar()
        
        # --- File Menu ---
        file_menu = menu_bar.addMenu("&File")
        
        # New File
        new_action = QAction("&New File", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()

        # 🆕 NEW: Open File Action
        open_file_icon = self.style().standardIcon(QStyle.SP_DialogOpenButton)
        open_file_action = QAction("&Open File...", self)
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.setIcon(open_file_icon)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        # 🆕 NEW: Open Folder Action
        open_folder_icon = self.style().standardIcon(QStyle.SP_DirIcon)
        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.setIcon(open_folder_icon)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()

        # Save
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        save_action.setIcon(save_icon)
        save_action.triggered.connect(self.save_current)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- View Menu / Tools Menu (Remaining menus unchanged) ---
        view_menu = menu_bar.addMenu("&View")
        fullscreen_action = QAction("&Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        tools_menu = menu_bar.addMenu("&Tools")
        run_action_menu = QAction("&Run Code", self)
        run_action_menu.setShortcut("F5")
        run_action_menu.triggered.connect(self.run_code)
        tools_menu.addAction(run_action_menu)
        tools_menu.addSeparator()
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        settings_action.setIcon(settings_icon)
        settings_action.triggered.connect(lambda: self.toggle_settings_view(not self.toggle_settings_action.isChecked()))
        tools_menu.addAction(settings_action)

        self.setMenuBar(menu_bar)

    # 🎨 Toolbar Setup (UPDATED with Open File Action)
    def init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Save button
        save_icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        save_action = QAction(save_icon, "Save (Ctrl+S)", self)
        save_action.triggered.connect(self.save_current)
        toolbar.addAction(save_action)
        
        # New File Action
        new_file_icon = self.style().standardIcon(QStyle.SP_FileIcon) 
        new_file_action = QAction(new_file_icon, "New File (Ctrl+N)", self)
        new_file_action.triggered.connect(self.new_file)
        toolbar.addAction(new_file_action)
        
        # 🆕 NEW: Open File Action (added to toolbar)
        open_file_icon = self.style().standardIcon(QStyle.SP_DialogOpenButton)
        open_file_action = QAction(open_file_icon, "Open File (Ctrl+O)", self)
        open_file_action.triggered.connect(self.open_file)
        toolbar.addAction(open_file_action)

        toolbar.addSeparator()

        # Run/Execute Action 
        run_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        run_action = QAction(run_icon, "Run Code (F5)", self)
        run_action.triggered.connect(self.run_code)
        toolbar.addAction(run_action)

        toolbar.addSeparator()
        
        # Toggle Settings button
        settings_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        self.toggle_settings_action = QAction(settings_icon, "Settings", self)
        self.toggle_settings_action.setCheckable(True)
        self.toggle_settings_action.triggered.connect(self.toggle_settings_view)
        toolbar.addAction(self.toggle_settings_action)
        
    
    # 🆕 NEW CORE FUNCTION: Open Single File
    def open_file(self):
        """Opens a file dialog and loads the selected file into the editor."""
        # Use QFileDialog to get a file path
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)")

        if file_path:
            try:
                # Assuming Editor has the load_file method
                self.editor.load_file(file_path)
                self.status_bar.showMessage(f"Opened file: {file_path}", 3000)
            except AttributeError:
                QMessageBox.critical(self, "Core Error", "Editor module missing 'load_file' method.")
            except Exception as e:
                QMessageBox.critical(self, "Open Error", f"Failed to load file: {e}")
                self.status_bar.showMessage("Error: Failed to open file.", 5000)

    # 🆕 NEW CORE FUNCTION: Open Project Folder
    def open_folder(self):
        """Opens a directory dialog and sets the selected folder as the project root."""
        # Use QFileDialog to get a directory path (QFileDialog.getExistingDirectory)
        folder_path = QFileDialog.getExistingDirectory(self, "Open Project Folder", "")

        if folder_path:
            try:
                # Assuming FileManager has a set_root_path method
                self.file_manager.set_root_path(folder_path)
                self.setWindowTitle(f"CFL IDE - Project: {folder_path.split('/')[-1]}")
                self.status_bar.showMessage(f"Project folder opened: {folder_path}", 5000)
            except AttributeError:
                QMessageBox.critical(self, "Core Error", "FileManager module missing 'set_root_path' method.")
            except Exception as e:
                QMessageBox.critical(self, "Folder Error", f"Failed to set project folder: {e}")
                self.status_bar.showMessage("Error: Failed to open folder.", 5000)


    # ... (new_file, run_code, toggle_settings_view, save_current, autosave, etc., methods remain unchanged)
    def new_file(self):
        # ... (unchanged logic)
        try:
            self.editor.create_new_file()
            self.status_bar.showMessage("New file created.", 3000)
        except AttributeError:
            QMessageBox.critical(self, "Core Error", "Editor module missing 'create_new_file' method.")
            self.status_bar.showMessage("Error: Cannot create new file.", 5000)

    def run_code(self):
        # ... (unchanged logic)
        try:
            file_path = self.editor.get_current_file_path()
            if not file_path:
                QMessageBox.warning(self, "Run Error", "No file is currently open or saved to run.")
                self.status_bar.showMessage("Run Error: No file selected.", 5000)
                return

            self.terminal.execute_file(file_path)
            self.status_bar.showMessage(f"Executing: {file_path} in terminal...", 5000)
            
        except AttributeError as e:
            QMessageBox.critical(self, "Core Error", f"Missing method for running code: {e}")
            self.status_bar.showMessage("Error: Cannot execute code.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Execution Error", f"An unexpected error occurred during run: {e}")
            self.status_bar.showMessage("Execution failed.", 5000)

    # CORE FUNCTION (UNCHANGED LOGIC)
    def toggle_settings_view(self, checked):
        # ... (unchanged logic)
        self.toggle_settings_action.setChecked(checked)
        
        if checked:
            self.main_layout.removeWidget(self.splitter_top)
            self.main_layout.removeWidget(self.terminal)
            self.splitter_top.hide()
            self.terminal.hide()
            self.main_layout.addWidget(self.settings_ui)
            self.settings_ui.show()
            self.status_bar.showMessage("Settings view active.")
        else:
            self.main_layout.removeWidget(self.settings_ui)
            self.settings_ui.hide()
            self.main_layout.addWidget(self.splitter_top)
            self.main_layout.addWidget(self.terminal)
            self.splitter_top.show()
            self.terminal.show()
            self.status_bar.showMessage("IDE view active. Ready.")

    def save_current(self):
        # ... (unchanged logic)
        if not self.editor.save_current_file():
            QMessageBox.warning(self, "Save Error", "Could not save the file.")
            self.status_bar.showMessage("Save Error: Could not save file.", 5000)
        else:
            self.status_bar.showMessage("File saved successfully.", 3000) 

    def toggle_autosave(self, state):
        # ... (unchanged logic)
        self.autosave_enabled = bool(state)
        self.settings["autosave"] = self.autosave_enabled
        save_settings(self.settings)

    def autosave(self):
        # ... (unchanged logic)
        if self.autosave_enabled:
            if self.editor.save_current_file():
                self.status_bar.showMessage("Autosave triggered.", 1000) 

    def apply_theme(self, theme_name):
        # ... (unchanged logic)
        stylesheet = load_theme(theme_name)
        if stylesheet:
            self.setStyleSheet(stylesheet)
        else:
            self.setStyleSheet("")
            
    def keyPressEvent(self, event):
        # ... (unchanged logic)
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def toggle_fullscreen(self):
        # ... (unchanged logic)
        if self.fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.fullscreen = not self.fullscreen
        self.status_bar.showMessage(f"Fullscreen: {'ON' if self.fullscreen else 'OFF'}", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CFL()
    window.show()
    sys.exit(app.exec())