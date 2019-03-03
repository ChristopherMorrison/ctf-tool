#!/usr/bin/python3

# Validates the directory structure of a given problem set

import os
import sys
import argparse

def validate_ctf_directory(directory):
    valid_directory = True

    for dirname, subdirList, fileList in os.walk(directory, topdown=False):
        if subdirList:
            continue
        if "challenge.zip" not in fileList:
            print(f"challenge.zip missing in {dirname}\n")
            valid_directory = False
        if "value.txt" not in fileList:
            print(f"value.txt missing in {dirname}\n")
            valid_directory = False
        if "message.txt" not in fileList:
            print(f"message.txt missing in {dirname}\n")
            valid_directory = False
        if "flag.txt" not in fileList:
            print(f"flag.txt missing in {dirname}\n")
            valid_directory = False
    #    if len(fileList) is not 4:
    #        print(f"Incorrect number of files in the directory {dirname}\n")
    #        valid_directory = False
    if not valid_directory:
        print(f"Validation attempt failed for {directory}")
        return(1)
    else:
        print(f"Validation attempt passed for {directory}")
        return(0)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    args = parser.parse_args()
    sys.exit(validate_ctf_directory(args.directory))
