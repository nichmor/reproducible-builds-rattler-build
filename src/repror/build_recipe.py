import os
import json
import sys
import conf
from pathlib import Path
import tempfile
from repror.build import (
    Recipe,
    build_local_recipe,
    build_remote_recipes,
)
from repror.rattler_build import setup_rattler_build


def build_recipes(recipes: list[Recipe], tmp_dir, build_dir):
    cloned_prefix_dir = Path(tmp_dir) / "cloned"
    build_info = {}

    for recipe in recipes:
        url = recipe["url"]
        if url == "local":
            build_info.update(build_local_recipe(recipe, build_dir))
        else:
            build_info.update(
                build_remote_recipes(recipe, build_dir, cloned_prefix_dir)
            )

    return build_info


if __name__ == "__main__":
    platform, version = sys.argv[1], sys.argv[2]
    # this should be optional
    # so we could run it locally nice
    recipe_string = sys.argv[3]

    url, branch, path = recipe_string.split("::")

    recipe_obj: Recipe = Recipe(url=url, branch=branch, path=path)

    if platform not in ["ubuntu", "macos", "windows"]:
        print("Invalid platform ", platform)
        sys.exit(1)

    config = conf.load_config()

    build_info = {}

    with tempfile.TemporaryDirectory() as tmp_dir:
        setup_rattler_build(config, Path(tmp_dir))

        build_dir = Path("build_outputs")
        build_dir.mkdir(exist_ok=True)

        build_results = {}

        build_info = build_recipes([recipe_obj], tmp_dir, build_dir)

        os.makedirs("build_info", exist_ok=True)

        # build_id = uuid.uuid4().hex

        with open(
            f"build_info/{platform}_{version}_{recipe_string.replace("/", "_").replace("::", "_").replace(":", "_")}_build_info.json",
            "w",
        ) as f:
            json.dump(build_info, f)
