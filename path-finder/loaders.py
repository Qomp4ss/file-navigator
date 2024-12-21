from abc_loader import BaseLoader
import pandas as pd

PDLoader = BaseLoader({pd.read_csv: ['.csv', '.txt'],
                       pd.read_excel: ['.xlsx', '.xls'],
                       pd.read_feather: '.feather',
                       pd.read_hdf:['.h5', '.hdf5'],
                       pd.read_json: '.json',
                       pd.read_parquet:'.gzip',
                       pd.read_pickle: '.pkl',
                       pd.read_sas: '.sas7bdat',
                       pd.read_stata: '.dta',
                       pd.read_html: '.html'})