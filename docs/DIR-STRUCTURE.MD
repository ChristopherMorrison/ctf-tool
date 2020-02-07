# Directory Structure
```
<ctf_problem_set>/
    <category>/
        <problem_name>/
            Makefile        - Makefile for the challenge, ctf-tool will try `make clean; make` before validating any challenges by default.

            flag.txt        - the challenge's flag

            message.txt     - the message to show on ctfd for the problem

            value.txt       - the point value of the challenge

            challenge.zip   - (optional) zip file for users to download, is renamed to <problem name>.zip when added so users can track files easier

            server.zip      - (optional) zip file that contains all of the relevant files for running a problem as a nc server. A copy of the binary and flag should be in here.

            requires-server - (optional) a file that denotes that the challenges requires being run on the challenge host. Contains the command you wish to run under the server. This must be present for server.zip to be used. E.g. "pwn1"

            max-attempts    - (optional) a single number that describes how many attempts users are allowed per. 0 = inf

            solution.txt    - (unimp) details on how to solve the challenge

            hint_<x>.txt    - (unimp) Hint file where x is the order the hints should be given

            ?               - (future) Challenge host setup script?
```

