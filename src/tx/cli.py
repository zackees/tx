# pylint: disable=consider-using-with

"""
A wrapper around magic-wormhole send to more easily send a file
"""

import argparse
import os
import secrets
import subprocess
import sys
import warnings
from typing import IO

KEY_LENGTH = 32


def gen_code(key_length: int) -> str:
    """Returns a random number string of the given length."""
    # only numbers
    return "".join([str(secrets.randbelow(10)) for _ in range(key_length)])


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_help(self, file: IO[str] | None = None):
        """Prints the help message."""
        msg = self.format_help()
        print(msg)
        stdout = subprocess.run(
            ["wormhole", "--help"], capture_output=True, text=True, check=False
        ).stdout

        print(
            "\n\n"
            + "###########################################################\n"
            + '## Any unknown options will be passed to "wormhole send" ##\n'
            + "###########################################################\n\n"
            + stdout
        )


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = ArgumentParser(
        description="Sends a file using magic-wormhole",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file_or_dir", help="The file or directory to send")
    parser.add_argument(
        "--code-length",
        type=int,
        default=KEY_LENGTH,
        help="The code length to generate",
    )
    parser.add_argument("--code", type=str, default=None, help="The code to use")
    args, unknown = parser.parse_known_args()
    if args.code is not None and args.code_length is not None:
        parser.error(
            "Cannot specify both --code and --code-length. Either specify --code or --code-length."
        )
    return args, unknown


def gen_wormhole_receive_command(code: str) -> str:
    return f"wormhole recieve --accept-file {code}"


def main() -> int:
    try:
        args, unknown = parse_args()
        if "--appid" in unknown:
            warnings.warn("The --appid option is not supported. Use --code instead.")
            return 1
        file_or_dir = args.file_or_dir
        if not os.path.exists(file_or_dir):
            print(f"File or directory {file_or_dir} does not exist.")
            return 1
        code = args.code or gen_code(args.code_length)
        recieve_cmd = gen_wormhole_receive_command(code)
        cmd_list = ["wormhole", "send", file_or_dir, "--code", code] + unknown
        print(f'\nSending "{file_or_dir}"...')
        print("On the other computer, run the following command:\n")
        print("    " + recieve_cmd)
        print("")
        proc = subprocess.Popen(
            cmd_list,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert proc.stdout is not None
        assert proc.stderr is None
        # stream out stdout line by line
        for line in iter(proc.stdout.readline, ""):
            if "Sending" in line and "kB file" in line:
                continue
            if line == "\n":
                continue
            if "Wormhole code is" in line:
                continue
            if "On the other computer" in line:
                continue
            if "wormhole receive" in line:
                continue
            print(line, end="")
        proc.stdout.close()
        rtn = proc.wait()
        return rtn
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
