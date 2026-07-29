from __version__ import (
    __version__,
    __appname__,
)

import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-v", "--version", action="version", version=__version__)
args = parser.parse_args()
