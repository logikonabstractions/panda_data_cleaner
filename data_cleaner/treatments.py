""" contains data cleaning/merging etc... for different cases """
import pandas as pd
import logging
log = logging.getLogger("default")
def merge_entfacs(main_entfac, entfacs):
    """ takes entfac xlsx & merges them:
        - removes any duplicated pk_ent
        - drops any empty rows
        - removes trailing whitespaces, long withspaces cells

        main_entfac is the dataframe returned (changes made inplace)
        entfacs is a list of entfacs that will be merged into the main one
    """

    # drop all nas
    for f in entfacs:
        log.info(f"Treating {f}")
        # merge them
        main_entfac = main_entfac.append(f)

    # drop any pk_ent duplicated in the result
    main_entfac.dropna(axis=0, inplace=True, subset=["pk_ent"])
    log.info(f"Removing duplicate pk_ent from merged file...")
    main_entfac.drop_duplicates(inplace=True, subset=["pk_ent"])

    # remove any trailing whitespace
    main_entfac = cleanup_spaces(main_entfac)
    return main_entfac

def cleanup_spaces(df):
    """ takes a dataframe & cleans up dbase's weird spaces:
        - trailing whitespaces
        - leading whitespaces
        - repeated whitespaces within text
    """
    log.info(f"Removing trailing whitespaces ...")
    df.replace(to_replace='\s*$', value="", regex=True, inplace=True)       # trailing
    log.info(f"Removing leading whitespaces ...")
    df.replace(to_replace='^\s*', value="", regex=True, inplace=True)       # leading
    log.info(f"Removing repeated whitespaces ...")
    df.replace(to_replace='\n', value=" ", regex=True, inplace=True)       # newlines
    df.replace(to_replace='\r', value=" ", regex=True, inplace=True)       # carriage returns
    df.replace(to_replace='\t', value=" ", regex=True, inplace=True)       # tabs
    df.replace(to_replace='_x000D_', value=" ", regex=True, inplace=True)    # weird placeholdesr for carriage returns
    df.replace(to_replace='\s\s+', value=" ", regex=True, inplace=True)       # remove duplicated spaces from previous stuff

    return df


def fk_in_target():
    pass