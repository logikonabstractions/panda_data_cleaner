from .DataManager import DataManager
import pandas as pd
from utils.logger import get_root_logger
L = get_root_logger("engine_logger")

class Program:
    def run(self):
        raise NotImplemented

class CleanData:
    def __init__(self, configs):
        # init DataManager
        self.cf = configs
        self.data_man = DataManager(configs)
        self.merged_files = None

    def run(self):
        """ run whatever the program is """
        L.info(f"Running CleanData program... ")
        self.data_man.read_files()
        self.data_man.clean_all_files()
        self.data_man.files_to_csv()

class MergeData:
    def __init__(self, configs):
        # init DataManager
        self.cf = configs
        self.data_man = DataManager(configs)

    def run(self):
        """ run whatever the program is """
        L.info(f"Running MergeData program.... ")
        self.data_man.read_files()
        self.merge_files_on_columns()

    def merge_files_on_columns(self):
        """ takes the files to merge & merges them toghether """
        for key, merge_def in self.cf.merges.items():
            L.info(f"Treating merge def: {merge_def}")
            f1, f2 = merge_def["files"]
            output_name = merge_def["output_name"]
            pk_name = merge_def["pk_name"]

            df1 = getattr(self.data_man, f1)
            df2 = getattr(self.data_man, f2)
            df1_rows = df1.shape[0]
            df2_rows = df2.shape[0]
            L.info(f"Finished reading {df1.columns}, {df2.columns}")
            if self.check_columns_matche(df1, df2):
                L.info(f"Columns match in both files... ")
                merged_file = df1.append(df2)

                # drop any pk_ent duplicated in the result
                L.info(f"Dropping any pk_na values merged file... (currently {merged_file.shape[0]} rows)")
                merged_file.dropna(axis=0, inplace=True, subset=[pk_name])
                L.info(f"Removing duplicate pk_ent from merged file...  (currently {merged_file.shape[0]} rows)")
                merged_file.drop_duplicates(inplace=True, subset=[pk_name])
                merged_file.sort_values(pk_name, inplace=True)
                self.data_man.merged_files = merged_file
                L.info(f"Merged file stored in data_man.merged_files attr with {df1.shape[0]} + {df2.shape[0]} = {merged_file.shape[0]} rows")
                L.info(f"Resulting file: ")
                L.info(f"\n{merged_file}")
                self.write_merged_file(filename=output_name)
            else:
                raise Exception(f"Columns of files to merge don't matche, aborting: {df1.columns}, {df2.columns}")

    def check_columns_matche(self, df1, df2):
        """ checks that col matches in files to merge .
            For now, we just check that all the columns have same name in the same order
         """

        return all(df1.columns == df2.columns)


    def write_merged_file(self, filename):
        """ writes the merged file in  new xlsx """
        L.info("Writing xlsx file... this may take a few moements for large files.... ")
        self.data_man.file_to_excel(self.data_man.merged_files, filename=filename)