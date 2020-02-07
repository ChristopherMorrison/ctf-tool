# CTF-TOOL
Finally! A tool for building modular CTFs with minimum effort.


# Concepts
## Challenge Types:
| Challenges Type   | Definition |
| ------------------| ---------- |
| Standard          | Standard challenges present the player with a question and optionally a set of files. The player is expected to derive a flag by solving the problem. Files may be provided to the player to download from the CTFd challenge board.
| Service           | Service challenges are standard challenges but also require a service to be running that the player can connect to (typically via netcat/TCP socket). This is commonly used for buffer overflow type problems. The flag is typically given to the player after 'correct' interaction with the remote service


## Challenge Packs:
ctf-tool's design revolves around the concept of challenge packs which are formated directories and subdirectories that represent individual challenges. The reasoning of using challenge packs as a building block is that it allows problems to be neatly sorted, reused, and allows the CTF builder to adjust the difficulty for the audience's proficiecy level by combining different challenge packs into a single build. 

The actual content and structure of challenge packs for ctf-tool is detailed in [DIR-STRUCTURE.md](docs/DIR-STRUCTURE.MD). The current version uses a lot of text files that is planned to be replaced/augmented with a single ini configuration file at a later date.


## Flags:
For the sake of simplicity, ctf-tool 1.0 only currently supports a single static flag per problem. Flags should look something like `ctf{flag}` where `ctf` is a slug for your event and `flag` is your challenge's specific flag.

After Makefile support is finalized, another future change is planned to allow the configuration of flag slugs at build time as long as it is supported by the challenge's Makefile.

CTFd supports multiple flags and regex flags which is a planned feature for ctf-tool's future. Static flag randomization and per-player flags are also planned for the future.


## CTF Host / Challenge Host Machines:
The CTF Host is the machine that the players will be directed to in order to submit flags for points. In the current version, ctf-tool expects the CTF host to be an instance of CTFd, in future versions FBCTD support is planned as well. We have had a large amount of success using the CTFd docker image.

The Challenge Host is the machine that ctf-tool expects to install services on for players to be able to connect to. **This is the machine that CTF-TOOL is run on.** After doing an install, there is no way to uninstall the problems. This means that the Challenge Host should be a non-critical machine can be thrown away in the event a ctf-tool build fails or when the event is over.

ctf-tool considers the challenge host and the ctf host to be two seperate machines, although this is not required in any way. Using one machine for both should be perfectly fine. The first time ctf-tool was actually used for a ctf, only one machine was used.


# Installation
## Supported Systems
*Linux:* Currently, only Debian/Ubuntu is considered stable, although other debian-based distros should work. Really any host with all the dependency packages installed should work. 

*Windows:* No offical support currently. Although if you can run a CTFd instance you can use it as the CTF Host

*Mac:* No offical support currently, same as Windows.


## Setup for Debian/Ubuntu machines
1. Clone this repo
2. Install `docker-ce` by following the instructions on the docker website
3. Install the dependencies with the `apt` helper script
```
sudo scripts/install_required_packages.sh
```
4. Run the tool with the --install flag unless you don't need services for challenges. This will build the CTFd config zip file which you will need to upload to an instance of CTFd


# Tool instructions
## ./ctf-tool.py build
Builds a CTFd config from a problem set and optionally installs the problem set onto the local machine for TCP connections.

Meant to be a plug and play clone of the capability seen at Battelle/Hack Ohio 2017 CTF with major extentions.

The default CTFd config will have the admin user **root** with password **root** after the new zip is uploaded to an existing instance. This can be changed with `--basezip`

Arguments:

    directory
        Directories of challenge packs to load. Example challenge packs are included in the challenges/ directory. Two OverTheWire.org games are included as well as the development example pack.

    --basezip BASEZIP
        Base config zip to use for CTFd. Default one is in the resources directory. This can be made by configuring a CTFd instance without adding any challenges and exporting the configuration. The provided zip has admin root with password root.

    --force
        Unsafe option. Ignores validation errors when checking challenge packs before build. Don't use this unless you're developing ctf-tool.

    --address ADDRESS
        Address of the challenge host for players to use. This will be automatically appended to the challenge description along with whatever port the tool randomly assigns to the service. ex. ctf.cyberatuc.org

    --name NAME
        Name to prepend to the output zip file. Useful for organizing. Build timestamp will also be included in the filename.

    --install-cron
        Install any service challenges on the current machine and register them as cron jobs. Not recommended.

    --install-service
        Install any service challenges on the current machine and register them as systemd services. Better than cron.

    --install-docker
        Shove any service challenges into docker containers and host them on the local machine. Best option.

    --no-make
        Don't run `make clean; make` on challenges with Makefiles when building.

    --no-make-clean
        Don't run `make clean` but still use make on challenges with Makefiles.

## ./ctf-tool.py validate
A simple mini-tool for validating that a challenge pack has been correctly made.

Arguments:

    directory
        Directories of challenge packs to load. Example challenge packs are included in the challenges/ directory. Two OverTheWire.org games are included as well as the development example pack.

    --verbose
        Show optional warnings. Warnings are just things that would make the challenge easier for players.

    --no-make
        Don't run `make clean; make` for challenges with Makefiles. Default behavior is to run `make clean; make` and then validate.


# Development Roadmap
## Features
* add the challenge host setup script (default behaviour)
* Add prereq challenges ability
* some kind of more interactive way to setup / generally more user friendly
* FBCTF output format
* checkout some vulnerable vm generators and vulnhub for a self-randomizing event every time
* Need to support flags that are hardcoded in challenges (different flag value for running server than in distributed zip)
* Improve Docker interface
* Distribute as docker container
* Scalable difficulty settings


## Challenge packs/integrations
These are some of the challenge packs we hope to add to the public repo, all of these challenges are publicly documented extensively so adding their flags here should not be a huge issue. We do have a private repo of challenges that we create, as to not have the answers floating around.
* OTW challenges
* Various vulnhub challenges
* Google CTF beginners ctf
* Battelle.org/cyber-challenge - This is a good med/hard/hard pack
* Advent of Code clone?
* Google CTF beginners ctf
* Lock pick challenge?
* Juice Shop
