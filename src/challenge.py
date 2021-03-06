import os
import random
import shutil
import tempfile
import re
import textwrap
from typing import List

from src.util import EmptyConfigFileError
from src.util import contents_of


# literally just a token class for challenge to abuse
# TODO: there is probably a way around using this
class _chal_rep(object):
    def __init__(self):
        return


class Challenge(object):
    def __init__(self, abs_directory):
        # Local fs info
        self.directory = abs_directory
        self.challenge_binary = "" # use for challenge.zip?

        # Standard Challenge
        self.id = None
        self.name = os.path.basename(abs_directory)
        self.flag = contents_of(os.path.join(abs_directory,"flag.txt"))
        self.description = contents_of(os.path.join(abs_directory, 'message.txt')).strip()
        self.max_attempts = int(contents_of(os.path.join(abs_directory, "max-attempts")) if os.path.exists(os.path.join(abs_directory,"max-attempts")) else 0) # TODO: no demo yet
        self.value = int(contents_of(os.path.join(abs_directory, 'value.txt')))
        self.category = os.path.basename(os.path.dirname(abs_directory))
        self.type = 'standard'
        self.state = 'visible'
        self.requirements = None
        
        # Server Challenge
        self.requires_server_path = None
        self.server_zip_path = None
        self.username = None
        self.crontab_path = None
        self.port = random.randint(48620, 49150)
        self.requires_server_string = None
        self.listener_command = None

        # Files
        self.has_challenge_zip = os.path.exists(os.path.join(abs_directory,"challenge.zip"))

        return

    def __repr__(self):
        # prints the json repr of what ctfd needs, don't add anyhting else becasue it will break ctfd
        return f"'{self.id}','{self.name}','{self.description}','{self.max_attempts}','{self.value}','{self.category}','{self.type}','{self.state}','{self.requirements}'"

    def ctfd_repr(self):
        retVal = _chal_rep()
        retVal.id = self.id
        retVal.name = self.name
        retVal.description = self.description
        retVal.max_attempts = self.max_attempts
        retVal.value = self.value
        retVal.category = self.category
        retVal.type = self.type
        retVal.state = self.state
        retVal.requirements = self.requirements
        return retVal

    def ctfd_flag_repr(self):
        retVal = _chal_rep()
        retVal.id = None                # to be set later
        retVal.challenge_id = self.id   # The associated challenge id
        retVal.type = "static"          # "static" or whatever the value for regular expression is
        retVal.content = self.flag      # the flag string or regex
        retVal.data = None              # ??? maybe something with regex
        return retVal
    
    def copy_zip_file_to_temp(self,tempdir):
        if os.path.exists(f"{self.directory}/challenge.zip"):
            filename = "_".join(self.name.split(" "))
            os.makedirs(os.path.join(tempdir,filename))
            shutil.copy2(
                os.path.join(
                    self.directory,
                    "challenge.zip"
                ),
                os.path.join(
                    tempdir,
                    f"{filename}/{filename}.zip"
                )
            )
        return

    def ctfd_file_list(self):
        retVal = _chal_rep()
        filename = "_".join(self.name.split(" "))
        if self.has_challenge_zip:            
            # Build obj
            retVal.id = None
            retVal.type = "challenge"
            retVal.location = f"{filename}/{filename}.zip"
            retVal.challenge_id = self.id
            retVal.page_id = None
        return retVal

    def set_requires_server_string(self):
        with open(self.requires_server_path, "r") as f:
            requires_server_string = f.readline()

        if requires_server_string == "" or requires_server_string is None:
            raise EmptyConfigFileError
        requires_server_string = re.sub("(\r)*\n", "", requires_server_string)

        requires_server_args = requires_server_string.split(" ")
        if len(requires_server_args) > 1:
            requires_server_args[1] = os.path.join(f"/home/{self.username}", requires_server_args[1])
        else:
            requires_server_args[0] = os.path.join(f"/home/{self.username}", requires_server_args[0])
        requires_server_string = " ".join(requires_server_args)

        self.requires_server_string = requires_server_string

    def set_listener_command(self):
        self.listener_command = f"python3 /usr/local/bin/challenge-listener.py '{self.requires_server_string}' {self.port}"

    def generate_dockerfile(self, out_path):
        dockerfile_template = f"""
                                    FROM "ubuntu"
                                    COPY install_required_packages.sh /root/install_required_packages.sh
                                    COPY server.zip /home/{self.username}/server/server.zip 
                                    COPY requires-server /home/{self.username}/requires-server
                                    COPY challenge-listener.py /usr/local/bin/challenge-listener.py
                                    RUN chmod 755 /usr/local/bin/challenge-listener.py 
                                    RUN apt update
                                    RUN /root/install_required_packages.sh
                                    RUN useradd -M -d /home/{self.username} {self.username}
                                    WORKDIR /home/{self.username}/server
                                    RUN unzip server.zip 
                                    RUN chmod -R 755 $(pwd)
                                    RUN mv * .. 
                                    WORKDIR /home/{self.username}
                                    CMD {self.listener_command}"""

        dockerfile_template = textwrap.dedent(dockerfile_template)
    
        if os.path.split(out_path)[1] != "Dockerfile":
            out_path = os.path.join(out_path, "Dockerfile")

        with open(out_path, "w") as f:
            f.write(dockerfile_template)


