#!/usr/bin/env python3
import argparse as ap

if __name__ == "__main__":
    parser = ap.ArgumentParser(
        usage = "python %(prog)s [options] [args]",
        description = "argparse example",
        epilog = "This is where you might put example usage",
        formatter_class = ap.RawDescriptionHelpFormatter,
    )

    general_group = parser.add_argument_group("General Options")

    general_group.add_argument(
        "-V", "--version",
        action = "version",
        help = "show program version",
        version = "%(prog)s 0.1",
    )

    parser.parse_args()