import os
import random
import shutil
import tempfile
import re
from src.util import EmptyConfigFileError


# literally just a token class
class _chal_rep(object):
    def __init__(self):
        return

# eat a txt file
def contents_of(file):
    try:
        return open(file).read().strip()
    except:
        return None

class Challenge(object):
    def __init__(self, abs_directory):
        # Local fs info
        self.directory = abs_directory
        self.challenge_binary = "" # use for challenge.zip?

        # Challenge
        self.id = None
        self.name = os.path.basename(abs_directory)
        self.description = contents_of(os.path.join(abs_directory, 'message.txt')).strip()
        self.max_attempts = int(contents_of(os.path.join(abs_directory, "max-attempts")) if os.path.exists(os.path.join(abs_directory,"max-attempts")) else 0)
        self.value = int(contents_of(os.path.join(abs_directory, 'value.txt')))
        self.category = os.path.basename(os.path.dirname(abs_directory))
        self.type = 'standard'
        self.state = 'visible'
        self.requirements = None
        self.requires_server_path = None
        self.server_zip_path = None
        self.username = None
        self.crontab_path = None
        self.port = random.randint(48620, 49150)
        self.requires_server_string = None
        self.listener_command = None

        # Flag
        self.flag = contents_of(os.path.join(abs_directory,"flag.txt"))

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
            requires_server_args[1] = os.path.join(os.path.abspath(os.path.dirname(self.requires_server_path)),
                                                   requires_server_args[1])
        else:
            requires_server_args[0] = os.path.join(os.path.abspath(os.path.dirname(self.requires_server_path)),
                                                   requires_server_args[0])
        requires_server_string = " ".join(requires_server_args)
        self.requires_server_string = requires_server_string

    def set_listener_command(self):
        self.listener_command = f"python3 /usr/local/bin/challenge-listener.py '{self.requires_server_string}' {self.port}"
