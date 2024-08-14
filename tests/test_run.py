"""
Unit test file.
"""

import random
import shutil
import string
import subprocess
import threading
import unittest
from pathlib import Path

from tx.cli import run

TIMEOUT = 60

HERE = Path(__file__).parent
RX_PATH = HERE / "rx"
TX_PATH = HERE / "tx"

# Generate a random 32-character code
RANDOM_CODE = "".join(random.choices(string.digits, k=32))

RX_COMMAND = f"wormhole receive --accept-file {RANDOM_CODE}"


def run_tx(code):
    run(
        file_or_dir="testfile.txt",
        code=code,
        code_length=None,
        wormhole_args=[],
        cwd=TX_PATH,
    )


class RunTester(unittest.TestCase):
    """Main tester class."""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Ensure TX_PATH and RX_PATH exist
        RX_PATH.mkdir(parents=True, exist_ok=True)
        for path in RX_PATH.iterdir():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment."""
        # Remove all files in TX_PATH and RX_PATH

        for item in RX_PATH.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    def test_run(self) -> None:
        """Test command line interface (CLI)."""
        received_file_path = RX_PATH / "testfile.txt"
        self.assertFalse(received_file_path.exists(), "Received file already exists")
        # Create and start the tx thread
        tx_thread = threading.Thread(target=run_tx, args=(RANDOM_CODE,), daemon=True)
        tx_thread.start()

        # Run rx command
        with subprocess.Popen(
            RX_COMMAND,
            cwd=RX_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        ) as rx_proc:
            try:
                # Wait for the rx process to finish with a timeout of TIMEOUT seconds
                _, rx_err = rx_proc.communicate(timeout=TIMEOUT)
            except subprocess.TimeoutExpired:
                rx_proc.kill()
                _, rx_err = rx_proc.communicate()
                self.fail(f"RX process timed out after {TIMEOUT} seconds")

        # Wait for the tx thread to complete
        tx_thread.join(timeout=TIMEOUT)
        if tx_thread.is_alive():
            self.fail(f"TX thread did not complete within {TIMEOUT} seconds")

        # Check if the rx process completed successfully
        self.assertEqual(
            rx_proc.returncode,
            0,
            f"RX process failed with error: {rx_err.decode()}",
        )

        # Check if the received file exists
        received_file_path = RX_PATH / "testfile.txt"
        self.assertTrue(received_file_path.exists(), "Received file does not exist")


if __name__ == "__main__":
    unittest.main()
