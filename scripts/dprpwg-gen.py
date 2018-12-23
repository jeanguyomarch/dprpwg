#! /usr/bin/env python3
#
# This script generates a dprpwg_config.h file from dprpwg_config.stubs.h by
# using pseudo-random numbers. The numbers are generated accourding to the
# python PEP506 Note. As such, they SHOULD be suitable for cryptographic use.


import argparse
import ctypes
import secrets
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve()
DEFAULT_CONFIG = THIS_DIR.parent.parent / "src" / "dprpwg_config.stub.h"

class Help:
    TEMPLATE = """Path to the dprpwg_config.sub.h file to be used as a template
to generate a suitable dprpwg_config.h file"""
    OUTPUT = "Path to the output header to generate"

def getopts(argv):
    parser = argparse.ArgumentParser(description='DPRPWG config.h generator')
    parser.add_argument("--template", "-t", metavar='CONFIG.h',
                        default=DEFAULT_CONFIG, help=Help.TEMPLATE)
    parser.add_argument("--output", "-o", metavar='OUTPUT.h',
                        help=Help.OUTPUT, required=True)
    return parser.parse_args(argv[1:])

def main(argv):
    args = getopts(argv)

    # Try not to overwrite an existing file
    if Path(args.output).is_file():
        print(f"*** File {args.output} already exists", file=sys.stderr)
        sys.exit(1)

    # Here is the list of all the #define values we shall substitute
    variables = ("PW_MUL", "PW_SEEK_MUL", "PW_INV_MUL",
                 "DOM_MUL", "DOM_SEEK_MUL", "DOM_INV_MUL",
                 "YR_MUL", "YR_SEEK_MUL", "YR_INV_MUL")

    # The values to substitute are 'unsigned int'. So, determine the count of
    # bits that can be used in the generation of the random values.
    # We assume 8 bits per byte.
    bits = ctypes.sizeof(ctypes.c_uint * 8)

    # Make a substitution table that to each variable associates a random
    # number (as a string)
    replace_table = {x: str(secrets.randbits(bits)) for x in variables}

    def _find_variable(text_line):
        """Lambda: if one the variables described in the scope above is
        contained in 'text_line', we will return the value it shall be replaced
        by.
        """
        for variable in variables:
            if variable in text_line:
                return replace_table[variable]

    text = ""

    # Go through each line of the file. If a line contains the variable, we
    # replace "<YOUR_NUMBER>" by the random number associated with the variable
    with open(args.template, "r") as filep:
        for line in filep:
            var = _find_variable(line)
            if var is not None:
                line = line.replace("<YOUR_NUMBER>", var)
            text += line

    # Finally, write the config.h header to the filesystem. Shall be be in the
    # specified path or in the stdout otherwise.
    with open(args.output, "w") as filep:
        filep.write(text)
    # Mark the file as read-only for the user only
    Path(args.output).chmod(0o400)

if __name__ == "__main__":
    main(sys.argv)
