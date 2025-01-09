import unittest
from file_navigator import PathFinder
from pathlib import Path
from unittest.mock import patch
from itertools import chain

class TestPathFinder(unittest.TestCase):
    
    def test_empty_init(self):
        self.assertIsInstance(PathFinder(), PathFinder)

    def test_init_good_arg(self):
        arg1 = {r"C:\\": 1}
        arg2 = {r"C:\\": 0}
        arg3 = {r"C:\\": True}
        arg4 = {r"C:\\": False}
        
        args = (arg1, arg2, arg3, arg4)
        
        for arg in args:
            self.subTest(arg = arg)
            self.assertIsInstance(PathFinder(arg), PathFinder)

    @unittest.expectedFailure
    def test_init_bad_arg_1(self):
        arg = [1, "2"]
        
        self.assertIsInstance(PathFinder(arg), PathFinder)

    @unittest.expectedFailure
    def test_init_bad_arg_2(self):
        arg =  {1: True}
        
        self.assertIsInstance(PathFinder(arg), PathFinder)

    @unittest.expectedFailure
    def test_init_bad_arg_3(self):
        arg = {r"C:\\": 12}
        
        self.assertIsInstance(PathFinder(arg), PathFinder)

    @unittest.expectedFailure
    def test_init_bad_arg_4(self):
        arg = {r"C:\\": "True"}

        
        self.assertIsInstance(PathFinder(arg), PathFinder)


    @unittest.expectedFailure
    def test_init_bad_arg_5(self):
        arg = {r"ABC": False}
        
        self.assertIsInstance(PathFinder(arg), PathFinder)
        
    @unittest.expectedFailure
    def test_init_bad_arg_6(self):
        arg = {r"ABC": None}
        
        self.assertIsInstance(PathFinder(arg), PathFinder)
        
    @patch('file_navigator.pathfinder.os.path.isdir')  
    def test_add_dirs(self, mock_isdir):
        directories =  {"/folder1": True,
                        "/folder2/subfolderA": False,
                        "/folder3/subfolderB/subsubfolderC": True}
        
        mock_isdir.side_effect = lambda path: True if path in directories else False
        pf = PathFinder()
        pf.add_dirs(directories)
        self.assertEqual(directories, pf.directories)
    
    @patch('file_navigator.pathfinder.os.path.isdir')     
    def test_add_dirs_bad_arg(self, mock_isdir):
        
        directories = ['/root/subfolder1', '/root/subfolder2',
                       '/root/subfolder3', '/root']
        
        arg1 = ({"/root/subfolder1": False,
                "/root/subfolder2": True,
                "/root/subfolder3": False},
                {"/root": True},)
        
        arg2= ({"/root": True},
                {"/root/subfolder3": False})

        

        args = (arg1, arg2)
        mock_isdir.side_effect = lambda path: True if path in directories else False
        
        for arg in args:
            with self.subTest(arg = arg):
                pf = pf = PathFinder(arg[0])
                with self.assertRaises(ValueError):
                    pf.add_dirs(arg[1])
        

    @patch('file_navigator.pathfinder.os.path.isdir')     
    def test_del_dirs_iterable_arg(self, mock_isdir):
        directories =  {"/folder1": True,
                        "/folder2/subfolderA": False,
                        "/folder3/subfolderB/subsubfolderC": True}
        
        expected = {"/folder2/subfolderA": False,
                    "/folder3/subfolderB/subsubfolderC": True}
        
        pf = PathFinder()
        pf.add_dirs(directories)
        pf.del_dirs(["/folder1"])
        
        
        self.assertEqual(expected, pf.directories)

    @patch('file_navigator.pathfinder.os.path.isdir')     
    def test_del_dirs_bad_arg(self, mock_isdir):
        directories =  {"/folder1": True,
                        "/folder2/subfolderA": False,
                        "/folder3/subfolderB/subsubfolderC": True}        
        pf = PathFinder()
        pf.add_dirs(directories)
        self.assertRaises(KeyError, pf.del_dirs, '/folder4')

    @patch('file_navigator.pathfinder.os.path.isdir')        
    def test_find_arg_validation(self, mock_isdir):
        directory = r"C:\mock_directory"
        mock_isdir.side_effect = lambda path: True if path == directory else False
        pf = PathFinder({directory: False})
        
        args = [
            (1, 'x'),
            ('*', 2,),
            ('H1', 'c', 3, 'isin'),
            ('H1', 'c', 'abcd', 'isin'),
            ('eurgbp|gbpeur|EURGBP_H4', 'txt|csv', 'regex', 'abcd')
            ]
        expected = {
           (1, 'x'): TypeError,
            ('*', 2,):TypeError,
            ('H1', 'c', 3, 'isin'): TypeError,
            ('H1', 'c', 'abcd', 'isin'): ValueError,
            ('eurgbp|gbpeur|EURGBP_H4', 'txt|csv', 'regex', 'abcd'): ValueError
                }


        for arg in args:
            with self.subTest(arg = arg):
                with self.assertRaises(expected[arg]):
                    pf.find(*arg)

    @patch('file_navigator.pathfinder.os.walk')
    @patch('file_navigator.pathfinder.os.path.isdir')
    @patch('file_navigator.pathfinder.os.path.isfile')
    def test_find_nested_dir(self, mock_isfile, mock_isdir, mock_walk):
        directory = r"C:\mock_directory"
        mock_isdir.side_effect = lambda path: True if path == directory else False
        
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

            
        mock_walk.return_value = sorted([
            [directory, ['EUR', 'CURR'], [f]]  if 'xlsx' in f 
            else ['\\'.join([directory, 'EUR']), [], [f]] if 'csv' in f 
            else ['\\'.join([directory, 'CURR']), [], [f]] 
            for f in mock_files
            ])
        mock_isfile.side_effect = lambda path: True if path.split('\\')[-1] in mock_files else False
        
        pf = PathFinder({directory: True})
        args = [
            ('.*_.*|F.*', '.x.*|.c.*', 'regex', 'regex'),
            ('*', '*', 'glob', 'glob'),
            ('H1', 'c', 'isin', 'isin'),
            ('eurgbp|gbpeur|EURGBP_H4', 'txt|csv', 'regex', 'regex'),
            ('Forex', '.xlsx', 'eq', 'eq')
            ]
        expected = {
            ('.*_.*|F.*', '.x.*|.c.*', 'regex', 'regex'): [
                'EURGBP_H4.csv', 'EURGBP_M5.csv','EURJPY_H1.csv',
                'EURJPY_M30.csv','EURUSD_M5.csv', 'Forex.xlsx'
                ],
            ('*', '*', 'glob', 'glob'): mock_files,
            ('H1', 'c', 'isin', 'isin'): ['EURJPY_H1.csv'],
            ('eurgbp|gbpeur|EURGBP_H4', 'txt|csv', 'regex', 'regex'): [
                'EURGBP_H4.csv', 'eurgbp.txt', 'gbpeur.txt'
                ],
            ('Forex', '.xlsx', 'eq', 'eq'): ['Forex.xlsx']
                }
        
        for arg in args:
            with self.subTest(arg = arg):
                result = [p[0] for p in pf.find(*arg).paths]
                self.assertCountEqual(result, expected[arg])
       

    @patch('file_navigator.pathfinder.os.scandir')
    @patch('file_navigator.pathfinder.os.path.isdir')
    @patch('file_navigator.pathfinder.os.path.isfile')
    def test_find_flat_dir(self, mock_isfile, mock_isdir, mock_scandir):
        directory = r"C:\mock_directory"
        mock_isdir.side_effect = lambda path: True if path == directory else False
        
        mock_files = ['EURGBP_H4.csv','EURGBP_M5.csv','EURJPY_H1.csv',
                      'EURJPY_M30.csv', 'EURUSD_M5.csv','Forex.xlsx',
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
        mock_scandir.return_value = mock_files
        mock_isfile.side_effect = lambda path: True if path.split('\\')[-1] in mock_files else False
        
        pf = PathFinder({directory: False})
        args = [
            ('.*_.*|F.*', '.x.*|.c.*', 'regex', 'regex'),
            ('*', '*', 'glob', 'glob'),
            ('H1', 'c', 'isin', 'isin'),
            ('eurgbp|gbpeur|EURGBP_H4', 'txt|csv', 'regex', 'regex'),
            ('Forex', '.xlsx', 'eq', 'eq')
            ]
        expected = {
            ('.*_.*|F.*', '.x.*|.c.*', 'regex', 'regex'): [
                'EURGBP_H4.csv', 'EURGBP_M5.csv','EURJPY_H1.csv',
                'EURJPY_M30.csv','EURUSD_M5.csv', 'Forex.xlsx'
                ],
            ('*', '*', 'glob', 'glob'): mock_files,
            ('H1', 'c', 'isin', 'isin'): ['EURJPY_H1.csv'],
            ('eurgbp|gbpeur|EURGBP_H4', 'txt|csv', 'regex', 'regex'): [
                'EURGBP_H4.csv', 'eurgbp.txt', 'gbpeur.txt'
                ],
            ('Forex', '.xlsx', 'eq', 'eq'): ['Forex.xlsx']
                }
        
        for arg in args:
            with self.subTest(arg = arg):
                result = [p[0] for p in pf.find(*arg).paths]
                self.assertCountEqual(result, expected[arg])
    
    def test_empty_find(self):
        pf = PathFinder()
        with self.assertRaises(ValueError):
            pf.find('Forex', '.xlsx', 'eq', 'eq')
        
    
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPathFinder('test_empty_init'))
    suite.addTest(TestPathFinder('test_init_good_arg'))
    suite.addTest(TestPathFinder('test_init_bad_arg_1'))
    suite.addTest(TestPathFinder('test_init_bad_arg_2'))
    suite.addTest(TestPathFinder('test_init_bad_arg_3'))
    suite.addTest(TestPathFinder('test_init_bad_arg_4'))
    suite.addTest(TestPathFinder('test_init_bad_arg_5'))
    suite.addTest(TestPathFinder('test_init_bad_arg_6'))
    suite.addTest(TestPathFinder('test_add_dirs'))
    suite.addTest(TestPathFinder('test_del_dirs_iterable_arg'))
    suite.addTest(TestPathFinder('test_del_dirs_bad_arg'))
    suite.addTest(TestPathFinder('test_find_arg_validation'))
    suite.addTest(TestPathFinder('test_find_nested_dir'))
    suite.addTest(TestPathFinder('test_find_flat_dir'))
    suite.addTest(TestPathFinder('test_empty_find'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
