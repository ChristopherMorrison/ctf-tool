#!/usr/bin/python3
import os
import argparse
import json
import re
import shutil
import uuid
import zipfile
import time
import tempfile
import pickle
from src.validate import validate_ctf_directory
from src.challenge import Challenge


class EmptyConfigFileError(Exception):
    pass


def validate_challenge_bundles(args):
    """ Validates all specified directories in args.directories """
    for challenge_pack in args.directory:
        problem_dir = os.path.join(os.getcwd(), challenge_pack)
        if validate_ctf_directory(problem_dir) != 0 and args.force is not True:
            quit(1)


def get_challenge_list(args):
    """ Builds a list of challenge objects from all challenge bundles in args.directory """
    challenges = []
    challenge_names = []
    for challenge_pack in args.directory:
        problem_dir = os.path.join(os.getcwd(), challenge_pack)
        category_dirs = [dir for dir in os.listdir(problem_dir) if os.path.isdir(os.path.join(problem_dir, dir))]
        for category in category_dirs:
            for challenge in os.listdir(os.path.join(problem_dir, category)):
                if os.path.isdir(os.path.join(problem_dir, category, challenge)):
                    chal = Challenge(os.path.join(problem_dir, category, challenge))
                    if chal.name in challenge_names:
                        print(f"Two or more challenges named {chal.name}")
                        # This is because of the zip file names for challenge.zip not being
                        # hash based. This may also be a limitation of CTFd #TODO
                        quit(1)
                    challenges.append(chal)
                    challenge_names.append(chal.name)
    for i in range(len(challenges)):
        challenges[i].id = i + 1
    return challenges


def get_flag_list(challenges):
    """ Builds a list of objects from challenges that dumbs nicely into json for CTFd """
    challenge_flag_list = []
    challenge_flag_list = [chal.ctfd_flag_repr() for chal in challenges]
    challenge_flag_list = [flag for flag in challenge_flag_list if flag is not None]
    for i in range(len(challenge_flag_list)):
        challenge_flag_list[i].id = i + 1
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
    chal_file = open("challenges.csv", "w")
    chal_file.write(f"id,name,description,max_attempts,value,category,type,state,requirements\n")
    for challenge in challenges:
        chal_file.write(repr(challenge) + "\n")
    chal_file.close()


def dump_to_ctfd_json(not_challenges):
    chal_dict = dict()
    chal_dict['count'] = len(not_challenges)
    chal_dict['results'] = []
    for c, not_chal in enumerate(not_challenges):
        chal_dict['results'].append(not_chal.__dict__)
    chal_dict['meta'] = {}
    return chal_dict


def force_valid_username(name):
    """force replace certain special characters with _, force to lowercase,
    truncate username if it is over 30 characters. Some people think they are super clever when
    they use accents in their challenge names. (╯°□°）╯︵ ┻━┻"""
    resulting_username = re.sub("[^A-Za-z0-9_-]", "_", name)
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


def get_binary_path_from_requires_server_string(requires_server_string):
    requires_server_args = requires_server_string.split(" ")
    if len(requires_server_args) > 1:
        binary_path = requires_server_args[1]
    else:
        binary_path = requires_server_args[0]

    return binary_path


def get_requires_server_string(path):
    with open(path, "r") as f:
        requires_server_string = f.readline()

    if requires_server_string == "" or requires_server_string is None:
        raise EmptyConfigFileError
    requires_server_string = re.sub("(\r)*\n", "", requires_server_string)

    requires_server_args = requires_server_string.split(" ")
    if len(requires_server_args) > 1:
        requires_server_args[1] = os.path.join(os.path.abspath(os.path.dirname(path)),
                                               requires_server_args[1])
    else:
        requires_server_args[0] = os.path.join(os.path.abspath(os.path.dirname(path)),
                                               requires_server_args[0])
    requires_server_string = " ".join(requires_server_args)
    return requires_server_string


def get_listener_command(requires_server_string, port):
    return f"python3 /usr/local/bin/challenge-listener.py '{requires_server_string}' {port}"


def setup_listener(requires_server_path, server_zip_path, port, crontab_path, username):
    """sets up listeners"""
    if server_zip_path is not None:
        zip_ref = zipfile.ZipFile(server_zip_path, "r")
        unzipped_server_dir = os.path.join(os.path.abspath(os.path.dirname(server_zip_path)), "server")
        zip_ref.extractall(unzipped_server_dir)
        zip_ref.close()
        copytree(unzipped_server_dir, os.path.split(server_zip_path)[0])
        shutil.rmtree(unzipped_server_dir, ignore_errors=True)

    requires_server_string = get_requires_server_string(requires_server_path)
    command = get_listener_command(requires_server_string, port)

    binary_path = get_binary_path_from_requires_server_string(requires_server_string)
    # change perms for binary
    shutil.chown(binary_path, user="root", group="root")
    os.chmod(binary_path, 0o755)
    # create crontab

    create_user_crontab(crontab_path, command, username)


def create_user_crontab(crontab_path, command, username):
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
    listener_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "scripts", "challenge-listener.py")
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


