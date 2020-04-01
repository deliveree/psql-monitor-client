from os import listdir
from toml import load


def load_conf(folder_path="conf"):
    """Loads all conf from all files inside a given folder.
    Args:
        folder_path (str): Path to the folder
    """
    filenames = listdir(folder_path)
    conf = [
        folder_path + "/" + filename
        for filename in filenames if filename.endswith(".conf")
    ]
    return load(conf)
