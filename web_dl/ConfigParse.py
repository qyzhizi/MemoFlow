from configparser import RawConfigParser as ConfigParser


class ConfigParse(object):

    def __init__(self, file):
        self.file = file
        self.conf = ConfigParser()

    # read ini file to dict
    def read_file(self):
        self.conf.read(self.file)
        return {section: dict(self.conf.items(section))
                for section in self.conf.sections()}
