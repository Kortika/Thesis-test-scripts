from pathlib import Path


def check_directory_exists(dir_path: Path, dir_type: str):
    if not dir_path.exists():
        print(f"{dir_type} directory doesn't exists: {dir_path}")
        exit(1)
