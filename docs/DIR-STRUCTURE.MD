# Directory Structure
```
<ctf_problem_set>/
	<category>/
		<problem_name>/
			flag.txt      - the challenge's flag
			message.txt   - the message to show on ctfd for the problem
			value.txt     - the point value of the challenge
			challenge.zip - zip file for users to download -- TODO: rename to the problem name
			solution.txt  - (unimp) details on how to solve the challenge
			hint_<x>.txt  - (unimp) Hint file where x is the order the hints should be given
			requires-server - an empty file that denotes that the challenges requires being run on the challenge host
			max-attempts  - (optional) a single number that describes how many attempts users are allowed per. 0 = inf
			<anthing else>- tbd
			?             - Challenge host setup script?
			?		      - CTF init script (compiling and the like)
```

