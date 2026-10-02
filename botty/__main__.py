"""Entry point for `python -m botty` and `botty` command."""

import sys

from botty.main import main

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(line_buffering=True)

main()
