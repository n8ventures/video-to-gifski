from __version__ import (
    __version__, 
    __appname__, 
)

import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-E", "--Egg",action='store_true', help = "Egg, mi amor")
parser.add_argument('-v', '--version', action='version', version = __version__)
parser.add_argument('-D', '--debug', action='store_true', help=f'Debug mode. use cmd \' {__appname__}.exe | MORE\'. But, you already knew that, don\'t cha?')
parser.add_argument('-ct', '--checkthreads', action='store_true', help='Checks threads. (Will not work without [-D])')

args = parser.parse_args()