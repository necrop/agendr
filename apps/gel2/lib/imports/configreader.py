#-------------------------------------------------------------------------------
# Name: ConfigReader
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

import re
import ConfigParser


true_rx = re.compile(r"^(yes|on|true|1)$", re.I)
false_rx = re.compile(r"^(no|off|false|0)$", re.I)


class ConfigReader(object):
    parser = ConfigParser.ConfigParser()
    file_read = False

    def __init__(self, file=None):
        if file and not ConfigReader.file_read:
            ConfigReader.parser.readfp(file)
            ConfigReader.file_read = True

    def get(self, section, option):
        value = ConfigReader.parser.get(section, option)
        if (value is None or
            value.strip() == "" or
            value.lower() == "none"):
            return None
        elif re.search(r"^-?[0-9]+$", value):
            return int(value)
        elif true_rx.search(value):
            return True
        elif false_rx.search(value):
            return False
        else:
            return value

    def items(self, section):
        return ConfigReader.parser.items(section)
