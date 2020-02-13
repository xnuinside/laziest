__version__ = "0.0.3"

import astor as a

a.dump_tree(a.parse_file('/Users/jvolkova/laziest/laziest/test.py'))