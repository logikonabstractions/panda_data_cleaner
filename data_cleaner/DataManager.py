""" manages the i/o, keeps files/objs in memory etc. """
from utils.utils import Configs
import pandas as pd
import os
from utils.logger import get_root_logger
L = get_root_logger("engine_logger")


class DataManager:

    def __init__(self, configs=Configs(None)):
        self.cf = configs
        self.files_list = []        # since we use setattr(...), we store hte var names here for treatement we like to iterat on all of them

    def read_files(self):
        """ reachs each files in the dictionnary"""
        for file_desc in self.cf.files_to_read:
            for k,v, in file_desc.items():
                L.info(f"reading {k} - {v}")
                df = pd.read_excel(os.path.join(self.cf.inputs_folder, v))
                setattr(self, k, df)
                self.files_list.append(k)           # accounting stuff

    def clean_all_files(self):
        """ cleanup for all the data in the fileswe have read """
        for f in self.files_list:
            df = getattr(self, f, None)
            L.info(f"Should have a bunch of newlines:{df.loc[2,'note']}")
            self.cleanup_spaces(df)
            L.info(f"Newlines should be gone:{df.loc[2,'note']}")

    def cleanup_spaces(self, df):
        """ takes a dataframe & cleans up dbase's weird spaces:
            - trailing whitespaces
            - leading whitespaces
            - repeated whitespaces within text
        """
        L.info(f"Removing trailing whitespaces ...")
        df.replace(to_replace='\s*$', value="", regex=True, inplace=True)  # trailing
        L.info(f"Removing leading whitespaces ...")
        df.replace(to_replace='^\s*', value="", regex=True, inplace=True)  # leading
        L.info(f"Removing repeated whitespaces ...")
        df.replace(to_replace='\n', value=" ", regex=True, inplace=True)  # newlines
        df.replace(to_replace='\r', value=" ", regex=True, inplace=True)  # carriage returns
        df.replace(to_replace='\t', value=" ", regex=True, inplace=True)  # tabs
        df.replace(to_replace='_x000D_', value=" ", regex=True, inplace=True)  # weird placeholdesr for carriage returns
        df.replace(to_replace='\s\s+', value=" ", regex=True,
                   inplace=True)  # remove duplicated spaces from previous stuff

        return df