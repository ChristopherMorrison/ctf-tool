import subprocess
import socket
import os
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("program", type=str)
parser.add_argument("port")
args = parser.parse_args()

while 1:
    os.system(f"socat TCP4-LISTEN:{args.port},tcpwrap=script,reuseaddr,fork EXEC:'{args.program}',stderr,pty")

