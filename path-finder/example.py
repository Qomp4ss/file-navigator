from operators import PathFinder
from loaders import PDLoader

    
pf = PathFinder({r'D:\\':True})
files = pf.find("*", ".csv|.txt|.xlsx", name_type="glob", ext_type = "regex")
scoped_files = files.select_paths("Forex", "isin").groupby("name")
eur_pln = scoped_files['eurpln'].load(PDLoader)
    