def get_challenge_list(directory_list: List[str]) -> List[Challenge]:
    """ Builds a list of challenge objects from all challenge bundles in args.directory """
    challenges = []
    challenge_names = []
    for challenge_pack in directory_list:
        problem_dir = os.path.join(os.getcwd(), challenge_pack)
        category_dirs = [dir for dir in os.listdir(problem_dir) if os.path.isdir(os.path.join(problem_dir, dir)) and not dir.startswith('.')]
        for category in category_dirs:
            for challenge in os.listdir(os.path.join(problem_dir, category)):
                if os.path.isdir(os.path.join(problem_dir, category, challenge)):
                    chal = Challenge(os.path.join(problem_dir, category, challenge))
                    if chal.name in challenge_names:
                        print(f"Two or more challenges named {chal.name}")
                        # TODO: v2 This is because of the zip file names for challenge.zip not being hash based. This may also be a limitation of CTFd, need to investigate
                        quit(1)
                    challenges.append(chal)
                    challenge_names.append(chal.name)
    for i in range(len(challenges)):
        challenges[i].id = i + 1
    return challenges


def make_challenges(directory_list: List[str], no_make_clean=False):
    """For every challenge in the given packs that have Makefiles, run `make clean; make`"""
    for challenge_pack in directory_list:
        problem_dir = os.path.join(os.getcwd(), challenge_pack)
        category_dirs = [dir for dir in os.listdir(problem_dir) if os.path.isdir(os.path.join(problem_dir, dir)) and not dir.startswith('.')]
        for category in category_dirs:
            for challenge in os.listdir(os.path.join(problem_dir, category)):
                if os.path.isdir(f'{problem_dir}/{category}/{challenge}') and os.path.exists(f'{problem_dir}/{category}/{challenge}/Makefile'):
                    if not no_make_clean:
                        os.system(f'make clean -s -C "{problem_dir}/{category}/{challenge}"')
                    os.system(f'make -s -C "{problem_dir}/{category}/{challenge}"')
    return


def make_clean_challenges(directory_list: List[str]):
    """For every challenge in the given packs that have Makefiles, run `make clean`"""
    for challenge_pack in directory_list:
        problem_dir = os.path.join(os.getcwd(), challenge_pack)
        category_dirs = [dir for dir in os.listdir(problem_dir) if os.path.isdir(os.path.join(problem_dir, dir)) and not dir.startswith('.')]
        for category in category_dirs:
            for challenge in os.listdir(os.path.join(problem_dir, category)):
                if os.path.isdir(f'{problem_dir}/{category}/{challenge}') and os.path.exists(f'{problem_dir}/{category}/{challenge}/Makefile'):
                    os.system(f'make clean -s -C "{problem_dir}/{category}/{challenge}"')
    return


def get_flag_list(challenges: List[Challenge]):
    """Builds a list of objects from challenges that dump nicely into json for CTFd """
    challenge_flag_list = []
    challenge_flag_list = [chal.ctfd_flag_repr() for chal in challenges]
    challenge_flag_list = [flag for flag in challenge_flag_list if flag is not None]
    for i in range(len(challenge_flag_list)):
        challenge_flag_list[i].id = i + 1
    return challenge_flag_list

