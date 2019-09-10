#!/usr/bin/env python3
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
import shlex
import textwrap
from src.validate import validate_ctf_directory
from src.challenge import Challenge
from src.util import EmptyConfigFileError


# CTFd Util functions
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
                        # TODO: v2 This is because of the zip file names for challenge.zip not being hash based. This may also be a limitation of CTFd, need to investigate
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


def make_ctfd_output_folder():
    """ Builds a temporary output folder to copy challenge data into before zip"""
    tempdirname = os.path.join("output", time.strftime("%Y.%m.%d-%H:%M:%S"))
    tempuploaddir = os.path.join(tempdirname, "uploads")
    tempdirname = os.path.join(tempdirname, "db")
    os.makedirs(tempdirname)
    os.makedirs(tempuploaddir)
    return tempdirname, tempuploaddir


def output_ctfd_csv(challenges): # TODO: unused
    """ Writes the csv format of the ctfd challenges to disk"""
    chal_file = open("challenges.csv", "w")
    chal_file.write(f"id,name,description,max_attempts,value,category,type,state,requirements\n")
    for challenge in challenges:
        chal_file.write(repr(challenge) + "\n")
    chal_file.close()


def dump_to_ctfd_json(not_challenges): # TODO: "not_challenges" is confusing
    chal_dict = dict()
    chal_dict['count'] = len(not_challenges)
    chal_dict['results'] = []
    for c, not_chal in enumerate(not_challenges):
        chal_dict['results'].append(not_chal.__dict__)
    chal_dict['meta'] = {}
    return chal_dict


# Server challenge installation (cron)
def setup_listener(challenge): # TODO: break into smaller functions, this does a lot
    """sets up listeners"""
    if challenge.server_zip_path is not None:
        zip_ref = zipfile.ZipFile(challenge.server_zip_path, "r")
        unzipped_server_dir = os.path.join(os.path.abspath(os.path.dirname(challenge.server_zip_path)), "server")
        zip_ref.extractall(unzipped_server_dir)
        zip_ref.close()
        copytree(unzipped_server_dir, os.path.split(challenge.server_zip_path)[0])
        shutil.rmtree(unzipped_server_dir, ignore_errors=True)

    binary_path = get_binary_path_from_requires_server_string(challenge.requires_server_string)
    # change perms for binary
    #shutil.chown(binary_path, user="root", group="root")
    #os.chmod(binary_path, 0o755)
    # create crontab
    create_user_crontab(challenge.crontab_path, challenge.listener_command, challenge.username)


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


def install_systemd_service(command, username):
    """
        Creates a new service called <username>.service and
    """
    systemd_unitfile = f"""[Unit]
                           Description=Run {command} as user {username}

                           [Service]
                           User={username}
                           Type=exec
                           ExecStart={command}
                           ExecReload=/bin/kill -1 -- $MAINPID
                           ExecStop=/bin/kill -- $MAINPID
                           KillMode=process
                           Restart=on-failure
                        
                           [Install]
                           WantedBy=multi-user.target"""
    systemd_unitfile = textwrap.dedent(systemd_unitfile)
    systemd_unit_path = f"/etc/systemd/system/{username}.service"
    with open(systemd_unit_path, "w") as f:
        f.write(systemd_unitfile)
    os.chmod(systemd_unit_path, 0o644)
    os.system("systemctl daemon-reload")
    os.system(f"systemctl enable {username}.service")


# Server challenge installation (files)
def get_binary_path_from_requires_server_string(requires_server_string):
    """
    Gets the binary to run from the requires-server file. Tries to be smart with interpreters
    TODO: force shebang lines to simplify this
    """
    requires_server_args = shlex.split(requires_server_string)
    if len(requires_server_args) > 1:
        binary_path = requires_server_args[1]
    else:
        binary_path = requires_server_args[0]

    return binary_path


