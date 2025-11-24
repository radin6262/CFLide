from PySide6.QtWidgets import QTreeView, QFileSystemModel
from PySide6.QtCore import Signal, QDir

class FileManager(QTreeView):
    file_open_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.model = QFileSystemModel()
        
        # Start with the current working directory, which QDir.currentPath() provides
        default_path = QDir.currentPath()
        self.model.setRootPath(default_path)
        
        self.setModel(self.model)
        
        # Set the view's root index to the default path
        self.setRootIndex(self.model.index(default_path))
        
        self.doubleClicked.connect(self.on_double_click)
        
        # Hide unnecessary columns (Size, Type, Date Modified)
        for i in range(1, self.model.columnCount()):
            self.setColumnHidden(i, True)
            
        self.setColumnWidth(0, 300) 
        self.setHeaderHidden(True) # Hide the header for a cleaner look

    def on_double_click(self, index):
        if self.model.isDir(index):
            return
        
        file_path = self.model.filePath(index)
        self.file_open_requested.emit(file_path)

    # 🆕 NEW FUNCTION: Sets the root directory for the file manager view
    def set_root_path(self, path):
        """
        Updates the QFileSystemModel to display the contents of the specified path.
        This is called by the main application when 'Open Folder' is selected.
        """
        # Ensure the path exists before attempting to set it
        if QDir(path).exists():
            self.model.setRootPath(path)
            self.setRootIndex(self.model.index(path))
            return True
        else:
            print(f"Error: Directory not found: {path}")
            return False