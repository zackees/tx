![image](https://github.com/zackees/tx/assets/6856673/9207453b-8280-4804-b63b-7382b219f37d)

# tx

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)

[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)

Easiest way to send files:

Install
```bash
pip install wormhole-tx
```

```bash
tx myfile.mp4
# Then follow the directions
```

This will generate a `magic-wormhole` command that you can use on the receiving end.

# Install

`git clone ...`
`. ./install`
`. ./activate.sh`

To develop software, run `. ./activate.sh`

# Windows

This environment requires you to use `git-bash`.

# Linting

Run `./lint.sh` to find linting errors using `pylint`, `flake8` and `mypy`.

# Versions

  * 1.0.1: Fixes missing `magic-wormhole` dependency.
