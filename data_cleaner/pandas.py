""" contains all the pandas-related code for now """

import pandas as pd
import logging
import sys
from .treatments import *
log = logging.getLogger("default")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)
# load entfacs
file_name = "produit.xlsx"
prod_old = "produit_old.xlsx"


log.info(f"loading old producs... ")
oldprod = pd.read_excel(f"./inputs/{prod_old}", header=0)
oldcols = oldprod.columns

xlsx_df = pd.read_excel(f"./inputs/{file_name}", header=0, usecols=oldcols)
log.info(f"{file_name} has been read: {xlsx_df.columns}")
# zfac = pd.read_excel("./inputs/zfacture.xlsx", header=0)
# log.info(f"zfac has been read: {zfac.columns}")
xlsx_df = cleanup_spaces(xlsx_df)

# write the fie to excel
xlsx_df.to_excel("produits_new.xlsx")
xlsx_df.to_csv("produits_new.csv", index=False)
