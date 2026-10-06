import functools
import logging
import re
import sys
import subprocess
import tomllib
import tempfile
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("tmt_plans.utils")

CI_CONFIG_FILES = [
    "fedora-ci.yaml",
    "fedora-ci.yml",
    "fedora-ci.toml",
]


@functools.cache
def get_env_file() -> Path | None:
    env_file = os.environ.get("TMT_PLAN_ENVIRONMENT_FILE")
    return Path(env_file) if env_file else None


def save_env(name: str, value: Any) -> None:
    if not (env_file := get_env_file()):
        return
    with env_file.open("a") as f:
        f.write(f"{name}={value!s}\n")


@functools.cache
def get_workdir() -> Path:
    """
    Get or generate a temporary workdir used across tests.

    We do not expect any reboot in these tests, so we can use a ``/tmp`` path.
    Avoid using paths like ``TMT_PLAN_DATA`` because we do not want these to be
    synced back to testing-farm artifact storage.
    """
    workdir = os.environ.get("WORKDIR")
    if not workdir:
        workdir = tempfile.mkdtemp(prefix="tmt-test-workdir-")
        save_env("WORKDIR", workdir)
    logger.info(f"Temporary workdir: {workdir}")
    return Path(workdir)


def get_config(dist_git_path: Path, section: str) -> dict[str, Any] | None:
    from ruamel.yaml import YAML

    for ci_file_name in CI_CONFIG_FILES:
        ci_file = dist_git_path / ci_file_name
        if ci_file.exists():
            break
    else:
        return None

    logger.info(f"Found config file {ci_file_name}")
    with ci_file.open("rb") as f:
        if ci_file.suffix == ".toml":
            full_config = tomllib.load(f)
        elif ci_file.suffix in [".yaml", ".yml"]:
            full_config = YAML().load(f)
        else:
            raise AssertionError("Trying to load a file not listed in CI_CONFIG_FILES")

    if not (tools := full_config.get("tools")):
        logger.info("No `tools` section found")
        return None
    if not (config := tools.get(section)):
        logger.info(f"No `tools.{section}` section found")
        return None
    return config


def get_dist_git(koji_task_id: str) -> Path:
    workdir = get_workdir()
    result = subprocess.run(
        [
            "koji",
            "taskinfo",
            "-v",
            koji_task_id,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    task_info = result.stdout
    task_error = result.stderr
    logger.info(f"Task info output:\n{task_info}\nTask error:\n{task_error}")
    source_match_obj = re.search(r"Source:\s*(.*)", task_info)
    if source_match_obj is None:
        logger.error(
            "Could not find 'Source:' in koji taskinfo output. Maybe a 500 error? Please retry."
        )
        sys.exit(1)
    source = source_match_obj.group(1)
    source_match = re.search(r"git\+(?P<url>.*)#(?P<ref>.*)", source)
    repo_url = source_match.group("url")
    repo_ref = source_match.group("ref")

    # Clone the dist-git used in the build
    dist_git_path = workdir / "dist-git"
    subprocess.run(
        ["git", "clone", repo_url, dist_git_path],
        check=True,
    )
    subprocess.run(
        ["git", "checkout", "-d", repo_ref],
        cwd=dist_git_path,
        check=True,
    )
    return dist_git_path


def get_koji_build(koji_task_id: str) -> None:
    # TODO: Migrate these to tmt artifacts when possible
    workdir = get_workdir()
    subprocess.run(
        ["koji", "download-task", koji_task_id],
        cwd=workdir,
        check=True,
    )
    save_env("RPM_FILES", f"{workdir}/*.rpm")
