import argparse
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / ".runtime" / "practice-software-testing"
APP_REPOSITORY = "https://github.com/testsmith-io/practice-software-testing.git"
APP_REVISION = "ae7caecb811dd8952c09d997e69be7cb946ecd44"
COMPOSE_FILE = APP_DIR / "docker-compose.prod.yml"
WINDOWS_DOCKER = Path(r"C:\Program Files\Docker\Docker\resources\bin\docker.exe")


def executable(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    if name == "docker" and WINDOWS_DOCKER.is_file():
        return str(WINDOWS_DOCKER)
    raise RuntimeError(f"{name!r} was not found in PATH")


def run(command: Sequence[str], *, cwd: Path | None = None) -> None:
    environment = os.environ.copy()
    environment.update(
        {
            "SPRINT": "sprint5",
            "DISABLE_LOGGING": "false",
            "COMPOSE_PROJECT_NAME": "toolshop-portfolio",
        }
    )
    subprocess.run(command, cwd=cwd, env=environment, check=True)


def ensure_application() -> None:
    git = executable("git")
    if not (APP_DIR / ".git").exists():
        APP_DIR.parent.mkdir(parents=True, exist_ok=True)
        run([git, "clone", "--no-checkout", "--filter=blob:none", APP_REPOSITORY, str(APP_DIR)])
    run([git, "fetch", "--depth", "1", "origin", APP_REVISION], cwd=APP_DIR)
    run([git, "checkout", "--detach", "FETCH_HEAD"], cwd=APP_DIR)


def compose(*arguments: str) -> None:
    run(
        [
            executable("docker"),
            "compose",
            "-f",
            str(COMPOSE_FILE),
            "-f",
            str(ROOT / "compose.app.override.yml"),
            *arguments,
        ],
        cwd=APP_DIR,
    )


def endpoint_is_ready(url: str) -> bool:
    try:
        with urlopen(url, timeout=5) as response:
            return int(response.status) == 200
    except OSError:
        return False


def wait_until_ready(
    endpoints: tuple[str, ...] = ("http://localhost:4200", "http://localhost:8091/status"),
    timeout_seconds: int = 300,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    pending = set(endpoints)
    while pending and time.monotonic() < deadline:
        for url in tuple(pending):
            if endpoint_is_ready(url):
                print(f"READY: {url}")
                pending.remove(url)
        if pending:
            time.sleep(2)
    if pending:
        raise RuntimeError(f"Application endpoints are not ready: {sorted(pending)}")


def migrate_database() -> None:
    compose("exec", "-T", "laravel-api", "php", "artisan", "migrate:fresh", "--seed")
    compose(
        "exec", "-T", "--user", "root", "laravel-api", "chown", "-R", "www-data:www-data", "storage"
    )
    wait_until_ready(("http://localhost:8091/products",))


def start() -> None:
    compose("up", "--pull", "missing", "-d")
    wait_until_ready()
    if not endpoint_is_ready("http://localhost:8091/products"):
        migrate_database()


def reset() -> None:
    compose("down", "--volumes", "--remove-orphans")
    compose("up", "--pull", "missing", "-d")
    wait_until_ready()
    migrate_database()


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the pinned upstream Toolshop application")
    parser.add_argument("command", choices=("start", "stop", "reset", "status", "logs", "wait"))
    arguments = parser.parse_args()

    if arguments.command in {"start", "reset", "stop", "status", "logs"}:
        ensure_application()
    if arguments.command == "start":
        start()
    elif arguments.command == "reset":
        reset()
    elif arguments.command == "stop":
        compose("down", "--remove-orphans")
    elif arguments.command == "status":
        compose("ps")
    elif arguments.command == "logs":
        compose("logs", "--tail", "200")
    elif arguments.command == "wait":
        wait_until_ready()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
