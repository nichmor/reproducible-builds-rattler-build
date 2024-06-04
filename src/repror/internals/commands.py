import glob
import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from subprocess import CompletedProcess


def run_command(command, cwd=None, env=None) -> CompletedProcess:
    """Run a specific command."""
    return subprocess.run(command, cwd=cwd, env=env, check=True)


def calculate_hash(conda_file: Path):
    """Calculate the SHA-256 hash of a conda file."""
    with conda_file.open() as f:
        # Read the entire file
        data = f.read()
        # Calculate the SHA-256 hash
        build_hash = hashlib.sha256(data).hexdigest()

    return build_hash


def find_conda_file(build_folder: Path):
    """Find the conda file in the build folder."""
    conda_file = glob.glob(str(build_folder) + "/**/*.conda", recursive=True)[0]

    return conda_file


def find_all_conda_files(build_folder: Path):
    """Find all conda files in the build folder."""
    return glob.glob(str(build_folder) + "/**/*.conda", recursive=True)


def move_file(conda_file: Path, destination_directory: Path):
    # Make dirs if they don't exist
    os.makedirs(destination_directory, exist_ok=True)
    # Get the base filename
    filename = os.path.basename(conda_file)

    # Move the file to the destination directory
    file_loc = destination_directory / filename
    shutil.move(conda_file, file_loc)

    return file_loc
