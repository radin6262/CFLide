# --- IMPORTS FOR core/editor.py ---
from PySide6.QtWidgets import (
    QWidget, QTabWidget, QPlainTextEdit, QScrollBar, 
    QMessageBox, QFileDialog
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QTextCharFormat, 
    QTextCursor, QSyntaxHighlighter
)
from PySide6.QtCore import (
    QSize, Qt, QRect, QFileInfo, QSignalBlocker, 
    QFile, QIODevice, Signal, QRegularExpressionMatch, QRegularExpression
)

# ------------------------------------------------------------------
# 🚨 LINE NUMBER AREA WIDGET 
# ------------------------------------------------------------------

class LineNumberArea(QWidget):
    """Custom widget to draw line numbers."""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        
    def sizeHint(self):
        """Tells the layout manager the required width."""
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        """Delegates the painting to the editor's core logic."""
        self.editor.lineNumberAreaPaintEvent(event)

# ------------------------------------------------------------------
# 🚨 CODE EDITOR CORE (The Text Input Widget)
# ------------------------------------------------------------------

class CodeEditorCore(QPlainTextEdit): 
    
    # Signal to notify the main window that the document's state has changed
    document_title_changed = Signal(str) 

    def __init__(self, parent=None, file_path=None):
        super().__init__(parent)
        
        # Internal state
        self._file_path = file_path
        self._is_dirty = False
        self._title = "Untitled" if file_path is None else QFileInfo(file_path).fileName()

        # Appearance setup (basic example)
        font = QFont("Monospace", 10)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))

        # 🚨 LINE NUMBER IMPLEMENTATION START
        self.lineNumberArea = LineNumberArea(self)
        
        # Connect necessary signals
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        # Connect vertical scroll bar value changes
        self.verticalScrollBar().valueChanged.connect(lambda: self.updateLineNumberArea(self.rect(), 0))
        
        # Initial call to set the margin
        self.updateLineNumberAreaWidth(0)
        # 🚨 LINE NUMBER IMPLEMENTATION END
        
        # Document modification tracking
        self.document().modificationChanged.connect(self._update_dirty_state)
        self.document().setModified(False)

        # Initial title update
        self.document_title_changed.emit(self.get_tab_title())
        
    def get_tab_title(self):
        """Returns the title string for the QTabWidget."""
        star = " *" if self._is_dirty else ""
        return self._title + star

    def get_file_path(self):
        return self._file_path

    # Added required method for Save As fallback in CFL main window (new feature)
    def get_default_filename(self):
        """Provides a default name for Save As dialog if file is untitled."""
        # Ensure 'untitled' default gets a .txt extension
        if "untitled" in self._title.lower() and not self._title.endswith(('.txt', '.py')):
            return self._title + ".txt"
        return self._title

    def _update_dirty_state(self, modified):
        """Updates the dirty state and notifies the main window."""
        self._is_dirty = modified
        self.document_title_changed.emit(self.get_tab_title())

    # -------------------------------------------------------------
    # 🚨 CORE LINE NUMBER LOGIC METHODS 
    # -------------------------------------------------------------

    def lineNumberAreaWidth(self):
        """Calculates the optimal width based on the number of lines."""
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        
        # space = 3px padding + font width * digits + 8px right margin
        space = 3 + self.fontMetrics().horizontalAdvance('0') * digits + 8
        return space

    def updateLineNumberAreaWidth(self, _):
        """Sets the margin of the viewport to reserve space for the line numbers."""
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
        
    def resizeEvent(self, event):
        """Overrides resize event to reposition the line number widget."""
        super().resizeEvent(event) 
        
        cr = self.contentsRect()
        # Set the geometry of the LineNumberArea to be on the left margin
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        """
        The method that actually draws the numbers, called by the LineNumberArea's paintEvent.
        """
        painter = QPainter(self.lineNumberArea)
        
        # --- 🎨 Styling ---
        painter.fillRect(event.rect(), QColor("#282c34")) # Background
        painter.setPen(QColor("#5c6370")) # Text color for numbers
        painter.setFont(self.font())
        # --- 🎨 Styling End ---

        # Calculate the visible area
        block = self.firstVisibleBlock()
        block_number = block.blockNumber() 
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        # Loop through all visible blocks (lines)
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line_number = str(block_number + 1) # 1-indexed line number
                
                painter.drawText(
                    0, top, self.lineNumberArea.width() - 5, self.fontMetrics().height(),
                    Qt.AlignRight, line_number
                )
                
            block = block.next()
            if not block.isValid():
                break
                
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
            
    def updateLineNumberArea(self, rect, dy):
        """
        Updates or scrolls the line number area when text is edited or scrolled.
        """
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    # -------------------------------------------------------------
    # --- File I/O and Save Logic (REQUIRED FOR MAIN WINDOW)
    # -------------------------------------------------------------

    def save_file(self, path=None):
        """Saves the document content to the specified path or current path."""
        path = path if path else self._file_path
        if not path:
            print("DEBUG: save_file called with no path, returning False.")
            return False

        file = QFile(path)
        if not file.open(QIODevice.WriteOnly | QIODevice.Text):
            print(f"DEBUG: Failed to open file for writing: {path}. Error: {file.errorString()}")
            QMessageBox.warning(self, "Save Error", f"Cannot write file {path}:\n{file.errorString()}")
            return False
        
        try:
            # We must use encode('utf-8') for reliable file writing
            file.write(self.toPlainText().encode('utf-8'))
            file.close()
            
            # Update state only upon successful save
            self._file_path = path
            self._title = QFileInfo(path).fileName()
            self.document().setModified(False) 
            self.document_title_changed.emit(self.get_tab_title()) # Notify tab widget title change
            print(f"DEBUG: Successfully saved file to: {path}")
            return True
        except Exception as e:
            print(f"DEBUG: Unexpected error during file write: {e}")
            QMessageBox.critical(self, "Write Error", f"An unexpected error occurred during save: {e}")
            return False

    def load_file_content(self, path):
        """Loads text content from a file."""
        file = QFile(path)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            QMessageBox.warning(self, "Open Error", f"Cannot read file {path}:\n{file.errorString()}")
            return False
        
        try:
            content = str(file.readAll(), 'utf-8')
            file.close()

            # Block signals while loading to prevent spurious dirty state
            with QSignalBlocker(self.document()):
                self.setPlainText(content)
            
            self._file_path = path
            self._title = QFileInfo(path).fileName()
            self.document().setModified(False)
            self.document_title_changed.emit(self.get_tab_title())
            return True
        except Exception as e:
            QMessageBox.critical(self, "Read Error", f"An unexpected error occurred during load: {e}")
            return False

