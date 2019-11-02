#!/usr/bin/env python3
import argparse
import sys

from src import ascii_art
from src.commands import command_dict
from src.tui import log_error


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("command",
                        help="command to run",
                        choices=[cmd for cmd in command_dict if not command_dict[cmd].hidden])
    return parser


def main():
    # Art
    print(ascii_art)
    
    # Parser args
    parser = get_parser()
    args = parser.parse_args(sys.argv[1:2])

    # run command action
    try:
        selected_command = command_dict[args.command] 
        return selected_command().run_command(sys.argv[2:])
    except Exception as e:
        log_error(str(e))  # Nicer display on error
        raise  # Shows traceback


if __name__ == "__main__":
    quit(main())
