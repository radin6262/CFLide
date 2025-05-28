from PySide6.QtWidgets import QTabWidget, QPlainTextEdit
import os

class Editor(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def load_file(self, file_path):
        for i in range(self.count()):
            if self.tabText(i) == os.path.basename(file_path):
                self.setCurrentIndex(i)
                return

        editor = QPlainTextEdit()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                editor.setPlainText(f.read())
            editor.setProperty("file_path", file_path)
            self.addTab(editor, os.path.basename(file_path))
            self.setCurrentWidget(editor)
        except Exception as e:
            editor.setPlainText(f"Failed to open file:\n{e}")
            self.addTab(editor, "Error")
            self.setCurrentWidget(editor)

    def get_current_editor(self):
        return self.currentWidget()

    def save_current_file(self):
        editor = self.get_current_editor()
        if editor:
            file_path = editor.property("file_path")
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                    return True
                except Exception:
                    return False
        return False

    def close_tab(self, index):
        self.removeTab(index)
