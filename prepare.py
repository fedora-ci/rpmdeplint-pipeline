#!/usr/bin/python3
# /// script
# ///

import argparse
import logging
import os
import subprocess
from pathlib import Path

logging.basicConfig(level="INFO")
logger = logging.getLogger(Path(__file__).name)


def koji_task(args: argparse.Namespace, repo_path: Path) -> None:
    logger.info(f"""
    Preparing environment for:
    Koji task: {args.koji_task_id}
    Arch: {args.arch}
    """)

    logger.info("Downloading artifacts from Koji")
    subprocess.run(
        [
            "koji",
            "download-task",
            args.koji_task_id,
            "--arch=noarch",
            f"--arch={args.arch}",
        ],
        cwd=repo_path,
        check=True,
    )

    logger.info(f"Creating the repo: {repo_path}")
    subprocess.run(
        [
            "createrepo",
            f"{repo_path}",
        ],
        check=True,
    )


def bodhi_update(args: argparse.Namespace, repo_path: Path) -> None:
    logger.info(f"""
    Preparing environment for:
    Bodhi update: {args.bodhi_update_id}
    Arch: {args.arch}
    """)

    logger.info("Downloading artifacts from Bodhi")
    subprocess.run(
        [
            "bodhi",
            "updates",
            "download",
            # we don't need signed packages for now?
            "--no-gpg",
            f"--updateid={args.bodhi_update_id}",
            f"--arch={args.arch}",
        ],
        cwd=repo_path,
        check=True,
    )

    # bodhi updates download does not fail on failed downloads.
    # for now we just manually check that there are at least a rpm present
    rpms = list(repo_path.glob("*.rpm"))
    if not rpms:
        logger.error("No rpms were downloaded? Something bad is happening!")
        raise SystemExit(1)

    logger.info(f"Creating the repo: {repo_path}")
    subprocess.run(
        [
            "createrepo",
            f"{repo_path}",
        ],
        check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arch", default="x86_64")
    parser.add_argument(
        "--workdir",
        type=Path,
        default=os.environ.get("TMT_PLAN_DATA", "."),
    )

    actions = parser.add_subparsers(required=True, dest="action")

    koji_parser = actions.add_parser("koji-task")
    koji_parser.add_argument("koji_task_id")

    bodhi_parser = actions.add_parser("bodhi-update")
    bodhi_parser.add_argument("bodhi_update_id")

    args = parser.parse_args()

    repo_path: Path = args.workdir / "repo" / args.arch
    repo_path.mkdir(exist_ok=True, parents=True)

    try:
        match args.action:
            case "koji-task":
                koji_task(args, repo_path)
            case "bodhi-update":
                bodhi_update(args, repo_path)
            case _:
                raise NotImplementedError
    except SystemExit:
        raise 
    except subprocess.CalledProcessError:
        logger.error("Prepare failed")
        raise SystemExit(1)
    except Exception as exc:
        logger.error("Unexpected prepare failure", exc_info=exc)
        raise SystemExit(2)
