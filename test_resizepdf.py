import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pymupdf


SCRIPT = Path(__file__).with_name("resizepdf.py")


class ResizePdfTests(unittest.TestCase):
    def test_compresses_images_and_preserves_text(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "document.pdf"
            target = Path(directory) / "document_resized.pdf"
            samples = random.Random(42).randbytes(600 * 600 * 3)
            image = pymupdf.Pixmap(pymupdf.csRGB, 600, 600, samples, False)
            with pymupdf.open() as document:
                page = document.new_page(width=200, height=200)
                page.insert_text((10, 190), "Testo ricercabile")
                page.insert_image(pymupdf.Rect(0, 0, 144, 144), pixmap=image)
                document.save(source)

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--dpi", "72"],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertLess(target.stat().st_size, source.stat().st_size)
            with pymupdf.open(target) as document:
                self.assertIn("Testo ricercabile", document[0].get_text())
                info = document[0].get_image_info()[0]
                self.assertLessEqual(info["width"], 150)
                self.assertLessEqual(info["height"], 150)

            target.unlink()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--dpi", "150"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with pymupdf.open(target) as document:
                info_150 = document[0].get_image_info()[0]
                self.assertGreater(info_150["width"], info["width"])
                self.assertGreater(info_150["height"], info["height"])

    def test_rejects_existing_output_and_invalid_dpi(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "document.pdf"
            target = Path(directory) / "document_resized.pdf"
            with pymupdf.open() as document:
                document.new_page()
                document.save(source)
            target.write_bytes(b"existing")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source)], capture_output=True, text=True
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), b"existing")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--dpi", "0"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("maggiore di zero", result.stderr)
            self.assertEqual(target.read_bytes(), b"existing")


if __name__ == "__main__":
    unittest.main()
