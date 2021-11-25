import sys
# directories
LOG_DIR             = "logs"
TEST_DIR            = "tests"
# filenames
CONFIGS_FILE        = "configs.json"
# others
BASE_LOGGER_NAME    = "engine_logger"
ROOT                = sys.path[0]


class Configs:
    """ just a wrapper around the config file, so we can easily add props etc.. for conveniences"""
    def __init__(self, configs):
        self.cf = configs


    @property
    def files_to_read(self):
        """ returns the configs relevent for the data manager """
        return self.cf["main_program"]["files_to_read"]

    @property
    def inputs_folder(self):
        return f'{ROOT}/{self.cf["main_program"]["inputs_folder"]}'