def copytree(src, dst, symlinks=False, ignore=None):
    """
    Handles the root dir already existing
    https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


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
    # add user and copy everything to new user's home dir
    os.system("useradd -m {:s}".format(challenge.username))
    if not os.path.exists(challenge.server_zip_path):
        # Directory is missing server.zip, but letting execution continue so that the user is warned
        challenge.server_zip_path = None
    else:
        shutil.copy2(challenge.server_zip_path, new_user_home)
        challenge.server_zip_path = os.path.join(new_user_home, "server.zip")
    shutil.copy2(challenge.requires_server_path, new_user_home)
    challenge.requires_server_path = os.path.join(new_user_home, "requires-server")
    
    # I forget what this does
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
        # Setup crontab
        setup_listener(challenge)
        #os.system(f"chown root:{challenge.username} {new_user_home}/flag.txt")
        #os.system(f"chmod 020 {new_user_home}/flag.txt")
        challenge.description += f"\n\nnc {address} {challenge.port}"
        os.remove(f"{new_user_home}/requires-server")
        os.remove(f"{new_user_home}/server.zip")
    except EmptyConfigFileError:
        print(f"\n\nThe requires-server file for the challenge: {challenge.username} is empty, "
              f"skipping listener setup for that challenge")
        raise EmptyConfigFileError
    
    # Set permissions on user dir (root:challenge_user -rx-rx---)
    # TODO: use the python equivalent although this is pretty much universal
    os.system(f"chown -R root:{challenge.username} {new_user_home}") 
    os.system(f"chmod -R 550 {new_user_home}")


# Docker challenge installation TODO v2
def create_challenge_docker_env(path, challenges):
    docker_compose_str = "version: '3.3'\nservices:\n"
    dockerenv_path = os.path.join(path, "dockerenv")
    listener_script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                        "scripts",
                                        "challenge-listener.py")
    required_package_script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                "scripts",
                                                "install_required_packages.sh")
    os.mkdir(dockerenv_path)
    # yaml is anti tabs
    t = "    "
    for challenge in challenges:

        challenge_docker_path = os.path.join(dockerenv_path, challenge.username)
        os.mkdir(challenge_docker_path)
        try:
            shutil.copy2(listener_script_path, challenge_docker_path)
            shutil.copy2(required_package_script_path, challenge_docker_path)
            shutil.copy2(challenge.server_zip_path, challenge_docker_path)
            shutil.copy2(challenge.requires_server_path, challenge_docker_path)
        except Exception:
            continue
        challenge.generate_dockerfile(challenge_docker_path)
        docker_compose_str += f"{t}{challenge.username}:\n"
        docker_compose_str += f"{t}{t}build: '{challenge.username}/.'\n"
        docker_compose_str += f"{t}{t}user: '{challenge.username}'\n"
        docker_compose_str += f"{t}{t}tty: true\n"
        docker_compose_str += f"{t}{t}ports:\n"
        docker_compose_str += f"{t}{t} - '{challenge.port}:{challenge.port}'\n"

    docker_compose_path = os.path.join(dockerenv_path, "docker-compose.yml")
    with open(docker_compose_path, "w") as f:
        f.write(docker_compose_str)


# Main
def main():
    # CLI Parser
    # TODO: v2 make this like the range-master parser so it's easier to extend
    parser = argparse.ArgumentParser()
    parser.add_argument("--basezip",
                        help="Zip file to pull ctfd metadata from, use a fresh CTFd instance export if you need one",
                        nargs=1,
                        default=["resources/ctfd.base.zip"])
    parser.add_argument("directory", help="Directories of challenge packs to load", nargs="+")
    parser.add_argument("--force", action="store_true", help="ignore challenge pack validation errors")
    parser.add_argument("--install", action="store_true", help="use the local machine as the challenge host")
    parser.add_argument("-d", "--docker", help="Install service challenges through docker", action='store_true')
    parser.add_argument("--address", nargs=1, help="Server address to list in CTFd for participants to connect to")
    parser.add_argument("--name", default="ctf-tool", help="Name of the output zip file")
    args = parser.parse_args()

    # Validate the problem set
    if any([validate_ctf_directory(dir) for dir in args.directory]):
        quit(1)

    # Search through our challenge directory and build our list of challenge objects
    challenges = get_challenge_list(args)

    # CTFd
    # Build the flag list
    challenge_flag_list = get_flag_list(challenges)

    # Build file list (need to copy our files to the temp dir soon too)
    tempdirname, tempuploaddir = make_ctfd_output_folder()
    
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
        assert os.geteuid() == 0, "You must be root to install challenges!"
        for challenge in challenges:
            challenge.requires_server_path = is_server_required(challenge.directory)

            if challenge.requires_server_path is not None:
                # Set vars for challenge objects
                challenge.username = force_valid_username(challenge.name)
                new_user_home = os.path.join("/home/", challenge.username)
                challenge.server_zip_path = os.path.join(os.path.split(challenge.requires_server_path)[0], "server.zip")
                challenge.crontab_path = os.path.join("/var/spool/cron/crontabs", challenge.username)
                challenge.set_requires_server_string()
                challenge.set_listener_command()
        if args.docker is True:
            challenges_requiring_server = [challenge for challenge in challenges if challenge.requires_server_path is not None]
            create_challenge_docker_env(os.getcwd(), challenges_requiring_server)
            os.chdir("dockerenv")
            os.system("docker-compose build && docker-compose up -d")
            os.chdir(os.path.abspath(os.path.dirname(os.getcwd())))
        else:
            for challenge in challenges:
                # TODO: v2 make this a factory method with something like challenge.type
                if challenge.requires_server_path is not None:
                    new_user_home = os.path.join("/home/", challenge.username)
                    try:
                        install_on_current_machine(challenge, new_user_home, args.address)
                    except EmptyConfigFileError:
                        continue
            install_listener_script()
            try:
                install_cron_reboot_persist()
            except FileExistsError:
                pass
            except FileNotFoundError:
                print("/etc/rc.#d folders not present on current system, skipping reboot persistence")

    # Output CTFd jsons
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

    output_zip_name = os.path.join(os.getcwd(), "output", f"{args.name}.ctfd.{time.strftime('%Y.%m.%d-%H:%M:%S')}.zip")
    os.system(f"cd {tempdirname}/.. && zip {output_zip_name} -r db/ uploads/*/*")


if __name__ == "__main__":
    main()
