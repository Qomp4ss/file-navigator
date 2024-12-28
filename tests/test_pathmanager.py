import unittest
from fpath_finder.pathfinder import PathManager
from pathlib import Path
from unittest.mock import patch

class TestPathManager(unittest.TestCase):
    
    def test_select_paths(self):
        mock_dir = r"C:\mock_directory"        
        mock_files = ['Forex.xlsx','EURGBP_H4.csv','EURGBP_M5.csv',
                      'EURJPY_H1.csv','EURJPY_M30.csv', 'EURUSD_M5.csv',
                      'audcad.txt','audchf.txt','audusd.txt',
                      'cadaud.txt','cadeur.txt','cadjpy.txt',
                      'cadpln.txt','cadusd.txt','chfgbp.txt',
                      'chfpln.txt','chfusd.txt','euraud.txt',
                      'eurchf.txt','eurgbp.txt','eurjpy.txt',
                      'eurpln.txt','gbpcad.txt','gbpchf.txt',
                      'gbpeur.txt','gbpjpy.txt','gbppln.txt',
                      'jpyaud.txt','jpypln.txt','nzdusd.txt',
                      'usdcad.txt','usdchf.txt','usdjpy.txt',
                      'usdpln.txt','xaggbp.txt','xauchf.txt',
                      'xaueur.txt','xaugbp.txt']

                
        mock_paths = [
            (mock_dir, f)   if 'xlsx' in f 
            else ('\\'.join([mock_dir, 'CURR']),f) if 'csv' in f 
            else ('\\'.join([mock_dir, f[:3].upper()]), f)
            for f in mock_files
            ]
        
        args = [
            ('J.*|X.*',  'regex'),
            ('*',  'glob'),
            ('N', 'isin'),
            ('XAG|NZD', 'regex'),
            (r'C:\mock_directory\CURR', 'eq')
            ]
        expected = {
            ('J.*|X.*',  'regex'): ['jpyaud.txt', 'jpypln.txt', 'xaggbp.txt',
                                    'xauchf.txt', 'xaueur.txt', 'xaugbp.txt'],
            ('*', 'glob'): mock_files,
            ('N', 'isin'): ['nzdusd.txt'],
            ('XAG|NZD', 'regex'): ['xaggbp.txt', 'nzdusd.txt'],
            (r'C:\mock_directory\CURR', 'eq'): ['EURGBP_H4.csv', 'EURGBP_M5.csv',
                                                'EURJPY_H1.csv','EURJPY_M30.csv', 
                                                'EURUSD_M5.csv']
                }
        
        for arg in args:
            with self.subTest(arg = arg):
                result = [p[0] for p in PathManager(mock_paths).select_paths(*arg).paths]
                self.assertCountEqual(result, expected[arg])

    
    def test_groupby(self):
        pass
    
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPathManager('test_select_paths'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())