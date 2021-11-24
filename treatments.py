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
    log.info(f"Removing extra whitespaces from merged file...")
    main_entfac.replace(to_replace='\s*$', value="", regex=True, inplace=True)
    main_entfac.replace(to_replace='^\s*', value="", regex=True, inplace=True)
    return main_entfac