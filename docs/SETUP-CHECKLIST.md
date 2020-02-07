# SETUP CHECKLIST
a simple checklist for hosting a real ctfd instance with this tool, do these post-zip upload

# Pre-setup items
* [ ] DNS for the CTFd instance
* [ ] SSL for the CTFd instance (optional)
* [ ] IP for the Challenge host, can probably go static and have ACM pay for it

# CTFd config Checklist
## Appearance
1. [ ] CTF name had been set
2. [ ] CTFd is in Teams mode
3. [ ] (optional) Cyber@UC or event logo has been uploaded

## Accounts
1. [ ] Verify emails is enabled
2. [ ] Change default admin account from root:root

## Settings
1. [ ] Challenge Visibility is public
2. [ ] Score Visibility is public
3. [ ] Registration Visibility is public

## Email
1. [ ] CTFd is configured to use the Cyber@UC gmail

## Time
1. [ ] Start time is set to 15 minutes after the CTF presentation will be made or at other arranged time
2. [ ] End time is set to 23 hours after the start time (or when appropriate)
3. [ ] Freeze time is End Time

## Challenges
1. [ ] Make sure the challenges list has been imported successfully (CTFd will basically die if this doesn't happen so it's pretty obvious)

# Challenge host setup
1. [ ] Make sure the challenges are up with `sudo netstat -plant` or `docker ps`
2. [ ] Make sure flags have permissions `-----r---- root:challenge_name`
3. [ ] Make sure challenge user folders have permissions `d---r-x--- root:challenge_name`

# CTF run crew checklist
1. [ ] Verify everyone who is on the run crew has admin access to CTFd and the challenge host
2. [ ] Verify that everyone on the challenge crew knows what they are doing
3. [ ] Verify that everyone on the challenge crew is wearing the krusty crab uniform

# End of game checklist
1. [ ] Make sure the challenge host has been stopped and deleted one hour after the event ends
2. [ ] Make sure the CTFd instance is stopped one day after the event (lets people check their late answers)
3. [ ] Make sure the DNS name (if any) has been redirected properly to cyberatuc.org
