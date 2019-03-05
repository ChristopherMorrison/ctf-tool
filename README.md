# CTF-TOOL
A tool for building modular CTFs with minimum effort.


# Concepts
## Challenges:
| Challenges Type    | Definition |
| ------------------ | ---------- |
| Standard           | Standard challenges present the player with a question and optionally a set of files. The player is expected to input a flag to solve the problem.
| Service-Required   | Service-required challenges are similar to standard challenges but require a service to be running that the player can connect to (typically via netcat).
| Machine-Required   | Machine-required challenges are similar to both standard and service-required problems but instead require a dedicated machine to be presented to the players. This type is planned for future and not currently supported.
| Container-required | Same as Machine-required but use containers instead of machines. Also planned for future and not currently supported.

## Challenge Packs:
ctf-tool's design revolves around the concept of challenge packs which are in essence directories with the subdirectories that represent individual challenges. The reasoning of using challenge packs as a building block is that it allows problems to be neatly sorted, reused, and even allows the CTF builder to adjust the difficulty for the audience's proficiecy level. The actual content and structure of challenge packs is unfortunately still volatile as ctf-tool is developed into version 1.

## Flags:
For the sake of simplicity, ctf-tool only currently supports a single static flag per problem. CTFd supports multiple flags and regex flags which is a planned feature for ctf-tool's future. Additionally, static flag randomization and per-player flags are planned for the future.

## CTF Host / Challenge Host:
The CTF Host is the machine that the players will be directed to in order to submit flags for points. In the current version, ctf-tool expects the CTF host to be an instance of CTFd, but in future versions, FBCTD support is planned.

The Challenge Host is the machine that ctf-tool expects to install services on for players to be able to connect to. This is the machine that the tool is expected to be run on.

ctf-tool considers the challenge host and the ctf host to be two seperate machines, although this is not inforced in any way and using one machine for both should be perfectly fine.

# Supported Systems
*Linux:* Currently, only Ubuntu 18.04 is considered stable, although other debian-based distros should work. Really any host all the dependency packages installed should work. 

*Windows:* No offical support currently

*Mac:* No offical support currently

## Setup for ubuntu 18.04 machines
1. Clone this repo
2. Install docker-ce
3. sudo scripts/install_required_packages.sh
4. run the tool with the --install flag unless you don't need services for challenges

# Tool instructions
## ctf-tool.py
Builds a CTFd config from a problem set and optionally installs the problem set onto the local machine for socat connections. Meant to be a plug and play clone of the capability seen at Battelle/Hack Ohio 2017 CTF wiht major extentions.

# Development Roadmap
## Features
* add the challenge host setup script (default behaviour)
* Add prereq challenges ability
* some kind of more interactive way to setup
* FBCTF output format
* checkout some vulnerable vm generators and vulnhub for a self-randomizing event every time
* Need to support flags that are hardcoded in challenges (different flag value for running server than in distributed zip)

## Challenge packs/integrations
* OTW challenges
* Various vulnhub challenges
* Battelle.org/cyber-challenge - This is a good med/hard/hard pack
* Advent of Code clone?
* Google CTF beginners ctf
* Lock pick challenge?
* Juice Shop

