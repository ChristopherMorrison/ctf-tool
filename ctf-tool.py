#!/usr/bin/python3
import os
import string
import argparse
import json
import re
import shutil
import uuid
import zipfile
import time
import tempfile

from src.validate import validate_ctf_directory
from src.challenge import Challenge

class EmptyConfigFileError(Exception):
    pass

def validate_challenge_bundles(args):
    """ Validates all specified directories in args.directories """
    for challenge_pack in args.directory:
        problem_dir = os.path.join(os.getcwd(), challenge_pack)
        if validate_ctf_directory(problem_dir) != 0 and not args.force == True:
            quit(1)

def get_challenge_list(args):
    """ Builds a list of challenge objects from all challenge bundles in args.directory """
    challenges = []
    challenge_names = []
    for challenge_pack in args.directory:
        problem_dir = os.path.join(os.getcwd(), challenge_pack)
        category_dirs = [dir for dir in os.listdir(problem_dir) if os.path.isdir(os.path.join(problem_dir,dir))]
        for category in category_dirs:
            for challenge in os.listdir(os.path.join(problem_dir, category)):
                if os.path.isdir(os.path.join(problem_dir, category,challenge)):
                    chal = Challenge(os.path.join(problem_dir, category, challenge))
                    if chal.name in challenge_names:
                        print(f"Two or more challenges named {chal.name}") # This is because of the zip file names for challenge.zip not being hash based. This may also be a limitation of CTFd #TODO 
                        quit(1)
                    challenges.append(chal)
                    challenge_names.append(chal.name)
    for i in range(len(challenges)):
        challenges[i].id = i+1
    return challenges

def get_flag_list(challenges):
    """ Builds a list of objects from challenges that dumbs nicely into json for CTFd """
    challenge_flag_list = []
    challenge_flag_list = [chal.ctfd_flag_repr() for chal in challenges]
    challenge_flag_list = [flag for flag in challenge_flag_list if not flag == None]
    for i in range(len(challenge_flag_list)):
        challenge_flag_list[i].id = i+1
    return challenge_flag_list

def make_output_folder():
    """ Builds a temporary output folder to copy challenge data into before zip"""
    tempdirname = os.path.join("output", time.strftime("%Y.%m.%d-%H:%M:%S"))
    tempuploaddir = os.path.join(tempdirname, "uploads")
    tempdirname = os.path.join(tempdirname, "db")
    os.makedirs(tempdirname)
    os.makedirs(tempuploaddir)
    return tempdirname, tempuploaddir

def output_csv(challenges):
    """ Writes the csv format of the ctfd challenges to disk"""
    chal_file = open("challenges.csv","w")
    chal_file.write(f"id,name,description,max_attempts,value,category,type,state,requirements\n")
    for challenge in challenges:
        chal_file.write(repr(challenge)+"\n")
    chal_file.close()

def dump_to_ctfd_json(not_challenges):
    chal_dict = {}
    chal_dict['count'] = len(not_challenges)
    chal_dict['results'] = []
    for c, not_chal in enumerate(not_challenges):
        chal_dict['results'].append(not_chal.__dict__)
    chal_dict['meta'] = {}
    return chal_dict

