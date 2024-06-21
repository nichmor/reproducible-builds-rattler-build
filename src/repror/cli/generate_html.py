from collections import defaultdict
from typing import Optional

from pydantic import BaseModel
from rich import print

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from repror.internals.db import BuildState, get_rebuild_data
from repror.internals.git import github_api


class StatisticData(BaseModel):
    build_state: BuildState
    rebuild_state: Optional[BuildState] = None
    recipe_name: str
    equal_hash: Optional[bool] = None
    reason: Optional[str] = None
    time: str
    actions_url: Optional[str] = None

    @property
    def is_success(self):
        return (
            self.build_state == BuildState.SUCCESS
            and self.rebuild_state
            and self.rebuild_state == BuildState.SUCCESS
            and self.equal_hash
        )


def rerender_html(update_remote: bool = False):
    env = Environment(
        loader=FileSystemLoader(searchpath=Path(__file__).parent / "templates")
    )

    builds = get_rebuild_data()

    by_platform = defaultdict(list)

    for build in builds:
        if build.state == BuildState.FAIL:
            by_platform[build.platform_name].append(
                StatisticData(
                    build_state=build.state,
                    recipe_name=build.recipe_name,
                    time=str(build.timestamp),
                    reason=build.reason,
                    actions_url=build.actions_url,
                )
            )
            continue
        rebuild = build.rebuilds[-1] if build.rebuilds else None
        by_platform[build.platform_name].append(
            StatisticData(
                recipe_name=build.recipe_name,
                build_state=build.state,
                rebuild_state=rebuild.state if rebuild else None,
                reason=rebuild.reason if rebuild else None,
                time=str(rebuild.timestamp) if rebuild else str(build.timestamp),
                equal_hash=build.build_hash == rebuild.rebuild_hash
                if rebuild
                else None,
                actions_url=build.actions_url,
            )
        )

    template = env.get_template("index.html")

    html_content = template.render(by_platform=by_platform)
    # Save the table to README.md
    index_html_path = Path("docs/index.html")
    index_html_path.parent.mkdir(exist_ok=True)
    index_html_path.write_text(html_content)

    if update_remote:
        # Update the README.md using GitHub API
        print(":running: Updating index.html with new data")
        github_api.update_obj(
            html_content,
            "docs/index.html",
            "Update statistics",
        )
