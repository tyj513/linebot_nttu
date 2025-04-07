import shutil
from git import Repo

source_folder = "/HDD/p76131694/nttu/"

try:
    # Verify the path
    print("Checking if", source_folder, "is a Git repository...")
    repo = Repo(source_folder)
    print("Repository found.")

    # Add files to the index
    repo.git.add(all=True)

    # Commit changes
    repo.index.commit("Upload files from source_folder")

    # Push changes to remote repository
    origin = repo.remote(name="origin")
    origin.push()
    print("Pushed changes to remote repository.")

except git.exc.InvalidGitRepositoryError:
    print("InvalidGitRepositoryError: The specified directory is not a Git repository.")
except Exception as e:
    print("An error occurred:", e)
