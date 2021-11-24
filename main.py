import pandas as pd
import logging
import sys
from treatments import *
log = logging.getLogger("default")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)
# load entfacs

log.info(f"Start!")
entfac = pd.read_excel("./inputs/entfac.xlsx", header=0)
log.info(f"entfac has been read: {entfac.columns}")
zfac = pd.read_excel("./inputs/zfacture.xlsx", header=0)
log.info(f"zfac has been read: {zfac.columns}")

f = merge_entfacs(entfac, [zfac])
# write the fie to excel
entfac.to_excel("test.xlsx")
f.to_excel("test2.xlsx")