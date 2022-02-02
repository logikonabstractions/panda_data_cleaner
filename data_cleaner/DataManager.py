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
        self.merged_files = None


    def read_files(self):
        """ reachs each files in the dictionnary"""
        for var, details in self.cf.files_to_read.items():
            L.info(f"reading {var} - {details}")
            df = pd.read_excel(os.path.join(self.cf.inputs_folder, details["filename"]))
            setattr(self, var, df)
            self.files_list.append(var)           # accounting stuff

    def files_to_csv(self):
        """ writes all the df we have treated into csv for fixtures inputs """
        for f in self.files_list:
            L.info(f"Writing file {f} to csv ")
            df = getattr(self, f, None)
            df.to_csv(os.path.join(self.cf.outputs_folder, f"{f}.csv"), index=False)

    def file_to_excel(self, file, filename="out.xlsx"):
        file.to_excel(os.path.join(self.cf.outputs_folder, filename), index=False)
        L.info(f"Written file {filename} to dir {file}")

    def clean_all_files(self):
        """ cleanup for all the data in the fileswe have read """
        # cleanup for each/most files
        for f in self.files_list:
            try:
                fconfs = self.cf.get_file_configs(f)
                df = getattr(self, f, None)

                # loading the treatment to apply here from the configs
                treatments = self.cf.get_treatments(f)                  # so any empty 1st row gets dropped
                df.dropna(axis=0, inplace=True, subset=[df.columns[0]])

                for treat in treatments:
                    func = getattr(self, treat)
                    func(df, f)

                # self.clean_spaces(df)
                # self.clean_dates(df, f)

                if fconfs.get("set_na_zeros"):         # cols we want to set to all zeroes
                    for conf in fconfs.get("set_na_zeros"):
                        df[conf].fillna(0, inplace=True)
            except Exception as ex:
                L.error(f"Error cleaning all files: {f}. Ex: {ex}")

        # gloabal stuff
        # checking for missing foreign keys
        self.fk_checks()

    def fk_checks(self):
        checks = self.cf.fk_checks
        if checks:
            for check in checks:
                for fk, target in check.items():
                    try:
                        fk_filename, fk_name = fk.split(sep=".")
                        target_file, target_name = target.split(sep=".")
                        fk_file = getattr(self, fk_filename)


                        # get the panda columns
                        fk_col = getattr(self, fk_filename)[fk_name]
                        target_col = getattr(self, target_file)[target_name]

                        # apply, leave fk value if fk in target_col, fk = 0 otherwise
                        # assign that corrected col of values to fk_file.fk_name column
                        fk_file[fk_name] = fk_file[fk_name].astype(int).apply(lambda x: x if x in target_col.values else 0)
                        fk_file[fk_name].fillna(0, inplace=True)
                        # ans = fk_col.apply(lambda x: x if x in target_col.values else 0)
                        # fk_file[fk_name] = ans
                        L.info(f"fk table: {fk_filename}, fkname: {fk_name}, target table: {target_file}, targetname: {target_name},  ")
                    except Exception as ex:
                        L.error(f"COULDN'T FULLFIL FK_CHECK: {fk_filename}, {target_file}, {fk_name}")
                        L.error(f"Exc: {ex}")

    def clean_dates(self, df, filename):
        """ cleans/formats dates properly"""

        # get the fieldnames (cols) that are dates
        datefields = self.cf.get_date_fields(filename)
        # slice the df to work on those cols
        datecols = df.loc[:,datefields]
        # format in the output expected by django fixtures imports - parse it to a pd datetime,
        for col in datecols:
            try:
                # df[col] = pd.to_datetime(df[col], format='%Y/%m/%d/').dt.date
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce").dt.date
                df[col] = df[col].fillna("2001-01-01")
            except Exception as ex:
                L.error(f"COULDN'T CLEAN DATES FOR: {filename} col -- {col} -- from {datefields}. Ex: {ex}")
        return df

    def clean_spaces(self, df, filename=None):
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
        df.replace(to_replace='\s\s+', value=" ", regex=True, inplace=True)  # remove duplicated spaces from previous stuff
        return df

    def clean_missing_values(self, df, filename=None):
        """ replaces empty strings with None """
        return df.replace(r'^\s*$', None, regex=True, inplace=True)


    def clean_bools(self, df, filename=None):
        """ replaces any "FALSE", "TRUE" with python True False, anywhere in the file.
            0,1 can be parsed as t/f by django for fixtures corresponding to booleanfields, so we leave those as-is
         """
        df.replace(to_replace='TRUE', value=True, regex=True, inplace=True)  # trailing
        df.replace(to_replace='FALSE', value=False, regex=True, inplace=True)  # trailing
        return df

