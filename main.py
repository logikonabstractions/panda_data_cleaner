from data_cleaner.Programs import MergeData, CleanData
from utils.utils import *
from classes.arg_parser import ArgParser
from utils.logger import get_root_logger



class MainProgram:
    """ the runner of the simulation
        TODO: add a reset to return to start/default state of some kind
     """
    def __init__(self, arg_parser=None, logger=None):
        # those arguments may be set from the config file
        self.inputs_folder            = None
        self.outputs_folder           = None
        self.files_to_read              = []

        self.LOG            = logger if logger else self.get_logger()
        self.arg_parser     = arg_parser if arg_parser else ArgParser(self.LOG)
        self.configs   = None
        self.prog_name = None
        self.prog       = None
        self.init_args()

        # init program
        # self.data_man = DataManager(self.configs)

        self.LOG.info(f"Current mode {self.mode}.")
        self.LOG.info(f"Configs for current mode {self.configs}.")
        self.LOG.info(f"Done init in {self.__class__.__name__}.")

    def run(self):
        """ run whatever the program is """
        L.info(f"Running program {self.prog_name}")
        self.prog.run()
        # self.data_man.read_files()
        # self.data_man.clean_all_files()
        # self.data_man.files_to_csv()


    def init_args(self):
        """ parses whatever args we have & sets up this class accordingly
            attribute must already be declared in the class - otherwise they are ignored
        """
        self.arg_parser.parse_cmdline()
        self.configs = self.arg_parser.parse_yaml_configs()
        for k, v in self.configs[self.mode].items():
            if hasattr(self, k):
                setattr(self, k, v)
                self.LOG.info(f"Attribute {k} has been set to {getattr(self, k)}")
            else:
                self.LOG.warning(f"Config file contains an attribute that is not in this class's attribute and therefore has not been set (k,v): {k}, {v}")

        if self.mode != "default":                  # then those will complement/override the default values
            for k, v in self.configs[self.mode]["main_program"].items():
                if hasattr(self, k):
                    setattr(self, k, v)
                    self.LOG.info(f"Attribute {k} has been set to {getattr(self, k)}, overriding default values if any.")
                else:
                    self.LOG.warning(f"Config file contains an attribute that is not in this class's attribute and therefore has not been set (k,v): {k}, {v}")

        # then pass it to the wrapper for convenience
        self.configs = Configs(self.configs[self.mode])

        # set the program class onwhich to call run()
        if self.args.prog_name == "merge":
            self.prog = MergeData(self.configs)
        else:                                           # defaul - clean the data
            self.prog = CleanData(self.configs)


    @property
    def mode(self):
        """ the config mode we want. defaults is set by argparser at default"""
        return self.args.mode

    @property
    def args(self):
        return self.arg_parser.args




    def get_logger(self):
        """ inits the logs. should only be if for whatever reason no logger has been defined """
        logger = get_root_logger(BASE_LOGGER_NAME, filename=f'log.log')
        logger.info(f"Initated logger in {self.__class__.__name__} ")
        logger.debug(f'logger debug level msg ')
        logger.info(f'logger info level msg ')
        logger.warning(f'logger warn level msg ')
        logger.error(f'logger error level msg ')
        logger.critical(f'logger critical level msg ')
        return logger

if __name__ == '__main__':
    mp = MainProgram()
    mp.run()
