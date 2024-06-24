import hashlib
from pathlib import Path

import yaml
from repror.internals import git


def clone_remote_recipe(url: str, rev: str, clone_dir: Path) -> Path:
    repo_dir = clone_dir.joinpath(
        url.replace(".git", "").replace("/", "").replace("https:", "")
    )

    if not repo_dir.exists():
        git.clone_repo(url, repo_dir)

    git.checkout_branch_or_commit(repo_dir, rev)
    return repo_dir


def load_remote_recipe_config(
    url: str, rev: str, path: str, clone_dir: Path
) -> tuple[dict, str]:
    cloned_recipe = clone_remote_recipe(url, rev, clone_dir)

    recipe_path = cloned_recipe / path
    config = load_recipe_config(recipe_path)

    raw_config = recipe_path.read_text(encoding="utf8")

    return config, raw_config


def load_recipe_config(recipe_path: str | Path) -> dict:
    recipe_path = Path(recipe_path) if isinstance(recipe_path, str) else recipe_path
    raw_config = recipe_path.read_text(encoding="utf8")
    return yaml.safe_load(raw_config)


def get_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def list_recipe_files(recipe_path: Path) -> list[Path]:
    return list(recipe_path.rglob("*"))


def recipe_files_hash(recipe_folder: Path) -> str:
    total_hash = hashlib.sha256()
    for file in list_recipe_files(recipe_folder):
        if file.is_file():
            total_hash.update(file.read_bytes())
        else:
            total_hash.update(recipe_files_hash(file).encode())

    return total_hash.hexdigest()


def get_recipe_name(config: dict) -> str:
    if "context" in config:
        if "name" in config["context"]:
            return config["context"]["name"]

    if "package" in config:
        return config["package"]["name"]

    if "recipe" in config:
        return config["recipe"]["name"]

    raise ValueError("Recipe name not found in the configuration file")
