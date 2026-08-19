To solve the problem of an autonomous coding agent failing due to an overflowed context window with large repository files, we can implement a solution that dynamically manages the context window size. This solution will include:

1. **File Size Filtering**: Exclude large files from being added to the context window.
2. **Context Window Management**: Maintain a manageable size of the context window by removing older or less relevant files.

Here's a complete Python script that demonstrates this approach:

```python
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
```

### Explanation:
1. **File Size Filtering**: The `is_large_file` function checks if a file is larger than a specified size (1 MB in this case). If a file is large, it is skipped.
2. **Context Window Management**: The `manage_context_window` function ensures that the context window does not exceed the maximum size or number of files. It removes the oldest files first to maintain a manageable size.
3. **Repository Processing**: The `process_repository` function processes the repository by adding files to the context window and managing the context window size.

### Usage:
1. Replace `/path/to/your/repository` with the actual path to your repository.
2. Replace `/path/to/context/window` with the actual path where you want to store the context window files.
3. Run the script to process the repository and manage the context window.

This script should help prevent the context window from overflowing with large repository files, thus avoiding the failure of the autonomous coding agent.
