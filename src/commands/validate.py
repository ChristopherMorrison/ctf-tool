import argparse
import os
import sys
import argparse
import zipfile


# "Common" code
from src.commands import BaseCommand
from src.tui import log_error, log_success, log_warn, log_normal
from src.challenge import make_challenges, make_clean_challenges


class Validatecmd(BaseCommand):
    name = 'validate'
    description = ('Validate sets of problems')

    def __init__(self):
        super().__init__()

    def subparser(self):
        return None

    def __call__(self, argline):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument("directory", nargs="+")
        parser.add_argument("-v", "--verbose",
                            default=False,
                            action='store_true',
                            help='Show optional warnings')
        parser.add_argument('--no-make',
                            default=False,
                            action='store_true',
                            help="Don't run `make clean; make` for challenges with Makefiles")
        args = parser.parse_args(argline)

        # make clean; make
        if not args.no_make:
            make_challenges(args.directory)

        # validate
        check_list = [validate_ctf_directory(dir, args.verbose) for dir in args.directory]

        # make clean
        if not args.no_make:
            make_clean_challenges(args.directory)

        sys.exit(any(check_list))
    

def validate_ctf_directory(directory, verbose=False):
    """Validates the directory structure of a given problem set"""
    valid_directory = True

    categories = [folder for folder in os.listdir(directory) if os.path.isdir(f"{directory}/{folder}")]

    for category in categories:
        if category.startswith('.'):
            continue
        for challenge in os.listdir(f"{directory}/{category}"):
            dirname = f"{directory}/{category}/{challenge}"
            if os.path.isdir(dirname):            
                fileList = os.listdir(dirname)

                # Standard
                if "challenge.zip" not in fileList and verbose:
                    print(f"{dirname}: (optional) challenge.zip missing")

                if "value.txt" not in fileList:
                    print(f"{dirname}: value.txt missing")
                    valid_directory = False

                if "message.txt" not in fileList:
                    print(f"{dirname}: message.txt missing")
                    valid_directory = False

                if "flag.txt" not in fileList:
                    print(f"{dirname}: flag.txt missing")
                    valid_directory = False
                
                # Service-req
                if "requires-server" in fileList:
                    if "server.zip" not in fileList:
                        print(f"{dirname}: server.zip missing when requires-server specified")
                        valid_directory = False
                    elif open(f"{dirname}/requires-server").read().strip() not in zipfile.ZipFile(f"{dirname}/server.zip").namelist():
                        print(f"{dirname}: requires-server lists a binary not in server.zip")
                        valid_directory = False
                # TODO: v2 Container-req

                # TODO: v2Machine-req

    if not valid_directory:
        log_error(f"{directory} is NOT a valid challenge pack")
        return(1)
    else:
        log_success(f"{directory} is a valid challenge pack")
        return(0)
