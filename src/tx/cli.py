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
from typing import IO, Optional

from colorama import just_fix_windows_console

KEY_LENGTH = 32

just_fix_windows_console()


def gen_code(key_length: int) -> str:
    """Returns a random number string of the given length."""
    # only numbers
    return "".join([str(secrets.randbelow(10)) for _ in range(key_length)])


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_help(self, file: Optional[IO[str]] = None):
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
        default=None,
        help="The code length to generate",
    )
    parser.add_argument("--multi", action="store_true", help="Send multiple files")
    parser.add_argument("--code", type=str, default=None, help="The code to use")
    args, unknown = parser.parse_known_args()
    return args, unknown


def gen_wormhole_receive_command(code: str) -> str:
    return f"wormhole recieve --accept-file {code}"


def run(
    file_or_dir: str,
    cwd: Optional[str] = None,
    code: Optional[str] = None,
    code_length: Optional[int] = None,
    wormhole_args: Optional[list[str]] = None,
    multi_file: bool = False,
) -> int:
    cwd = cwd or os.getcwd()
    code = code or None
    wormhole_args = wormhole_args or []
    if not os.path.exists(os.path.join(cwd or "", file_or_dir)):
        print(f"File or directory {file_or_dir} does not exist.")
        return 1

    if code is not None and code_length is not None:
        raise ValueError(
            "Cannot specify both --code and --code-length. Either specify --code or --code-length."
        )
    if code_length is None:
        code_length = KEY_LENGTH

    code = code or gen_code(code_length)
    recieve_cmd = gen_wormhole_receive_command(code)
    cmd_list = ["wormhole", "send", "--code", code, file_or_dir] + wormhole_args

    cmd = subprocess.list2cmdline(cmd_list)

    if sys.platform == "win32":
        # On windows, we need to use chcp 65501 to support UTF-8 or else
        # we get an error when sending files with non-ascii characters
        cmd_list = ["chcp", "65001", "&&"] + cmd_list

    while True:

        print(f'\nSending "{file_or_dir}"...')
        print("On the other computer, run the following command:\n")
        print("    " + recieve_cmd)
        print("")

        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
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
        rtn_code = proc.wait()
        if multi_file:
            continue
        return rtn_code


def main() -> int:
    try:
        args, unknown = parse_args()
        print("$$$$$$$$$$$$$$$$$$$$$$")
        print(args, unknown)
        if "--appid" in unknown:
            warnings.warn("The --appid option is not supported. Use --code instead.")
            return 1
        return run(
            file_or_dir=args.file_or_dir,
            cwd=os.getcwd(),
            code=args.code,
            code_length=args.code_length,
            wormhole_args=unknown,
            multi_file=args.multi,
        )
    except KeyboardInterrupt:
        return 1


if __name__ == "__main__":
    sys.exit(main())
