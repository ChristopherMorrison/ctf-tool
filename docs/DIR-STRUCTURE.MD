# Directory Structure
```
<ctf_problem_set>/
	<category>/
		<problem_name>/
			flag.txt      - the challenge's flag
			message.txt   - the message to show on ctfd for the problem
			value.txt     - the point value of the challenge
			challenge.zip - zip file for users to download -- TODO: rename to the problem name
			server.zip    - zip file that contains all of the relevant files for running a problem as a nc server. A copy of the binary and flag should be in here.
			solution.txt  - (unimp) details on how to solve the challenge
			hint_<x>.txt  - (unimp) Hint file where x is the order the hints should be given
			requires-server - a file that denotes that the challenges requires being run on the challenge host. Contains the command you wish to run under the server. E.g. "pwn1"
			max-attempts  - (optional) a single number that describes how many attempts users are allowed per. 0 = inf
			<anthing else>- tbd
			?             - Challenge host setup script?
			?		      - CTF init script (compiling and the like)
```

