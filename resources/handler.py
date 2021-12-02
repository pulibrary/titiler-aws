"""AWS Lambda handler."""
import logging
import middleware
from mangum import Mangum
from titiler.application.main import app

# Add middleware to set host header
app.add_middleware(middleware.HostMiddleware)

logging.getLogger("mangum.lifespan").setLevel(logging.ERROR)
logging.getLogger("mangum.http").setLevel(logging.ERROR)

handler = Mangum(app, lifespan="auto", log_level="error")
