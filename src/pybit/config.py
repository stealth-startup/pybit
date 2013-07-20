# Copyright (c) 2010 Witchspace <witchspace81@gmail.com>
# Copyright (c) 2013 Rex
"""
Utilities for reading bitcoin configuration files.
"""


def read_config_file(filename):
    """
    Read a simple ``'='``-delimited config file.
    Raises :const:`IOError` if unable to open file, or :const:`ValueError`
    if an parse error occurs.
    """
    f = open(filename)
    try:
        cfg = {}
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    (key, value) = line.split('=', 1)
                    cfg[key] = value
                except ValueError:
                    pass  # Happens when line has no '=', ignore
    finally:
        f.close()
    return cfg


def read_default_config(filename=None):
    """
    Read bitcoin default configuration from the current user's home directory.

    Arguments:

    - `filename`: Path to a configuration file in a non-standard location (optional)

    TODO: windows is not included
    """
    if filename is None:
        import os
        import platform
        home = os.getenv("HOME")
        if not home:
            raise IOError("Home directory not defined, don't know where to look for config file")

        if platform.system() == "Darwin":
            location = 'Library/Application Support/Bitcoin/bitcoin.conf'
        else:
            location = '.bitcoin/bitcoin.conf'
        filename = os.path.join(home, location)

    elif filename.startswith("~"):
        import os
        filename = os.path.expanduser(filename)

    try:
        return read_config_file(filename)
    except (IOError, ValueError):
        pass  # Cannot read config file, ignore
