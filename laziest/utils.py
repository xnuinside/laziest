from logging import getLogger
from typing import Text

logger = getLogger(__name__)


pytest_needed = False

def map_types(_type):
    if _type == Text or _type == str :
        return 'str'
    else:
        return 'need_to_define'
