# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`wormhole-tx` (package name) / `tx` (command name) is a user-friendly wrapper around `magic-wormhole` for secure file transfers. It simplifies the wormhole experience by providing saner defaults, larger security keys (32 digits vs default), and immediate receiver command generation (before archive building phase).

**Key Innovation**: The receiving command is generated at the beginning instead of after the archive phase, allowing immediate client connection to sender.

## Development Setup

### Installation
```bash
. ./install       # Runs install script (platform-specific)
. ./activate.sh   # Activates virtual environment
```

The `install` script handles platform-specific setup (macOS/Linux/Windows). On Windows, use git-bash.

### Environment
- Python 3.10+ required (specified in pyproject.toml:9)
- Virtual environment managed via `venv/`
- Activation required: `. ./activate.sh` sets `IN_ACTIVATED_ENV=1`

## Common Commands

### Testing
```bash
./test                                    # Run all tests via unittest
python -m unittest discover -s tests -p "*test*.py"  # Direct unittest
tox                                       # Run full test suite with linting
```

### Linting
```bash
./lint                                    # Run all linters (ruff, black, isort, flake8, mypy)
ruff check --fix src tests                # Ruff only
black src tests                           # Black formatter
mypy src tests                            # Type checking
```

### Running Locally
```bash
tx myfile.txt                             # Send a file
tx myfile.txt --code 12345678901234567890123456789012  # Use specific code
tx myfile.txt --multi                     # Multi-file broadcast mode
```

### Building/Distribution
```bash
./upload_package.sh                       # Upload to PyPI
```

## Architecture

### Entry Point
- Command-line entry: `tx.cli:main` (defined in pyproject.toml:45)
- Programmatic API: `tx.cli.run()` function (added in v1.0.9)

### Core Flow (src/tx/cli.py)

1. **Argument Parsing** (cli.py:75-96)
   - Uses custom `ArgumentParser` class that extends help to show wormhole options
   - Parses known args into `Args` dataclass (cli.py:55-73)
   - Unknown arguments pass through to wormhole via `parse_known_args()`

2. **Code Generation** (cli.py:24-27)
   - `gen_code()`: Creates random 32-digit numeric code (vs wormhole's shorter default)
   - Key length configurable via `--code-length` or explicit `--code` override

3. **Command Execution** (cli.py:103-177 - `run()` function)
   - Generates receive command immediately: `wormhole receive --accept-file {code}`
   - Displays receive command to user before transfer begins
   - Filters wormhole stdout to suppress redundant information
   - **Windows-specific**: Uses `chcp 65001` for UTF-8 support (cli.py:131-134)
   - **Multi-file mode**: Infinite loop for broadcast-style transfers (cli.py:175-176)

4. **Output Filtering** (cli.py:161-170)
   - Suppresses: file size messages, code display, redundant receive commands
   - Preserves: progress info and important status messages

### Key Functions

- `run()` (cli.py:103): Main execution function - can be imported for programmatic use
  - Parameters: `file_or_dir`, `cwd`, `code`, `code_length`, `wormhole_args`, `multi_file`
  - Returns: exit code (0 = success)

- `gen_wormhole_receive_command()` (cli.py:99): Formats receive command string
  - **Bug**: Typo "recieve" vs "receive" in function name

### Test Architecture (tests/test_run.py)

Integration test using threading:
1. Spawns TX in background thread
2. Runs RX in subprocess with timeout
3. Verifies file transfer completion
4. Uses random 32-digit code for test isolation

## Configuration Files

### pyproject.toml
- Package name: `wormhole-tx` (PyPI)
- Command name: `tx` (entry point)
- Version: 1.1.5 (update line 18 for releases)
- Dependencies: `magic-wormhole>=0.18.0`, `colorama>=0.4.6`

### Linting Configuration
- **Ruff**: line-length 200 (pyproject.toml:21)
- **Flake8**: Ignores E501, E203, W503 (tox.ini:11)
- **Pylint**: Disabled missing-function-docstring, missing-module-docstring (pyproject.toml:32-35)
- **MyPy**: Ignores missing imports (pyproject.toml:40-42)
- **isort**: Black profile (pyproject.toml:37-38)

### tox.ini
Runs full CI pipeline:
- ruff → flake8 → pylint → mypy → pytest
- Parallel pytest via `-n auto` flag

## Code Style Notes

- Modern Python: Uses `|` union syntax (cli.py:58) requiring Python 3.10+
- Type hints: Dataclasses with post-init validation (cli.py:62-72)
- Argument handling: Dataclass pattern replaced argparse.Namespace (per git history)

## Platform Considerations

### Windows
- Requires git-bash environment
- UTF-8 encoding forced via `chcp 65001` (cli.py:131-134)
- Console fixes via `colorama.just_fix_windows_console()` (cli.py:21)

### Cross-Platform
- Virtual environment activation handled by `activate.sh`
- Install script detects OS and uses appropriate Python/package manager

## Known Issues

- Typo: `gen_wormhole_receive_command()` contains "recieve" instead of "receive" (cli.py:100)
- Validation warning: `--appid` explicitly not supported (cli.py:184-186)
