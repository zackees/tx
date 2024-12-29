TX
==

![image](https://github.com/zackees/tx/assets/6856673/9207453b-8280-4804-b63b-7382b219f37d)

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)

[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)

Easiest way to send files:

*Install*
```bash
pip install wormhole-tx
```

*Run*
```bash
tx myfile.mp4
# Then follow the directions
```

This will generate a `magic-wormhole` command that you can use on the receiving end.

# Background

`magic-wormhole` is even more powerful when properly tuned. `wormhole-tx` gives saner defaults and is more secure with a larger key. The command to run on the receiving end will auto-accept the file and wait for it to begin.

Additionally, the receiving command is generated at the *beginning* instead of the end of the archive building phase. This makes the command quicker to run since you can immediately connect the client to the sender.

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

  * 1.1.0: `--multi` keeps on dumping files to allow broad cast like file download
  * 1.0.9: Now has an api `tx.run` for code integration. Many other fixes.
  * 1.0.8: Update `magic-wormhole` to fix Mac M1 breakage.
  * 1.0.7: Adds missing dependency for colorama.
  * 1.0.6: Varius fixes and force UTF-8 on Windows to prevent crash during file send.
  * 1.0.3: Removes new typing system which doesn't work on python < 3.10
  * 1.0.2: Unknown arguments are passed onto `wormhole send`. Help now displays `wormhole --help`.
  * 1.0.1: Fixes missing `magic-wormhole` dependency.
