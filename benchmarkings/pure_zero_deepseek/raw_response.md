 To address the issue of an autonomous coding agent failing when its context window overflows with large repository files, we can implement a script that dynamically loads and processes the repository files in chunks. This approach will help manage the memory usage and prevent the context window from overflowing.

Here's a Python script that demonstrates this approach using the `git` library to handle Git repositories:

```python
import os
import git
from git import Repo

def process_file(file_path):
    # Placeholder function to process each file
    with open(file_path, 'r') as file:
        content = file.read()
        # Process the content as needed
        print(f"Processed file: {file_path}")

def process_repository(repo_path, chunk_size=100):
    repo = Repo(repo_path)
    commits = list(repo.iter_commits('main'))  # Assuming 'main' is the default branch

    for commit in commits:
        for file_change in commit.stats.files.keys():
            file_path = os.path.join(repo_path, file_change)
            if os.path.isfile(file_path):
                process_file(file_path)

    # Handle large repository by processing in chunks
    for branch in repo.branches:
        branch.checkout()
        commit_count = len(list(repo.iter_commits(branch)))
        for start in range(0, commit_count, chunk_size):
            chunk_commits = list(repo.iter_commits(branch))[start:start + chunk_size]
            for commit in chunk_commits:
                for file_change in commit.stats.files.keys():
                    file_path = os.path.join(repo_path, file_change)
                    if os.path.isfile(file_path):
                        process_file(file_path)

# Example usage
repo_path = '/path/to/your/git/repository'
process_repository(repo_path)
```

### Explanation:
1. **Repository Initialization**: The script initializes a Git repository using the `git` library.
2. **Iterate through Commits**: It iterates through the commits in the repository.
3. **File Processing**: For each file changed in a commit, it processes the file.
4. **Chunk Processing**: For large repositories, it processes commits in chunks to manage memory usage.

### Usage:
- Replace `'/path/to/your/git/repository'` with the path to your Git repository.
- The `process_file` function is a placeholder for any processing logic you need to implement.

This script ensures that the repository is processed without overwhelming the system's memory by breaking the task into manageable chunks.
