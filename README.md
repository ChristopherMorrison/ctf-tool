# CTF-TOOL
Finaly! A tool for building modular CTFs with minimum effort.


# Concepts
## Challenges:
| Challenges Type    | Definition |
| ------------------ | ---------- |
| Standard           | Standard challenges present the player with a question and optionally a set of files. The player is expected to input a flag to solve the problem. Files may be provided to the player to download from the CTFd challenge board.
| Service-Required   | Service-required challenges are standard challenges but also require a service to be running that the player can connect to (typically via netcat). This is commonly used for buffer overflow type problems.


## Challenge Packs:
ctf-tool's design revolves around the concept of challenge packs which are formated directories and subdirectories that represent individual challenges. The reasoning of using challenge packs as a building block is that it allows problems to be neatly sorted, reused, and even allows the CTF builder to adjust the difficulty for the audience's proficiecy level by combining different challenge packs into a single build. **The actual content and structure of challenge packs is unfortunately still volatile as ctf-tool is developed into version 1.**


## Flags:
For the sake of simplicity, ctf-tool 1.0 only currently supports a single static flag per problem. CTFd supports multiple flags and regex flags which is a planned feature for ctf-tool's future. Static flag randomization and per-player flags are also planned for the future.


## CTF Host / Challenge Host:
The CTF Host is the machine that the players will be directed to in order to submit flags for points. In the current version, ctf-tool expects the CTF host to be an instance of CTFd, but in future versions, FBCTD support is planned as well.

The Challenge Host is the machine that ctf-tool expects to install services on for players to be able to connect to. **This is the machine that the tool is expected to be run on.**

ctf-tool considers the challenge host and the ctf host to be two seperate machines, although this is not required in any way. Using one machine for both should be perfectly fine. The first time ctf-tool was actually used for a ctf, only one machine was used.


# Installation
## Supported Systems
*Linux:* Currently, only Debian/Ubuntu is considered stable, although other debian-based distros should work. Really any host with all the dependency packages installed should work. 

*Windows:* No offical support currently. Although if you can run a CTFd instance you can use it as the CTF Host

*Mac:* No offical support currently, same as Windows.


## Setup for Debian/Ubuntu machines
1. Clone or download this repo
2. Install `docker-ce` by following the instructions on the docker website
3. Install the dependencies with the `apt` helper script
```
sudo scripts/install_required_packages.sh
```
4. run the tool with the --install flag unless you don't need services for challenges. This will build the CTFd config zip file which you will need to upload to an instance of CTFd


# Tool instructions
## ctf-tool.py
Builds a CTFd config from a problem set and optionally installs the problem set onto the local machine for socat connections. Meant to be a plug and play clone of the capability seen at Battelle/Hack Ohio 2017 CTF whit major extentions.

## src/validate.py
A simple mini-tool for validating that a challenge pack has been correctly made.

# Development Roadmap
## Features
* add the challenge host setup script (default behaviour)
* Add prereq challenges ability
* some kind of more interactive way to setup / generally more user friendly
* FBCTF output format
* checkout some vulnerable vm generators and vulnhub for a self-randomizing event every time


## Challenge packs/integrations
These are some of the challenge packs we hope to add to the public repo, all of these challenges are publicly documented extensively so adding their flags here should not be a huge issue. We do have a private repo of challenges that we create, as to not have the answers floating around.
* OTW challenges
* Various vulnhub challenges
* Google CTF beginners ctf

