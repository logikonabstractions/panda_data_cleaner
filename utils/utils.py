import sys
import os
# directories
LOG_DIR             = "logs"
TEST_DIR            = "tests"
# filenames
CONFIGS_FILE        = "configs.json"
# others
BASE_LOGGER_NAME    = "engine_logger"
ROOT                = sys.path[0]
XLSX_ROOT           = "/home/fv/Documents/pro-2020/voltec/db_djangomodels_parser"


class Configs:
    """ just a wrapper around the config file, so we can easily add props etc.. for conveniences"""
    def __init__(self, configs):
        self.cf = configs

    def get_date_fields(self, filename):
        """ returns the list of fields marked as date for this file form the configs """
        return self.files_to_read[filename]["datefields"]

    def get_file_configs(self, filename):
        """ returns the configs for a specific file """
        return self.files_to_read[filename]

    @property
    def files_to_read(self):
        """ returns the configs relevent for the data manager """
        return self.cf["main_program"]["files_to_read"]

    @property
    def inputs_folder(self):
        # return f'{XLSX_ROOT}/{self.cf["main_program"]["inputs_folder"]}'
        return f'{os.path.join(XLSX_ROOT, self.cf["main_program"]["inputs_folder"])}'

    @property
    def outputs_folder(self):
        # return f'{XLSX_ROOT}/{self.cf["main_program"]["inputs_folder"]}'
        return f'{os.path.join(XLSX_ROOT, self.cf["main_program"]["outputs_folder"])}'

    @property
    def fk_checks(self):
        """ returns the details of fk to check """
        return self.cf["main_program"]["fk_checks"]
