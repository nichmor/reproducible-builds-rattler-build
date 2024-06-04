import json
import os
from pathlib import Path
import platform
from typing import Optional

from repror.internals.build import BuildInfo, Recipe, rebuild_package


def rebuild_packages(
    build_infos: dict[str, Optional[BuildInfo]],
    rebuild_dir: Path,
    platform: str,
):
    rebuild_infos: dict[str, Optional[BuildInfo]] = {}

    for recipe_name, info in build_infos.items():
        if not info:
            rebuild_infos[recipe_name] = None
            continue

        rebuild_directory = Path(rebuild_dir) / f"{recipe_name}_rebuild"

        output_dir = rebuild_directory / "output"

        rebuild_info = rebuild_package(info["conda_loc"], output_dir, platform)

        rebuild_infos[recipe_name] = rebuild_info

    return rebuild_infos


def rebuild_recipe(recipes: list[Recipe], tmp_dir: Path):
    platform_name, platform_version = platform.system().lower(), platform.release()

    Path(f"ci_artifacts/{platform_name}/build").mkdir(exist_ok=True, parents=True)
    Path(f"ci_artifacts/{platform_name}/rebuild").mkdir(exist_ok=True, parents=True)

    for recipe in recipes:
        with open(
            f"build_info/{platform_name}_{platform_version}_{recipe.build_id}_build_info.json",
            "r",
        ) as f:
            previous_build_info = json.load(f)

        rebuild_info = rebuild_packages(previous_build_info, tmp_dir, platform_name)

        os.makedirs(f"build_info/{platform_name}", exist_ok=True)

        with open(
            f"build_info/{platform_name}/{recipe.build_id}_platform_{platform_name}_{platform_version}_rebuild_info.json",
            "w",
        ) as f:
            json.dump(rebuild_info, f)

        with open(
            f"build_info/{platform_name}/{recipe.build_id}_platform_{platform_name}_{platform_version}_build_info.json",
            "w",
        ) as f:
            json.dump(previous_build_info, f)