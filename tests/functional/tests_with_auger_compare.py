import auger
import sys
sys.path.append("/Users/jvolkova/laziest/tests/functional")

import functions_with_args

with auger.magic([functions_with_args]):
    functions_with_args