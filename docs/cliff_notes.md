1. Get the list of challenges (already done with chal_host_setup.py)
2. Vague: connnect to our challenge host machine as root
3. For every challenge:
	a. Make a new user with the challenge name as the user name
	b. Copy the scripts/flags as needed to the new user dir
	c. Add the challenge host script to crontab @reboot setting with script to run and port
	d. set the user dir permissions to owned by root and only readable to that user

