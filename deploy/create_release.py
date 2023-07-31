import os
import shutil

def read_gitignore(gitignore_path):
    ignored_patterns = []
    with open(gitignore_path, "r") as gitignore_file:
        for line in gitignore_file:
            line = line.strip()
            if line and not line.startswith("#"):
                ignored_patterns.append(line)
    return ignored_patterns

def is_git_ignored(path, gitignore_patterns):
    for pattern in gitignore_patterns:
        if path == pattern or path.startswith(pattern + os.path.sep):
            return True
    return False

def copy_contents_to_parent_directory():
    # Get the current working directory
    current_directory = os.getcwd()

    # Move up one directory level
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))

    # Create a new directory inside the parent directory to copy contents into
    new_directory_name = "copy_of_" + os.path.basename(current_directory)
    new_directory_path = os.path.join(parent_directory, new_directory_name)
    os.makedirs(new_directory_path, exist_ok=True)

    # Get a list of all files and directories in the current directory
    contents = os.listdir(current_directory)

    # Get a list of patterns to ignore based on .gitignore
    gitignore_path = os.path.join(current_directory, ".gitignore")
    ignored_patterns = read_gitignore(gitignore_path)

    # Copy each item to the new directory
    for item in contents:
        item_path = os.path.join(current_directory, item)
        new_item_path = os.path.join(new_directory_path, item)
        if not is_git_ignored(item_path, ignored_patterns):
            if os.path.isdir(item_path):
                shutil.copytree(item_path, new_item_path, dirs_exist_ok=True)
            else:
                shutil.copy2(item_path, new_item_path)

    print("Contents copied successfully to:", new_directory_path)

if __name__ == "__main__":
    copy_contents_to_parent_directory()
