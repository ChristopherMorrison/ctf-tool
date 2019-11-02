import argparse

from abc import ABC, abstractmethod

class BaseCommand(ABC):
    # inspired by pip
    name = None
    description = None
    hidden = False
    
    def __init__(self):
        pass

    def subparser(self):
        parser =  argparse.ArgumentParser(prog=self.name,
                                       description=self.description)
        parser.add_argument("subcommand",
                            choices=[f[3:] for f in dir(self) if f.startswith("do_")])
        return parser
        
    def run_command(self, argline):
        try:
            # New test that dynamically rips the do_x choices from the local class
            # more compact implementation of the db subcommand parser that isn't a billion if statements
            args = self.subparser().parse_args(argline[:1])
            real_func = getattr(self, f"do_{args.subcommand}", None)
            return real_func(argline[1:])
        except Exception:
            # Add an option called default
            # This allows non-tiered commands
            # Command must implement __call__
            real_func = self
            return real_func(argline)


# Derive all commands and names from package automatically
# current way annoying but necessary without abusing the language
from src.commands.build import Buildcmd
from src.commands.validate import Validatecmd

command_list = [
    Buildcmd,
    Validatecmd
]

command_dict = dict()
for cmd in command_list:
    command_dict[cmd.name]=cmd