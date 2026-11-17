import argparse
from pathlib import Path
import sys

import pymupdf


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("il DPI deve essere un numero intero") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("il DPI deve essere maggiore di zero")
    return number


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Comprimi un PDF riducendo la risoluzione delle immagini."
    )
    parser.add_argument("pdf", type=Path, help="percorso del PDF originale")
    parser.add_argument("--dpi", type=positive_int, default=72, help="DPI desiderato (default: 72)")
    args = parser.parse_args()
    output = args.pdf.with_name(f"{args.pdf.stem}_resized.pdf")

    try:
        with pymupdf.open(args.pdf) as document:
            if not document.is_pdf:
                raise ValueError("il file indicato non è un PDF")
            if document.needs_pass:
                raise ValueError("i PDF protetti da password non sono supportati")
            document.rewrite_images(
                dpi_threshold=args.dpi + 1,
                dpi_target=args.dpi,
                quality=75,
            )
            with output.open("xb") as output_file:
                try:
                    document.save(output_file, garbage=4, deflate=True, use_objstms=True)
                except (OSError, RuntimeError, ValueError):
                    output_file.close()
                    output.unlink()
                    raise
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    print(f"PDF creato: {output}")
    print(f"Dimensione: {args.pdf.stat().st_size} -> {output.stat().st_size} byte")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
