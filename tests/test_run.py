"""
Unit test file.
"""

import filecmp
import os
import random
import string
import subprocess
import tempfile
import unittest

# Generate a random 32-character code
RANDOM_CODE = "".join(random.choices(string.digits, k=32))

TX_COMMAND = f"tx --code {RANDOM_CODE}"
RX_COMMAND = f"wormhole receive --accept-file {RANDOM_CODE}"


class RunTester(unittest.TestCase):
    """Main tester class."""

    def test_run(self) -> None:
        """Test command line interface (CLI)."""
        # Create temporary directories
        with tempfile.TemporaryDirectory() as tx_dir, tempfile.TemporaryDirectory() as rx_dir:
            # Create a test file in the tx directory
            test_file_path = os.path.join(tx_dir, "test_file.txt")
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write("This is a test file for tx-rx.")

            # Run tx command
            with subprocess.Popen(
                TX_COMMAND.split() + [test_file_path],
                cwd=tx_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as tx_proc:
                # Run rx command
                with subprocess.Popen(
                    RX_COMMAND.split(),
                    cwd=rx_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
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
            received_file_path = os.path.join(rx_dir, "test_file.txt")
            self.assertTrue(
                os.path.exists(received_file_path), "Received file does not exist"
            )

            # Compare the sent and received files
            self.assertTrue(
                filecmp.cmp(test_file_path, received_file_path, shallow=False),
                "Sent and received files do not match",
            )


if __name__ == "__main__":
    unittest.main()
