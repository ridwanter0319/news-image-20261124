"""Entry program for make.fun news-image-20261124.

Draws 'The World in One Day — Tuesday 24 November 2026' with compose.py
(Pillow) and writes it to /output/entry.png. The grader's stock
python3.13 image has no Pillow, so when PIL is unavailable the program
copies the entry.png shipped in this repository instead — the exact
bytes compose.py produced. Both runs write identical bytes; no network.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    try:
        import compose

        image = compose.render()
        image.save(target)
    except ImportError:
        shutil.copyfile(HERE / "entry.png", target)


if __name__ == "__main__":
    main()
