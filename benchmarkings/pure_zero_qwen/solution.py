import os
import shutil
from collections import deque

# Define the maximum size of the context window in bytes
MAX_CONTEXT_SIZE = 10 * 1024 * 1024  # 10 MB

# Define the maximum number of files to keep in the context window
MAX_FILES = 100

# Define the path to the repository
REPO_PATH = '/path/to/your/repository'

# Define the path to the context window
CONTEXT_WINDOW_PATH = '/path/to/context/window'

def is_large_file(file_path, max_size=1 * 1024 * 1024):  # 1 MB
    """Check if the file is larger than the specified size."""
    return os.path.getsize(file_path) > max_size

def add_file_to_context_window(file_path):
    """Add a file to the context window."""
    if is_large_file(file_path):
        print(f"Skipping large file: {file_path}")
        return
    
    # Move the file to the context window directory
    shutil.move(file_path, CONTEXT_WINDOW_PATH)
    print(f"Added file to context window: {file_path}")

def manage_context_window():
    """Manage the context window to ensure it does not overflow."""
    # Get a list of files in the context window directory
    files_in_context = [f for f in os.listdir(CONTEXT_WINDOW_PATH) if os.path.isfile(os.path.join(CONTEXT_WINDOW_PATH, f))]
    
    # Sort files by their last modified time (oldest first)
    files_in_context.sort(key=lambda x: os.path.getmtime(os.path.join(CONTEXT_WINDOW_PATH, x)))
    
    # Calculate the total size of the files in the context window
    total_size = sum(os.path.getsize(os.path.join(CONTEXT_WINDOW_PATH, f)) for f in files_in_context)
    
    # Remove files until the context window size is within the limit
    while total_size > MAX_CONTEXT_SIZE or len(files_in_context) > MAX_FILES:
        oldest_file = files_in_context.pop(0)
        file_path = os.path.join(CONTEXT_WINDOW_PATH, oldest_file)
        os.remove(file_path)
        total_size -= os.path.getsize(file_path)
        print(f"Removed file from context window: {file_path}")

def process_repository():
    """Process the repository and manage the context window."""
    # Clear the context window directory
    for file_name in os.listdir(CONTEXT_WINDOW_PATH):
        file_path = os.path.join(CONTEXT_WINDOW_PATH, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    # Add files from the repository to the context window
    for root, _, files in os.walk(REPO_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            add_file_to_context_window(file_path)
    
    # Manage the context window
    manage_context_window()

if __name__ == "__main__":
    process_repository()
