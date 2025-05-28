from PySide6.QtWidgets import QTreeView, QFileSystemModel
from PySide6.QtCore import Signal, QDir

class FileManager(QTreeView):
    file_open_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.currentPath())
        self.setModel(self.model)
        self.setRootIndex(self.model.index(QDir.currentPath()))
        self.doubleClicked.connect(self.on_double_click)
        self.setColumnWidth(0, 300)  # adjust width if too narrow
        self.setHeaderHidden(False)  # show the header with column titles

    def on_double_click(self, index):
        if self.model.isDir(index):
            return
        file_path = self.model.filePath(index)
        self.file_open_requested.emit(file_path)