def main():
    # CLI Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("basezip",help="Zip file to pull ctfd metadata from, use a fresh CTFd instance export if you need one",nargs=1)
    parser.add_argument("directory",help="Directories of challenge packs to load",nargs="+")
    parser.add_argument("--force", action="store_true",help="ignore challenge pack validation errors")
    parser.add_argument("--install", action="store_true",help="use the local machine as the challenge host")
    parser.add_argument("--address", nargs=1, help="Server address to list in CTFd for participants to connect to")
    args = parser.parse_args()

    # TODO:determine action(s) vs running a blob script
    pass

    # Validate the problem set
    validate_challenge_bundles(args)

    # Search through our challenge directory and build our list of challenges
    challenges = get_challenge_list(args)

    # Build the flag list
    challenge_flag_list = get_flag_list(challenges)

    # Build file list (need to copy our files to the temp dir soon too)
    tempdirname, tempuploaddir = make_output_folder()

    # Copy challenge files into our temp dir
    for chal in challenges:
        chal.copy_zip_file_to_temp(tempuploaddir)

    challenge_file_list = [chal.ctfd_file_list() for chal in challenges]
    challenge_file_list = [file for file in challenge_file_list if not file == None]
    for i in range(len(challenge_file_list)):
        challenge_file_list[i].id = i+1

    # Installation
    def force_valid_username(name):
        """force replace certain special characters with _, force to lowercase,
        truncate username if it is over 30 characters"""
        resulting_username = re.sub("[\t\n /\\><?|\"\'`\[\]{},:;~!@#$%^&*()=]", "_", name)
        if resulting_username is None:
            resulting_username = name
        if len(resulting_username) > 30:
            resulting_username = resulting_username[:30]
        return resulting_username.lower()

    def copytree(src, dst, symlinks=False, ignore=None):
        """Handles the root dir already existing
        https://stackoverflow.com/questions/1868714/how-do-i-copy-an
        -entire-directory-of-files-into-an-existing-directory-using-pyth"""
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)

    def setup_listener(requires_server_path, server_zip_path, port, crontab_path, username):
        """sets up listeners"""
        if server_zip_path is not None:
            zip_ref = zipfile.ZipFile(server_zip_path, "r")
            unzipped_server_dir = os.path.join(os.path.abspath(os.path.dirname(server_zip_path)), "server")
            zip_ref.extractall(unzipped_server_dir)
            zip_ref.close()
            copytree(unzipped_server_dir, os.path.split(server_zip_path)[0])
            shutil.rmtree(unzipped_server_dir, ignore_errors=True)

        with open(requires_server_path, "r") as f:
            requires_server_string = f.readline()
            if requires_server_string == "" or requires_server_string is None:
                raise EmptyConfigFileError
            requires_server_string = re.sub("(\r)*\n", "", requires_server_string)
            requires_server_string = requires_server_string.split(" ")
            if len(requires_server_string) > 1:
                requires_server_string[1] = os.path.join(os.path.abspath(os.path.dirname(requires_server_path)),
                                                         requires_server_string[1])
                binary_path = requires_server_string[1]
            else:
                requires_server_string[0] = os.path.join(os.path.abspath(os.path.dirname(requires_server_path)),
                                                         requires_server_string[0])
                binary_path = requires_server_string[0]
            requires_server_string = " ".join(requires_server_string)

        # change perms for binary
        shutil.chown(binary_path, user="root", group="root")
        os.chmod(binary_path, 0o755)
        # create crontab
        command = f"python3 /usr/local/bin/challenge-listener.py '{requires_server_string}' {port}"
        # internal screaming because of cron
        crontab_string = f"@reboot {command}\n"
        with open(crontab_path, "w") as f:
            f.write(crontab_string)
        # don't touch these permission changes, cron freaks out
        shutil.chown(crontab_path, user=username, group="crontab")
        os.chmod(crontab_path, 0o600)

    def install_cron_reboot_persist():
        reboot_persist_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "scripts", "reboot_persist.sh")

        shutil.copy2(reboot_persist_path, "/usr/local/bin/")
        new_reboot_persist_path = os.path.join("/usr/local/bin/", "reboot_persist.sh")
        os.chmod(new_reboot_persist_path, 0o755)
        symlink_path = "/etc/rc{:d}.d/CRON_REBOOT_PERSIST"
        for init_no in range(0, 7):
            os.symlink(new_reboot_persist_path, symlink_path.format(init_no))

    def install_listener_script():
        # copy listener script to install location
        listener_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),"scripts", "challenge-listener.py")
        shutil.copy2(listener_path, "/usr/local/bin/")
        new_listener_path = os.path.join("/usr/local/bin/", "challenge-listener.py")
        os.chmod(new_listener_path, 0o755)

    def is_server_required(path):
        requires_server_path = None
        # find out if user accounts must be made or not
        for root, dirs, files in os.walk(path):
            for item in files:
                if item == "requires-server":
                    requires_server_path = os.path.join(root, item)
                    break
            if requires_server_path is not None:
                break
        return requires_server_path

    # Add users to local machine (setup challenge host)
    if args.install == True:
        install_listener_script()
        try:
            install_cron_reboot_persist()
        except FileExistsError as err:
            pass
        for challenge in challenges:
            challenge.requires_server_path = is_server_required(challenge.directory)

            if challenge.requires_server_path is not None:
                challenge.username = force_valid_username(challenge.name)
                new_user_home = os.path.join("/home/", challenge.username)
                os.system("useradd -m {:s}".format(challenge.username))

                # copy everything to new user's home dir
                # TODO: We should probably only copy a smaller zip to the user's home then run some predefined script per challenge
                copytree(challenge.directory, new_user_home)

                shutil.chown(new_user_home, user="root", group="root")
                # change file permissions recursively and locate important files

                server_zip_path = None
                # NOTE: {chris->clif} Could we not have just used an os.system("chmod -r ///") call then changed the flag back?, also shouldn't we delay this call until we've finished moving files
                for root, dirs, files in os.walk(new_user_home):
                    for item in dirs:
                        dir_path = os.path.join(root, item)
                        shutil.chown(dir_path, user="root", group="root")
                        os.chmod(dir_path, 0o050)
                    for item in files:
                        file_path = os.path.join(root, item)
                        shutil.chown(file_path, user="root", group=challenge.username)
                        os.chmod(file_path, 0o040)
                        if item == "requires-server":
                            challenge.requires_server_path = file_path
                        if item == "server.zip":
                            challenge.server_zip_path = file_path
                        if item == "flag.txt" or item == "flag":
                            shutil.chown(file_path, user="root", group=challenge.username)
                            os.chmod(file_path, 0o040)

                challenge.crontab_path = os.path.join("/var/spool/cron/crontabs", challenge.username)
                required_vars = {"requires_server_path": challenge.requires_server_path,
                                 "server_zip_path": challenge.server_zip_path,
                                 "port": challenge.port,
                                 "crontab_path": challenge.crontab_path,
                                 "username": challenge.username}
                for key in list(required_vars.keys()):
                    if required_vars[key] is None:
                        print(f"key: {key} is not present")
                        exit(1)
                try:
                    setup_listener(**required_vars)
                    challenge.description += f"\n\nnc {args.address[0]} {challenge.port}"
                except EmptyConfigFileError as err:
                    print(f"\n\nThe requires-server file for the challenge: {challenge.username} is empty, "
                          f"skipping listener setup for that challenge")
                    print("If you would like to attempt this process when the file contains a valid command, use the "
                          f"following dict: {required_vars}\n\n")
                    continue

    # Output ctfd jsons
    with open(f"{tempdirname}/challenges.json","w") as chal_json:
        _json_repr_challenges = [chal.ctfd_repr() for chal in challenges]
        json.dump(dump_to_ctfd_json(_json_repr_challenges), chal_json)

    with open(f"{tempdirname}/files.json","w") as files_json:
        json.dump(dump_to_ctfd_json(challenge_file_list), files_json)

    with open(f"{tempdirname}/flags.json","w") as flags_json:
        json.dump(dump_to_ctfd_json(challenge_flag_list), flags_json)


    # Make CTFd config zip  
    # unzip existing CTFd meta (we'll use every file that we didn't generate a version of)
    temp_unzip_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4())[-12:])
    os.makedirs(temp_unzip_dir)
    base_zip = zipfile.ZipFile(os.path.join(os.getcwd(), args.basezip[0]))
    base_zip.extractall(path=temp_unzip_dir)
    
    # Merge dirs
    config_files_to_copy = [f for f in os.listdir(os.path.join(temp_unzip_dir,'db')) if not f in os.listdir(tempdirname)]
    for f in config_files_to_copy:
        shutil.copy2(os.path.join(temp_unzip_dir,"db",f), os.path.join(tempdirname,f))
    shutil.rmtree(temp_unzip_dir)

    output_zip_name = os.path.join(os.getcwd(), "output", "CTF-name.zip")
    os.system(f"cd {tempdirname}/.. && zip {output_zip_name} -r db/ uploads/*/*")
    

if __name__=="__main__":
    main()
    
