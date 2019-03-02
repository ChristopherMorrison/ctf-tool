# CTF
```
      _    __ _              _ 
  ___| |_ / _| |_ ___   ___ | |
 / __| __| |_| __/ _ \ / _ \| |
| (__| |_|  _| || (_) | (_) | |
 \___|\__|_|  \__\___/ \___/|_|
 ```

A tool for building modular CTFs with minimum effort.

# TODO: features
* add the challenge host setup script (default behaviour)
* add the ctfd challenge loader script (--install option)
* Add prereq challenges ability
* some kind of more interactive way to setup, especiialy with multiple challenge packs
* Add more challenges (see below)
* FBCTF output format
* checkout some vulnerable vm generators and vulnhub for a self-randomizing event every time
* Need to support flags that are hardcoded in challenges (different flag value for running server than in distributed zip)

# TODO: CTF packs/integrations
* OTW challenges
* Various vulnhub challenges
* Battelle.org/cyber-challenge - This is a good med/hard/hard pack
* Advent of Code clone?
* Google CTF beginners ctf
* Lock pick challenge?
* Juice Shop

# Setup for ubuntu 18.04 machines
1. Clone this repo
2. Install docker-ce
3. sudo scripts/install_required_packages.sh
4. run the tool with the --install flag unless you don't need services for challenges

# Tool instructions
## setup.py
Builds a CTFd config from a problem set and optionally installs the problem set onto the local machine for socat connections. Meant to be a plug and play clone of the capability seen at Battelle/Hack Ohio 2017 CTF.

```
usage: setup.py [-h] [--force] [--install] directory [directory ...]

positional arguments:
  directory   Directories of challenge packs to load

optional arguments:
  -h, --help  show this help message and exit
  --force     ignore directory structure errors
  --install   use the local machine as the challenge host
```


usage: ctf-tool.py [-h] [--force] [--install] [--address ADDRESS]
                   basezip directory [directory ...]

positional arguments:
  basezip            Zip file to pull ctfd metadata from, use a fresh CTFd
                     instance export if you need one
  directory          Directories of challenge packs to load

optional arguments:
  -h, --help         show this help message and exit
  --force            ignore challenge pack validation errors
  --install          use the local machine as the challenge host
  --address ADDRESS  Server address to list in CTFd for participants to
                     connect to
```