# ------------------------------------------------------------------
# 🚨 EDITOR (QTabWidget wrapper, REQUIRED FOR MAIN WINDOW)
# ------------------------------------------------------------------

class Editor(QTabWidget):
    document_title_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self._close_tab)
        self.currentChanged.connect(self._handle_tab_change)
        
        # Create an initial empty file
        self.create_new_file()

    def get_current_editor(self):
        """Returns the current CodeEditorCore instance or None."""
        return self.currentWidget()

    def get_current_file_path(self):
        """Returns the file path of the current editor."""
        editor = self.get_current_editor()
        return editor.get_file_path() if editor else None

    def create_new_file(self):
        """Adds a new, unsaved tab."""
        new_editor = CodeEditorCore(self)
        
        # Connect the new editor's title change signal to the QTabWidget's signal
        new_editor.document_title_changed.connect(self._update_tab_title)
        
        index = self.addTab(new_editor, new_editor.get_tab_title())
        self.setCurrentIndex(index)
        
        # Manually ensure the main window title is updated for the new tab
        self.document_title_changed.emit(new_editor.get_tab_title())


    def load_file(self, path):
        """Checks if file is open, otherwise opens it."""
        # Check if file is already open
        for i in range(self.count()):
            editor = self.widget(i)
            if editor.get_file_path() == path:
                self.setCurrentIndex(i)
                return

        new_editor = CodeEditorCore(self)
        if new_editor.load_file_content(path):
            new_editor.document_title_changed.connect(self._update_tab_title)
            index = self.addTab(new_editor, new_editor.get_tab_title())
            self.setCurrentIndex(index)
        else:
            # Cleanup the failed editor instance
            del new_editor
        
    def save_current_file(self):
        """Saves the current file, prompting for path if unsaved."""
        editor = self.get_current_editor()
        if not editor:
            print("DEBUG: save_current_file called but no editor widget is active.")
            return False
            
        # Only skip saving if the document is NOT modified AND already has a path.
        if not editor.document().isModified() and editor.get_file_path() is not None:
            print("DEBUG: Document not modified and already saved, skipping.")
            return True

        if editor.get_file_path() is None:
            # If path is unknown, prompt for a path (Save As)
            default_name = editor.get_default_filename() or "untitled.txt"
            
            # 💡 FIX: Reordering filter to default to Text Files (*.txt)
            filter_str = "Text Files (*.txt);;All Files (*);;Python Files (*.py)"

            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_name, filter_str)
            
            if file_path:
                print(f"DEBUG: QFileDialog returned path: {file_path}")
                return editor.save_file(file_path)
            else:
                print("DEBUG: QFileDialog cancelled.")
                return False # User cancelled save
        else:
            # Existing file, perform direct save
            print(f"DEBUG: Saving existing file to: {editor.get_file_path()}")
            return editor.save_file()

    def _update_tab_title(self, title):
        """Updates the tab title and forwards the signal to the main window."""
        editor = self.sender()
        index = self.indexOf(editor)
        if index != -1:
            self.setTabText(index, title)
            
        # If this is the active tab, update the main window title
        if self.currentIndex() == index:
            self.document_title_changed.emit(title)
        
    def _handle_tab_change(self, index):
        """Handles when the active tab changes."""
        editor = self.widget(index)
        if editor:
            self.document_title_changed.emit(editor.get_tab_title())

    def _close_tab(self, index):
        """Handles closing a tab, checking for unsaved changes."""
        editor = self.widget(index)
        if editor.document().isModified():
            # Prompt user to save changes
            ret = QMessageBox.warning(self, "Unsaved Changes",
                f"Document '{editor.get_tab_title().rstrip(' *')}' has been modified.\nDo you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            if ret == QMessageBox.Save:
                if not self.save_current_file():
                    return # Cancelled save, don't close
            elif ret == QMessageBox.Cancel:
                return # Cancelled close

        # Safe to close
        self.removeTab(index)
        editor.deleteLater() 
        
        # If all tabs are closed, create a new one
        if self.count() == 0:
            self.create_new_file()