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

# Add route for resource info lookup
# Used in rewrite_handler to fetch mosaic.json URL from a resource id
@app.get("/resources/{resource_id}")
def resource_info(resource_id: str, response: Response):
    # Set TTL of respone to 10 minutues.
    # Adding a Cache-Control: max-age directive overrides the default Cloudfront TTL
    # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Expiration.html#ExpirationDownloadDist
    response.headers["Cache-Control"] = "max-age=600"
    return fetch_data(resource_id)

def fetch_data(resource_id):
    http = urllib3.PoolManager()
    resp = http.request('GET', figgy_uri(resource_id))
    return json.loads(resp.data.decode('utf8'))

def figgy_uri(figgy_id):
    return f"https://figgy-staging.princeton.edu/concern/raster_resources/{figgy_id}/mosaic.json"

handler = Mangum(app, lifespan="auto", log_level="error")
