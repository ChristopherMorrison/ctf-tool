

class EmptyConfigFileError(Exception):
    pass


# eat a txt file
def contents_of(file):
    try:
        return open(file).read().strip()
    except:
        return None