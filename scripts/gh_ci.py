import argparse
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

WINDOWS_GH = Path(r"C:\Program Files\GitHub CLI\gh.exe")


def gh_executable() -> str:
    found = shutil.which("gh")
    if found:
        return found
    if WINDOWS_GH.is_file():
        return str(WINDOWS_GH)
    raise RuntimeError("GitHub CLI was not found; install and authenticate it with 'gh auth login'")


def run(arguments: Sequence[str], *, capture: bool = False) -> str | None:
    result = subprocess.run(
        [gh_executable(), *arguments],
        check=True,
        text=True,
        capture_output=capture,
    )
    return result.stdout.strip() if capture else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Operate this project's GitHub Actions through gh")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("workflows", help="List workflows")
    runs = subcommands.add_parser("runs", help="List recent CI runs")
    runs.add_argument("--limit", type=int, default=10)
    dispatch = subcommands.add_parser("dispatch", help="Dispatch the full CI workflow")
    dispatch.add_argument("--ref", default="main")
    watch = subcommands.add_parser("watch", help="Watch a run and return its exit status")
    watch.add_argument("run_id", type=int)
    download = subcommands.add_parser("download", help="Download all run artifacts")
    download.add_argument("run_id", type=int)
    download.add_argument("--directory", default="artifacts/downloaded")
    arguments = parser.parse_args()

    if arguments.command == "workflows":
        run(["workflow", "list"])
    elif arguments.command == "runs":
        run(["run", "list", "--workflow", "ci.yml", "--limit", str(arguments.limit)])
    elif arguments.command == "dispatch":
        run(["workflow", "run", "ci.yml", "--ref", arguments.ref])
        run(["run", "list", "--workflow", "ci.yml", "--limit", "5"])
    elif arguments.command == "watch":
        run(["run", "watch", str(arguments.run_id), "--exit-status"])
    elif arguments.command == "download":
        run(["run", "download", str(arguments.run_id), "--dir", arguments.directory])


if __name__ == "__main__":
    main()
