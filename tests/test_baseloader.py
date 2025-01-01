import unittest
from fpath_finder.abc_loader import BaseLoader

def load_1(path, kwarg1 = None):
    return f"{path} called with kwargs:{kwarg1}"

def load_2(path,  kwarg2 = True):
    return f"{path} called with kwargs:{kwarg2}"
def load_3(path,  kwarg3 = True):
    return f"{path} called with kwargs:{kwarg3}"

class TestBaseLoader(unittest.TestCase):
        
    def test_empty_init(self):
        #empty
        self.assertIsInstance(BaseLoader(), BaseLoader)
        #parametrized
    def test_init_good_args(self):
        arg1 = {load_1: '.txt'}
        arg2 = {load_1: '.txt', load_2: '.json'}
        arg3 = {load_1: '.txt',
                load_2: '.json',
                load_3: ['.xml', '.html']}
        arg4 = {load_1: ['.txt'], 
                load_3: ['.xml', '.html']}
        arg5 = None

        args = (arg1, arg2, arg3, arg4, arg5)
        
        expected1 = {'.txt': load_1}
        expected2 = {'.txt': load_1, '.json': load_2}
        expected3 = {'.txt': load_1,
                     '.json': load_2,
                     '.xml':load_3,
                     '.html':load_3}
        expected4 = {'.txt': load_1,
                     '.xml':load_3,
                     '.html':load_3}
        expected5 = {}

        expected = (expected1, expected2, 
                    expected3, expected4, 
                    expected5)
        
        for i in range(len(args)):
            self.subTest(arg = args[i])
            self.assertIsInstance(BaseLoader(args[i]), BaseLoader)
            self.assertCountEqual(BaseLoader(args[i])._mapp.items(), expected[i].items())

    def test_init_bad_args(self):
        arg1 = [{load_1: '.txt'}]
        arg2 = tuple({load_1: '.txt'})
            
        args = (arg1, arg2)
        for arg in args:
            with self.subTest(arg = arg):
                with self.assertRaises(TypeError):
                    BaseLoader(arg)
                    
    def test_add_functions_bad_arg(self):
        args = [
            {'.txt': load_1},
            {load_1: {'.txt', '.csv'}},
            {load_1: ('.txt', '.csv')},
            {load_1: (1,2,3)}
            ]
        for arg in args:
            with self.subTest(arg = arg):
                with self.assertRaises(TypeError):
                    BaseLoader().add_functions(arg)
    def test_load(self):
        bl = BaseLoader({load_1:'.xlsx',
                         load_2: '.json',
                         load_3: ['.csv', '.txt']})
        mock_dir = r"C:\mock_directory"        
        mock_files = ['Forex.xlsx', 'EURGBP_H4.csv', 'audcad.txt', 'audchf.txt']

        
        mock_paths = ['\\'.join([mock_dir, f]) 
                      if 'xlsx' in f 
                      else '\\'.join(['\\'.join([mock_dir, 'CURR']),f]) if 'csv' in f 
                      else '\\'.join(['\\'.join([mock_dir, f[:3].upper()]), f])
                      for f in mock_files]
        
        args = [
           (mock_paths[0], {'kwarg1': 1, 'kwarg2':'value2', 'kwarg3': 3}),
           (mock_paths[1],  {'kwarg1': 1, 'kwarg2':'value2', 'kwarg3': 3}),
           (mock_paths[2], {'kwarg1': 1, 'kwarg2':'value2', 'kwarg3': 3}),
           (mock_paths[3], {'kwarg1': 1, 'kwarg2':'value2', 'kwarg3': 3})
           ]

        expected = {
            'C:\\mock_directory\\Forex.xlsx': "C:\\mock_directory\\Forex.xlsx called with kwargs:1",
            'C:\\mock_directory\\CURR\\EURGBP_H4.csv': "C:\\mock_directory\\CURR\\EURGBP_H4.csv called with kwargs:3",
            'C:\\mock_directory\\AUD\\audcad.txt': "C:\\mock_directory\\AUD\\audcad.txt called with kwargs:3",
            'C:\\mock_directory\\AUD\\audchf.txt': "C:\\mock_directory\\AUD\\audchf.txt called with kwargs:3"
            }
        
        for arg in args:
            with self.subTest(arg = arg):
                a,b = arg
                self.assertCountEqual(bl.load(a,**b), expected[a])
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestBaseLoader('test_empty_init'))
    suite.addTest(TestBaseLoader('test_init_good_args'))
    suite.addTest(TestBaseLoader('test_init_bad_args'))
    suite.addTest(TestBaseLoader('test_add_functions_bad_arg'))
    suite.addTest(TestBaseLoader('test_load'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())