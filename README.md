# PDF Compression

Install the dependencies with [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv sync
```

Compress a PDF:

```bash
uv run python resizepdf.py file_name.pdf --dpi 72
```

The result is saved in the same folder as `file_name_resized.pdf`.
An existing destination file is not overwritten. The `--dpi` option is
optional and defaults to 72.

The script reduces the resolution of images and recompresses them with lossy
compression, keeping text and vector graphics intact. The DPI is a target
value: the actual resolution may differ because of rounding applied by
PyMuPDF. The resulting file is not necessarily smaller than the original,
especially if it contains few images or is already optimized. Password-protected
PDFs are not supported.
