# lib
import uvicorn

# local
from .app import app

# routers
from .members import *
from .server_stats import *

uvicorn.run(app, host="0.0.0.0", port=8080)
