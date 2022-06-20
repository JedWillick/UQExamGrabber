import argparse
import base64
import os
import sys
from io import StringIO
from pathlib import Path
from typing import Callable

import dotenv


class Env:
    _USERNAME = "UQ_USERNAME"
    _PASSWORD = "UQ_PASSWORD"
    _PATH = Path(__file__).parent / ".env"

    def __init__(self, username=None, password=None, timeout=5, headless=True) -> None:
        if not self._PATH.exists():
            Env._PATH.touch()

        with Env._PATH.open("rb") as f:
            data = base64.b64decode(f.read()).decode()

        stream = StringIO(data)
        dotenv.load_dotenv(stream=stream)

        self.username = os.getenv(self._USERNAME, username)
        self.password = os.getenv(self._PASSWORD, password)
        if not self.username or not self.password:
            print(
                "Either provide the -u and -p flags. "
                "Or see 'uqtools env --help' to set the environment variables"
            )
            sys.exit(1)
        self.timeout = timeout
        self.headless = headless

    @staticmethod
    def setup_args(sub: argparse._SubParsersAction) -> None:
        desc = "Configure variables in the .env file. No args to view current values"
        env = sub.add_parser("env", description=desc, help=desc)

        env.add_argument(
            "-u",
            "--username",
            help="Set UQ username",
        )
        env.add_argument(
            "-p",
            "--password",
            help="Set UQ password",
        )

        env.add_argument(
            "-r",
            "--remove",
            action="store_true",
            help="Remove .env file",
        )
        env.add_argument(
            "-f",
            "--file-path",
            action="store_true",
            help="Print the path to the .env file",
        )

    @staticmethod
    def file_cipher(func: Callable[[bytes], bytes]):
        with Env._PATH.open("rb") as f:
            data = func(f.read())
        with Env._PATH.open("wb") as f:
            f.write(data)

    @staticmethod
    def remove_env() -> None:
        Env._PATH.unlink(missing_ok=True)

    @staticmethod
    def config_env(args: argparse.Namespace) -> None:
        if args.remove:
            Env.remove_env()
            return
        if args.file_path:
            print(Env._PATH)
            return
        Env._PATH.touch()
        if len(sys.argv) == 2:
            text = Env._PATH.read_bytes()
            print(f"Try '{Path(sys.argv[0]).stem} env --help'") if not text else print(
                base64.b64decode(text).decode()
            )
            return

        Env.file_cipher(base64.b64decode)

        if args.username:
            dotenv.set_key(Env._PATH, Env._USERNAME, args.username)
        if args.password:
            dotenv.set_key(Env._PATH, Env._PASSWORD, args.password)

        Env.file_cipher(base64.b64encode)
