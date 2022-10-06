from .schedule import *
from .security import *
from .errands import *
from .easter_eggs import *
from .confession import *
from .create_vc import *
from .manage import *

from all_env import environment
if environment != "heroku":
    from .api import *

