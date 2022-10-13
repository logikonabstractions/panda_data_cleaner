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
            # L.info(f"Finished reading as DF")
            setattr(self, var, df)
            self.files_list.append(var)           # accounting stuff

    def files_to_csv(self):
        """ writes all the df we have treated into csv for fixtures inputs """
        for f in self.files_list:
            L.info(f"Writing file {f} to csv at {os.path.join(self.cf.outputs_folder, f'{f}.csv')} ")
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
                L.info(f"Cleaning file {f}")
                fconfs = self.cf.get_file_configs(f)
                df = getattr(self, f, None)

                # loading the treatment to apply here from the configs
                pre_treatments = self.cf.get_pretreatments(f)
                treatments = self.cf.get_treatments(f)
                df.dropna(axis=0, inplace=True, subset=[df.columns[0]])     # so any empty 1st row gets dropped

                # pretreatments
                for pretreat in pre_treatments:
                    func_name = list(pretreat.keys())[0]
                    func = getattr(self, func_name)
                    df = func(df, pretreat[func_name])

                #treaments
                for treat in treatments:
                    L.info(f"df.shape (treatements): {df.shape}")
                    func = getattr(self, treat)
                    func(df, f)

                if fconfs.get("set_na_zeros"):         # cols we want to set to all zeroes
                    for conf in fconfs.get("set_na_zeros"):
                        df[conf].fillna(0, inplace=True)

                if fconfs.get("set_na_null"):         # cols we want to set to set all missing val to null values/None
                    for conf in fconfs.get("set_na_null"):
                        df[conf].fillna("None", inplace=True)


                # replace all NA by empty vals or nulls?
                # df.fillna("None", inplace=True)
        
                # MUST settr otherwise any modification not done in-place will be ignored
                setattr(self, f, df)

            except Exception as ex:
                L.error(f"Error cleaning all files: {f}. Ex: {ex}")
                raise Exception(f"Cannot data processing - please fixe errors {ex}")

        

        # checking for missing foreign keys
        self.fk_checks()

    def fk_checks(self):
        L.info(f"fk_checks.... ")

        checks = self.cf.fk_checks
        if checks:
            for check in checks:
                for fk, target in check.items():
                    try:
                        fk_filename, fk_name = fk.split(sep=".")
                        target_file, target_name = target.split(sep=".")
                        fk_file = getattr(self, fk_filename)
                        L.info(f"FK_CHECK: SOURCE:{fk_filename}, TARGET:{target_file}, FIELD:{fk_name}")

                        # get the panda columns
                        fk_col = getattr(self, fk_filename)[fk_name]
                        target_col = getattr(self, target_file)[target_name]

                        # apply, leave fk value if fk in target_col, fk = 0 otherwise
                        # assign that corrected col of values to fk_file.fk_name column
                        # fk_file[fk_name] = fk_file[fk_name].astype(int).apply(lambda x: x if x in target_col.values else 0)
                        fk_file[fk_name] = fk_file[fk_name].apply(lambda x: x if x in target_col.values else 0)
                        fk_file[fk_name].fillna(0, inplace=True)
                        # ans = fk_col.apply(lambda x: x if x in target_col.values else 0)
                        # fk_file[fk_name] = ans
                        L.info(f"fk table: {fk_filename}, fkname: {fk_name}, target table: {target_file}, targetname: {target_name},  ")
                    except Exception as ex:
                        L.error(f"################## ########################")
                        L.error(f"################## ########################")
                        L.error(f"################## ########################")
                        L.error(f"FK check failed / exception during fk check.")
                        L.error(f"Exc: {ex}")

    def clean_dates(self, df, filename):
        """ cleans/formats dates properly"""
        L.info(f"Cleaning dates for {filename}")
        # get the fieldnames (cols) that are dates
        datefields = self.cf.get_date_fields(filename)
        # slice the df to work on those cols
        datecols = df.loc[:,datefields]
        # format in the output expected by django fixtures imports - parse it to a pd datetime,
        for col in datecols:
            try:
                # need to replace empty fields with None, otherwise later in django fixtures we get '' that it doesn't want to import
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce").dt.date
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="ignore").dt.date
                df.update(df.loc[:, col].fillna('None', inplace=True))
                # df[col] = pd.to_datetime(df[col], infer_datetime_format=True).dt.date
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

    def replace_value_in_cols(self, df, configs):
        """ for some fields such as fk_, we have 0s as values where really we'd rather have just no
            value (so that no fk at all is set). Configs is just a subset of the configs, e.g. what was
            set under pretreatments:
                        - <funcname>:
                            <configs>

            Assumes it's the same value to be replaced in all the columns
        """
        L.info(f"Replacing values in cols: {configs}")
        cols = configs["columns"]
        to_replace = configs["to_replace"]
        value = configs["value"]
        df.update(df.loc[:, cols].replace(to_replace=to_replace, value=value))
        return df

    def fill_nan_values(self, df, configs):
        """ fills the nan values 
        """
        L.info(f"Fill nan values in cols: {configs}")
        cols = configs["columns"]
        value = configs["value"]
        df.update(df.loc[:, cols].fillna(value))
        return df

    def insert_pk_0(self, df, configs):
        """ adds a row which is a copy of whatever the 1st row is and puts a pk=0 so we can easily reference """
        L.info(f"Insering pk_0: {configs}")

        # select the first row of the dataframe
        row = df.iloc[0,:]
        df = df.append(row, ignore_index=True)
        pk_name = configs["pk_colname"]
        pk_value = configs["pk_value"]
        # change the pk_col value to 0
        df.iloc[-1, df.columns.get_loc(pk_name)] = pk_value
        L.info(f"df.shape: {df.shape}")
        df.sort_values(pk_name, inplace=True)

        return df