#!/usr/bin/python3

# Validates the directory structure of a given problem set

import os
import sys
import argparse

def validate_ctf_directory(directory, verbose=True):
    valid_directory = True

    categories = [folder for folder in os.listdir(directory) if os.path.isdir(f"{directory}/{folder}")]
    # for dirname, subdirList, fileList in os.walk(directory, topdown=False):
    #     if subdirList:
    #         continue

    for category in categories:
        for challenge in os.listdir(f"{directory}/{category}"):
            dirname = f"{directory}/{category}/{challenge}"
            if os.path.isdir(dirname):            
                fileList = os.listdir(dirname)

                # Standard
                if "challenge.zip" not in fileList and verbose:
                    print(f"(optional) challenge.zip missing in {dirname}")
                    #valid_directory = False
                if "value.txt" not in fileList:
                    print(f"value.txt missing in {dirname}")
                    valid_directory = False
                if "message.txt" not in fileList:
                    print(f"message.txt missing in {dirname}")
                    valid_directory = False
                if "flag.txt" not in fileList:
                    print(f"flag.txt missing in {dirname}")
                    valid_directory = False
                
                # Service-req

                # Container-req

                # Machine-req

    if not valid_directory:
        print(f"Validation attempt failed for {directory}")
        return(1)
    else:
        print(f"Validation attempt passed for {directory}")
        return(0)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="+")
    parser.add_argument("-v", "--verbose", default=False, action='store_true')
    args = parser.parse_args()
    sys.exit(1 in [validate_ctf_directory(dir, args.verbose) for dir in args.directory])
