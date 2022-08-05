"""AWS Lambda handler."""
import logging
import middleware
import urllib3
import json
from mangum import Mangum
from titiler.application.main import app
from fastapi import Response

# Add middleware to set host header
app.add_middleware(middleware.HostMiddleware)

logging.getLogger("mangum.lifespan").setLevel(logging.ERROR)
logging.getLogger("mangum.http").setLevel(logging.ERROR)

handler = Mangum(app, lifespan="auto")
