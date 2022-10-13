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
# XLSX_ROOT           = "/home/fv/Documents/pro-2020/voltec/db_djangomodels_parser"

from utils.logger import get_root_logger
L = get_root_logger("engine_logger")

class Configs:
    """ just a wrapper around the config file, so we can easily add props etc.. for conveniences"""
    def __init__(self, configs):
        self.cf = configs
        # we use the xlsx_root if provided, if none we use the project's root
        if configs:
            if os.environ.get("ROOT_INPUT_FILES_DIR"):
                self.xlsx_root = os.environ.get("ROOT_INPUT_FILES_DIR")
            else:
                self.xlsx_root = configs["main_program"].get("xlsx_root") if configs["main_program"].get("xlsx_root") else ROOT

    def get_date_fields(self, filename):
        """ returns the list of fields marked as date for this file form the configs """
        return self.files_to_read[filename]["datefields"]

    def get_file_configs(self, filename):
        """ returns the configs for a specific file """
        return self.files_to_read[filename]


    def get_treatments(self, filename):
        """ """
        try:
            return self.files_to_read[filename]["treatments"]
        except Exception as ex:
            L.info(f"Couldn't get treatement for filename {filename}. Ex: {ex}")
            return []
    def get_pretreatments(self, filename):
        """ """
        try:
            return self.files_to_read[filename]["pretreatments"]
        except Exception as ex:
            L.info(f"No pretreatments for filename {filename}. Ex: {ex}")
            return []

    @property
    def merges(self):
        return self.cf["main_program"]["merges"]

    @property
    def files_to_read(self):
        """ returns the configs relevent for the data manager """
        return self.cf["main_program"]["files_to_read"]

    @property
    def inputs_folder(self):
        if os.environ.get("RAW_INPUT_XLSX"):
            return f'{os.path.join(self.xlsx_root, os.environ.get("RAW_INPUT_XLSX"))}' 
        else:
            return f'{os.path.join(self.xlsx_root, self.cf["main_program"]["inputs_folder"])}'

    @property
    def outputs_folder(self):
        if os.environ.get("CLEANED_INPUT_CSV"):
            return f'{os.path.join(self.xlsx_root, os.environ.get("CLEANED_INPUT_CSV"))}' 
        else:
            return f'{os.path.join(self.xlsx_root, self.cf["main_program"]["outputs_folder"])}'

    @property
    def fk_checks(self):
        """ returns the details of fk to check """
        return self.cf["main_program"].get("fk_checks")
