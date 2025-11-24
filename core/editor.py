from PySide6.QtWidgets import QTabWidget, QPlainTextEdit, QFileDialog
import os

class Editor(QTabWidget):
    
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

    # --- Existing Methods ---
    
    def load_file(self, file_path):
        """Opens a file in a new tab or switches to it if already open."""
        # Check if file is already open
        for i in range(self.count()):
            if self.widget(i).property("file_path") == file_path:
                self.setCurrentIndex(i)
                return

        editor = QPlainTextEdit()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                editor.setPlainText(f.read())
            
            # Store file path and mark as not needing save yet
            editor.setProperty("file_path", file_path)
            editor.setProperty("needs_save", False)
            editor.document().modificationChanged.connect(self._handle_modification)
            
            self.addTab(editor, os.path.basename(file_path))
            self.setCurrentWidget(editor)
        except Exception as e:
            editor.setPlainText(f"Failed to open file:\n{e}")
            self.addTab(editor, "Error")
            self.setCurrentWidget(editor)

    def get_current_editor(self):
        """Returns the QPlainTextEdit widget of the current tab."""
        return self.currentWidget()

    def save_current_file(self):
        """Saves the content of the current editor to its associated file path."""
        editor = self.get_current_editor()
        if editor:
            file_path = editor.property("file_path")
            
            # If it's a new, unsaved file (file_path is None), prompt for Save As
            if not file_path:
                return self._save_as()

            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(editor.toPlainText())
                    
                    editor.document().setModified(False) # Clear modified flag
                    editor.setProperty("needs_save", False)
                    return True
                except Exception:
                    return False
        return False
    
    def close_tab(self, index):
        """Handles tab closure, checking if the document needs saving."""
        editor = self.widget(index)
        if editor and editor.document().isModified():
            # NOTE: You would typically implement a QMessageBox here to prompt the user to save.
            # For simplicity, we just remove the tab for now.
            pass
            
        self.removeTab(index)

    # --- New Methods for Main App Integration ---

    def create_new_file(self):
        """Creates a new, blank, unsaved tab."""
        editor = QPlainTextEdit()
        
        # Mark the document as modified (needs saving) immediately
        editor.document().setModified(True) 
        editor.setProperty("file_path", None) # File path is unknown/unsaved
        editor.setProperty("needs_save", True)
        editor.document().modificationChanged.connect(self._handle_modification)
        
        # Add the tab with a placeholder title
        new_index = self.addTab(editor, "Untitled")
        self.setCurrentIndex(new_index)
        self.setTabText(new_index, "Untitled *") # Add asterisk to show it's unsaved

    def get_current_file_path(self):
        """
        Returns the absolute file path of the current editor tab.
        Returns None if the tab is new or unsaved.
        """
        editor = self.get_current_editor()
        if editor:
            return editor.property("file_path")
        return None
    
    # --- Internal Helper Methods ---

    def _save_as(self):
        """Handles the Save As dialog for unsaved files."""
        editor = self.get_current_editor()
        if not editor:
            return False
        
        # Open file dialog to get a new path
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "All Files (*);;Text Files (*.txt)")
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                
                # Update properties and tab title
                editor.setProperty("file_path", file_path)
                editor.document().setModified(False)
                self.setTabText(self.currentIndex(), os.path.basename(file_path))
                return True
            except Exception:
                return False
        return False

    def _handle_modification(self, modified):
        """Updates the tab title with an asterisk (*) when the document is modified."""
        editor = self.sender().parent() # Get the QPlainTextEdit widget
        index = self.indexOf(editor)
        
        current_text = self.tabText(index).rstrip(' *')
        if modified:
            self.setTabText(index, current_text + ' *')
        else:
            self.setTabText(index, current_text)