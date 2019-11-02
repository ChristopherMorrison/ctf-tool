from humanfriendly.tables import format_pretty_table
import colorama
colorama.init()

def print_object_table(objects, align_left=['id','friendlyname']):
    if objects:
        header = align_left + [attr for attr in objects[0].__dict__ if not attr.startswith("_") and not attr in align_left]
        table_contents = []
        for obj in objects:
            table_contents.append([getattr(obj, header) for header in header])
        header = [h.upper() for h in header]
        print(format_pretty_table(table_contents, header))
    else:
        log_warn("Nothing to show")


# FTODO: investigate python logger
def log_success(data):
    print(colorama.Fore.GREEN + " [+]" + colorama.Style.RESET_ALL + " " + data)

def log_warn(data):
    print(colorama.Fore.YELLOW + " [!]" + colorama.Style.RESET_ALL + " " + data)

def log_error(data):
    print(colorama.Fore.RED + " [!]" + colorama.Style.RESET_ALL + " " + data)

def log_normal(data):
    print(colorama.Fore.BLUE + " [*]" + colorama.Style.RESET_ALL + " " + data)
