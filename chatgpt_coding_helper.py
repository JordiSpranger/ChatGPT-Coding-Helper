from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeView, QTextEdit, QFileDialog, QFileSystemModel, QGroupBox, QTabWidget
)
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
import os
import json

class CodingHelperTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Create collapsible file selection group
        self.file_selection_group = QGroupBox("File Selection")
        self.file_selection_group.setCheckable(True)
        self.file_selection_group.setChecked(True)
        file_selection_layout = QVBoxLayout()

        self.folder_btn = QPushButton("Select Folder")
        self.folder_btn.clicked.connect(self.select_folder)
        file_selection_layout.addWidget(self.folder_btn)

        # Input for ignored directories
        ignored_dirs_layout = QHBoxLayout()
        ignored_dirs_label = QLabel("Ignored Directories (comma separated):")
        self.ignored_dirs_edit = QLineEdit()
        ignored_dirs_layout.addWidget(ignored_dirs_label)
        ignored_dirs_layout.addWidget(self.ignored_dirs_edit)
        file_selection_layout.addLayout(ignored_dirs_layout)

        # Set up the file system model and tree view
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setSelectionMode(QTreeView.MultiSelection)
        file_selection_layout.addWidget(self.tree_view)

        self.file_selection_group.setLayout(file_selection_layout)
        self.layout.addWidget(self.file_selection_group)

        # Create collapsible start text group
        self.start_text_group = QGroupBox("Summary Start Text")
        self.start_text_group.setCheckable(True)
        self.start_text_group.setChecked(True)
        start_text_layout = QVBoxLayout()
        self.start_text_edit = QTextEdit()
        start_text_layout.addWidget(self.start_text_edit)
        self.start_text_group.setLayout(start_text_layout)
        self.layout.addWidget(self.start_text_group)

        # Create collapsible end text group
        self.end_text_group = QGroupBox("Summary End Text")
        self.end_text_group.setCheckable(True)
        self.end_text_group.setChecked(True)
        end_text_layout = QVBoxLayout()
        self.end_text_edit = QTextEdit()
        end_text_layout.addWidget(self.end_text_edit)
        self.end_text_group.setLayout(end_text_layout)
        self.layout.addWidget(self.end_text_group)

        # Create collapsible summary group
        self.summary_group = QGroupBox("Summary")
        self.summary_group.setCheckable(True)
        self.summary_group.setChecked(True)
        summary_layout = QVBoxLayout()
        self.summarize_btn = QPushButton("Summarize Files")
        self.summarize_btn.clicked.connect(self.summarize_files)
        summary_layout.addWidget(self.summarize_btn)
        self.text_edit = QTextEdit()
        summary_layout.addWidget(self.text_edit)
        self.summary_group.setLayout(summary_layout)
        self.layout.addWidget(self.summary_group)

        # Add a button for copying the summarized text to clipboard
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        summary_layout.addWidget(self.copy_btn)

        # Character count label
        self.char_count_label = QLabel("Character Count: 0")
        self.text_edit.textChanged.connect(self.update_char_count)
        summary_layout.addWidget(self.char_count_label)

    def select_folder(self):
        directory = QFileDialog.getExistingDirectory(None, "Select a folder:")
        if directory:
            self.file_system_model.setRootPath(directory)
            self.tree_view.setRootIndex(self.file_system_model.index(directory))

    def summarize_files(self):
        indexes = self.tree_view.selectionModel().selectedRows()
        summarized_text = ""
        ignored_dirs = [dir_name.strip() for dir_name in self.ignored_dirs_edit.text().split(",")]

        root_path = self.file_system_model.filePath(self.tree_view.rootIndex())
        summarized_text += self.get_tree_structure(root_path, ignored_dirs) + "\n\n"

        for index in indexes:
            path = self.file_system_model.filePath(index)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()
                    summarized_text += f"{path}\n{content}\n\n"
            else:
                for i in range(self.file_system_model.rowCount(index)):
                    child_index = self.file_system_model.index(i, 0, index)
                    child_path = self.file_system_model.filePath(child_index)
                    if os.path.isfile(child_path):
                        with open(child_path, "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                            summarized_text += f"{child_path}\n{content}\n\n"

        summarized_text = self.start_text_edit.toPlainText() + "\n\n" + summarized_text + "\n\n" + self.end_text_edit.toPlainText()
        self.text_edit.setText(summarized_text)

    def get_tree_structure(self, path, ignored_dirs, indent=0):
        items = os.listdir(path)
        tree = ""
        for item in items:
            if item in ignored_dirs:
                continue
            tree += '    ' * indent + item + '\n'
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                tree += self.get_tree_structure(item_path, ignored_dirs, indent + 1)
        return tree

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())

    def update_char_count(self):
        char_count = len(self.text_edit.toPlainText())
        self.char_count_label.setText(f"Character Count: {char_count}")

def create_new_tab():
    global tab_widget
    new_tab = CodingHelperTab()
    tab_widget.addTab(new_tab, f"Session {tab_widget.count() + 1}")

# Application setup
app = QApplication([])

# Set the application icon
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graphics/icon.png')
app.setWindowIcon(QIcon(icon_path))

# Create the main window
main_window = QWidget()
main_window.setWindowTitle("ChatGPT Coding Helper")
main_window.resize(1000, 800)

# Main layout for the window
main_layout = QVBoxLayout(main_window)

# Initialize tab_widget as a global variable
tab_widget = QTabWidget()
main_layout.addWidget(tab_widget)

# Add a button to create new tabs
new_tab_button = QPushButton("New Session")
new_tab_button.clicked.connect(create_new_tab)
main_layout.addWidget(new_tab_button)

# Initialize with one tab
create_new_tab()

main_window.show()
app.exec_()
