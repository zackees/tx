"""
Unit test file.
"""

import filecmp
import random
import shutil
import string
import subprocess
import unittest
from pathlib import Path

HERE = Path(__file__).parent
RX_PATH = HERE / "rx"
TX_PATH = HERE / "tx"

# Generate a random 32-character code
RANDOM_CODE = "".join(random.choices(string.digits, k=32))

TX_COMMAND = f"tx --code {RANDOM_CODE}"
RX_COMMAND = f"wormhole receive --accept-file {RANDOM_CODE}"


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
        # Create a test file in the tx directory
        test_file_path = "testfile.txt"
        tx_cmd = f"{TX_COMMAND} {test_file_path}"
        # Run tx command
        with subprocess.Popen(
            tx_cmd,
            cwd=TX_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        ) as tx_proc:
            # Run rx command
            with subprocess.Popen(
                RX_COMMAND,
                cwd=RX_PATH,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            ) as rx_proc:
                try:
                    # Wait for both processes to finish with a timeout of 1 second
                    _, tx_err = tx_proc.communicate(timeout=1)
                    _, rx_err = rx_proc.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    tx_proc.kill()
                    rx_proc.kill()
                    _, tx_err = tx_proc.communicate()
                    _, rx_err = rx_proc.communicate()
                    self.fail("Subprocess timed out after 1 second")

        # Check if both processes completed successfully
        self.assertEqual(
            tx_proc.returncode,
            0,
            f"TX process failed with error: {tx_err.decode()}",
        )
        self.assertEqual(
            rx_proc.returncode,
            0,
            f"RX process failed with error: {rx_err.decode()}",
        )

        # Check if the received file exists
        received_file_path = RX_PATH / "testfile.txt"
        self.assertTrue(received_file_path.exists(), "Received file does not exist")

        # Compare the sent and received files
        self.assertTrue(
            filecmp.cmp(test_file_path, received_file_path, shallow=False),
            "Sent and received files do not match",
        )


if __name__ == "__main__":
    unittest.main()
