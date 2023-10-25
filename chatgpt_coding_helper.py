from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeView, QTextEdit, QFileDialog, QFileSystemModel, QGroupBox, QScrollArea
)
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
import os



def get_tree_structure(path, ignored_dirs, indent=0):
    """Recursively retrieves the tree structure of the directory."""
    items = os.listdir(path)
    tree = ""
    
    for item in items:
        # Skip ignored directories
        if item in ignored_dirs:
            continue
        
        tree += '    ' * indent + item + '\n'
        item_path = os.path.join(path, item)
        
        if os.path.isdir(item_path):
            tree += get_tree_structure(item_path, ignored_dirs, indent + 1)
            
    return tree


def select_folder():
    directory = QFileDialog.getExistingDirectory(None, "Select a folder:")
    if directory:
        # Set the directory for QFileSystemModel
        file_system_model.setRootPath(directory)
        tree_view.setRootIndex(file_system_model.index(directory))


def summarize_files():
    indexes = tree_view.selectionModel().selectedRows()
    summarized_text = ""

    # Fetch the ignored directories from the UI and parse them
    ignored_dirs = [dir_name.strip() for dir_name in ignored_dirs_edit.text().split(",")]

    # Include the complete tree structure at the beginning
    root_path = file_system_model.filePath(tree_view.rootIndex())
    summarized_text += get_tree_structure(root_path, ignored_dirs) + "\n\n"
    
    for index in indexes:
        path = file_system_model.filePath(index)
        
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                summarized_text += f"{path}\n{content}\n\n"
        else:
            for i in range(file_system_model.rowCount(index)):
                child_index = file_system_model.index(i, 0, index)
                child_path = file_system_model.filePath(child_index)
                if os.path.isfile(child_path):  # Check if it's a file
                    with open(child_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                        summarized_text += f"{child_path}\n{content}\n\n"
    
    # Wrap the summarized text with the start and end texts
    summarized_text = start_text_edit.toPlainText() + "\n\n" + summarized_text + "\n\n" + end_text_edit.toPlainText()

    text_edit.setText(summarized_text)
    text_edit.setText(summarized_text)


def copy_to_clipboard():
    clipboard = QApplication.clipboard()
    clipboard.setText(text_edit.toPlainText())


def update_char_count():
    char_count = len(text_edit.toPlainText())
    char_count_label.setText(f"Character Count: {char_count}")

# Create the application
app = QApplication([])

# Set the application icon
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
app.setWindowIcon(QIcon(icon_path))

# Create the main window
window = QWidget()
window.setWindowTitle("ChatGPT Coding Helper")
window.setToolTip("This tool streamlines the process of working with LLMs like ChatGPT for coding. \n"
                  "You can select a directory, list its files (including subdirectories), \n"
                  "and then select multiple files from this list. Summarizing their contents \n"
                  "into a single view makes it easier to iteratively request changes to scripts. \n"
                  "By providing context and updates, you can send a new request with the necessary \n"
                  "context for the next change, ensuring efficient coding. The start text can be \n"
                  "used for providing context, and the end text can be used for instructions for the \n"
                  "next change.")
layout = QVBoxLayout(window)


# Create collapsible file selection group
file_selection_group = QGroupBox("File Selection")
file_selection_group.setCheckable(True)
file_selection_group.setChecked(True)
file_selection_group.toggled.connect(lambda: scroll_file_selection.setVisible(file_selection_group.isChecked()))

file_selection_layout = QVBoxLayout()

folder_btn = QPushButton("Select Folder")
folder_btn.clicked.connect(select_folder)
file_selection_layout.addWidget(folder_btn)

# Input for ignored directories
ignored_dirs_layout = QHBoxLayout()
ignored_dirs_label = QLabel("Ignored Directories (comma separated):")
ignored_dirs_edit = QLineEdit()
ignored_dirs_layout.addWidget(ignored_dirs_label)
ignored_dirs_layout.addWidget(ignored_dirs_edit)
file_selection_layout.addLayout(ignored_dirs_layout)

# Use QTreeView with QFileSystemModel to display file hierarchy
file_system_model = QFileSystemModel()
file_system_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)
tree_view = QTreeView()
tree_view.setModel(file_system_model)
tree_view.setSelectionMode(QTreeView.MultiSelection)
file_selection_layout.addWidget(tree_view)

file_selection_area = QWidget()
file_selection_area.setLayout(file_selection_layout)
scroll_file_selection = QScrollArea()
scroll_file_selection.setWidgetResizable(True)
scroll_file_selection.setWidget(file_selection_area)

# Create collapsible start text group
start_text_group = QGroupBox("Summary Start Text")
start_text_group.setCheckable(True)
start_text_group.setChecked(True)
start_text_edit = QTextEdit()
start_text_layout = QVBoxLayout()
start_text_layout.addWidget(start_text_edit)
start_text_group.setLayout(start_text_layout)

# Create collapsible end text group
end_text_group = QGroupBox("Summary End Text")
end_text_group.setCheckable(True)
end_text_group.setChecked(True)
end_text_edit = QTextEdit()
end_text_layout = QVBoxLayout()
end_text_layout.addWidget(end_text_edit)
end_text_group.setLayout(end_text_layout)

# Create collapsible summary group
summary_group = QGroupBox("Summary")
summary_group.setCheckable(True)
summary_group.setChecked(True)
summary_group.toggled.connect(lambda: scroll_summary.setVisible(summary_group.isChecked()))

summary_layout = QVBoxLayout()

summarize_btn = QPushButton("Summarize Files")
summarize_btn.clicked.connect(summarize_files)
summary_layout.addWidget(summarize_btn)

text_edit = QTextEdit()
summary_layout.addWidget(text_edit)

summary_area = QWidget()
summary_area.setLayout(summary_layout)
scroll_summary = QScrollArea()
scroll_summary.setWidgetResizable(True)
scroll_summary.setWidget(summary_area)

# Add a button for copying the summarized text to clipboard
copy_btn = QPushButton("Copy to Clipboard")
copy_btn.clicked.connect(copy_to_clipboard)
summary_layout.addWidget(copy_btn)

# Add widgets to main layout
layout.addWidget(file_selection_group)
layout.addWidget(scroll_file_selection)
layout.addWidget(start_text_group)
layout.addWidget(end_text_group)
layout.addWidget(summary_group)
layout.addWidget(scroll_summary)
char_count_label = QLabel("Character Count: 0")
text_edit.textChanged.connect(update_char_count)
summary_layout.addWidget(char_count_label)

# Set the initial state of the collapsible groups
window.resize(1000, 800)  # Set an initial window size
window.show()

app.exec_()
