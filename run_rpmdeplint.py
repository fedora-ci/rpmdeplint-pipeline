#!/usr/bin/python3
# /// script
# dependencies = [
#   "fedora-distro-aliases",
# ]
# ///

import argparse
import logging
import os
import subprocess
from pathlib import Path

from fedora_distro_aliases import bodhi_active_releases

logging.basicConfig(level="INFO")
logger = logging.getLogger(Path(__file__).name)

KOJI_BASE = r"https://kojipkgs.fedoraproject.org/repos/{distro_build}/latest/{arch}"
"""
Koji build base repo used for the rmdepcheck base repo.
"""
FEDORA_ID_PREFIXES = {
    "FEDORA",
    "FEDORA-EPEL",
    "FEDORA-EPEL-NEXT",  # Currently only used by epel9-next
    # Skipping FEDORA-CONTAINER and FEDORA-FLATPAK
}
"""
Supported ``ID Prefix`` of the releases in https://bodhi.fedoraproject.org/releases.
"""


def get_distro_build(dist_git_branch: str) -> str:
    releases = [
        release
        for release in bodhi_active_releases()
        if release["id_prefix"] in FEDORA_ID_PREFIXES
        and release["branch"] == dist_git_branch
    ]

    if not releases or len(releases) > 1:
        logger.error(f"Could not identify release for branch '{dist_git_branch}'")
        exit(1)
    # Seems like we can use the dist_tag to construct the koji build tag for all cases
    return f"{releases[0]['dist_tag']}-build"


def main(args: argparse.Namespace) -> None:
    repo_path: Path = args.workdir / "repo" / args.arch
    subprocess.run(
        [
            "rpmdeplint",
            "--debug",
            f"check-{args.check}",
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
    parser = argparse.ArgumentParser(description="Actually run rmdepcheck")
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
        logger.error("Rmdepcheck failed!")
        raise SystemExit(1)
    except Exception as exc:
        logger.error("Unexpected rmdepcheck failure", exc_info=exc)
        raise SystemExit(2)
