#!/usr/bin/python3
# /// script
# dependencies = [
#   "koji",
# ]
# ///

import argparse
import logging
import os
import subprocess
from pathlib import Path

import koji

logging.basicConfig(level="INFO")
logger = logging.getLogger(Path(__file__).name)

KOJI_BASE = r"https://kojipkgs.fedoraproject.org/repos/{distro_build}/latest/{arch}"
"""
Koji build base repo used for the rpmdeplint base repo.
"""


def get_distro_build(dist_git_branch: str) -> str:
    config = koji.read_config("koji")
    koji_session = koji.ClientSession(config["server"])
    build_target = koji_session.getBuildTarget(dist_git_branch)
    if not build_target:
        logger.error("Could not find the build target for '%s'", dist_git_branch)
        raise SystemExit(1)
    return build_target["build_tag_name"]


def main(args: argparse.Namespace) -> None:
    repo_path: Path = args.workdir / "repo" / args.arch
    subprocess.run(
        [
            "rpmdeplint",
            "--debug",
            f"check-{args.check}",
            "--allconflicts",
            f"--arch={args.arch}",
            # Base repo
            "--repo=koji-base,{base_repo}".format(
                base_repo=KOJI_BASE.format(
                    distro_build=get_distro_build(args.dist_git_branch),
                    arch=args.arch,
                ),
            ),
            # RPMs to be checked
            *repo_path.glob("*.rpm"),
        ],
        check=True,
    )
    logger.info("All is good!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Actually run rpmdeplint")
    parser.add_argument("dist_git_branch")
    parser.add_argument("--arch", default="x86_64")
    parser.add_argument(
        "--workdir",
        type=Path,
        default=os.environ.get("TMT_PLAN_DATA", "."),
    )
    parser.add_argument(
        "--check",
        required=True,
        choices=["sat", "repoclosure", "conflicts", "upgrade"],
    )

    args = parser.parse_args()

    try:
        main(args)
    except (subprocess.CalledProcessError, SystemExit):
        logger.error("rpmdeplint failed!")
        raise SystemExit(1)
    except Exception as exc:
        logger.error("Unexpected rpmdeplint failure", exc_info=exc)
        raise SystemExit(2)