def install_on_current_machine(challenge, new_user_home, address):
    os.system("useradd -m {:s}".format(challenge.username))
    if not os.path.exists(challenge.server_zip_path):
        # Directory is missing server.zip, but letting execution continue so that the user is warned
        challenge.server_zip_path = None
    else:
        shutil.copy2(challenge.server_zip_path, new_user_home)
    shutil.copy2(challenge.requires_server_path, new_user_home)
    # copy everything to new user's home dir
    # TODO: We should probably only copy a smaller zip to the user's home
    # then run some predefined script per challenge
    # Clif: "Agreed", doing it with the server.zip and requires-server now
    # copytree(challenge.directory, new_user_home)

    shutil.chown(new_user_home, user="root", group="root")
    # NOTE: {chris->clif} Could we not have just used an os.system("chmod -r ///") call then
    # changed the flag back?, also shouldn't we delay this call until we've finished moving files
    # NOTE: {clif->chris} You right, I'll fix that.
    os.system(f"chown -R root:root {new_user_home}")
    os.system(f"chmod -R 040 {new_user_home}")

    required_vars = {"requires_server_path": challenge.requires_server_path,
                     "server_zip_path": challenge.server_zip_path,
                     "port": challenge.port,
                     "crontab_path": challenge.crontab_path,
                     "username": challenge.username}

    empty_required_keys = list()
    for key in list(required_vars.keys()):
        if required_vars[key] is None:
            empty_required_keys.append(key)

    if len(empty_required_keys) > 0:
        print(f"Challenge listener not set up for challenge: {challenge.name} because the following "
              "required parameters were not fulfilled:")
        for i in empty_required_keys:
            print(f"{i}")
        print("")
        return
    try:
        # I might just change this to pass in the whole challenge object
        setup_listener(**required_vars)
        challenge.description += f"\n\nnc {address} {challenge.port}"
    except EmptyConfigFileError:
        print(f"\n\nThe requires-server file for the challenge: {challenge.username} is empty, "
              f"skipping listener setup for that challenge")
        print("If you would like to attempt this process when the file contains a valid command, use the "
              f"following dict: {required_vars}\n\n")
        raise EmptyConfigFileError


def main():
    # CLI Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("basezip",
                        help="Zip file to pull ctfd metadata from, use a fresh CTFd instance export if you need one",
                        nargs=1)
    parser.add_argument("directory", help="Directories of challenge packs to load", nargs="+")
    parser.add_argument("--force", action="store_true", help="ignore challenge pack validation errors")
    parser.add_argument("--install", action="store_true", help="use the local machine as the challenge host")
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
    challenge_file_list = [file for file in challenge_file_list if file is not None]
    for i in range(len(challenge_file_list)):
        challenge_file_list[i].id = i + 1

    # Installation

    # Add users to local machine (setup challenge host)
    if args.install is True:
        install_listener_script()
        try:
            install_cron_reboot_persist()
        except FileExistsError:
            pass
        except FileNotFoundError:
            print("/etc/rc.#d folders not present on current system, skipping reboot persistence")
            pass

        for challenge in challenges:
            challenge.requires_server_path = is_server_required(challenge.directory)

            if challenge.requires_server_path is not None:
                # Set vars for challenge objects
                challenge.username = force_valid_username(challenge.name)
                new_user_home = os.path.join("/home/", challenge.username)
                challenge.server_zip_path = os.path.join(os.path.split(challenge.requires_server_path)[0], "server.zip")
                challenge.crontab_path = os.path.join("/var/spool/cron/crontabs", challenge.username)
                try:
                    pass
                    install_on_current_machine(challenge, new_user_home, args.address)
                except EmptyConfigFileError:
                    continue

        """for challenge in challenges:
            if challenge.requires_server_path is not None:
                with open(f"{challenge.name}.pickle", "wb") as f:
                    pickle.dump(challenge, f)
        """

    # Output ctfd jsons
    with open(f"{tempdirname}/challenges.json", "w") as chal_json:
        _json_repr_challenges = [chal.ctfd_repr() for chal in challenges]
        json.dump(dump_to_ctfd_json(_json_repr_challenges), chal_json)

    with open(f"{tempdirname}/files.json", "w") as files_json:
        json.dump(dump_to_ctfd_json(challenge_file_list), files_json)

    with open(f"{tempdirname}/flags.json", "w") as flags_json:
        json.dump(dump_to_ctfd_json(challenge_flag_list), flags_json)

    # Make CTFd config zip
    # unzip existing CTFd meta (we'll use every file that we didn't generate a version of)
    temp_unzip_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4())[-12:])
    os.makedirs(temp_unzip_dir)
    base_zip = zipfile.ZipFile(os.path.join(os.getcwd(), args.basezip[0]))
    base_zip.extractall(path=temp_unzip_dir)

    # Merge dirs
    config_files_to_copy = [f for f in os.listdir(os.path.join(temp_unzip_dir, 'db')) if
                            f not in os.listdir(tempdirname)]
    for f in config_files_to_copy:
        shutil.copy2(os.path.join(temp_unzip_dir, "db", f), os.path.join(tempdirname, f))
    shutil.rmtree(temp_unzip_dir)

    output_zip_name = os.path.join(os.getcwd(), "output", "CTF-name.zip")
    os.system(f"cd {tempdirname}/.. && zip {output_zip_name} -r db/ uploads/*/*")


if __name__ == "__main__":
    main()
