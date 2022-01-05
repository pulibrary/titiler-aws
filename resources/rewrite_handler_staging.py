from urllib.parse import parse_qs, urlencode
import urllib3
import json

# This is a viewer request function that rewrites id parameters to url parameters.
# Examples:
#   https://map-tiles-staging.princeton.edu/mosaicjson?id=1234567 ->
#   https://map-tiles-staging.princeton.edu/mosaicjson?url=s3://figgy-geo-staging/12/34/56/1234567/mosaic.json
#
#   https://map-tiles-staging.princeton.edu/cog?id=1234567 ->
#   https://map-tiles-staging.princeton.edu/cog?url=s3://figgy-geo-staging/12/34/56/1234567/display_raster.tif
def handler(event, context):
    request = event['Records'][0]['cf']['request']
    params = {k : v[0] for k, v in parse_qs(request['querystring']).items()}

    if ('id' in params and 'url' not in params):
            s3_root = "s3://figgy-geo-staging"

            if ('mosaicjson' in request['uri']):
                # Strategy - if it's Mosaic URL, then fetch S3 URL from
                # https://figgy.princeton.edu/concern/raster_resources/<id>/mosaic.json,
                # parse JSON and get URI parameter.
                item_id = params['id']
                item_url = figgy_s3_url(item_id)
            else:
                file_name = 'display_raster.tif'
                item_id = params['id']
                item_url = f"{s3_root}/{item_id[0:2]}/{item_id[2:4]}/{item_id[4:6]}/{item_id}/{file_name}"


            # Replace id param with url param
            params['url'] = item_url
            params.pop('id')
            request['querystring'] = urlencode(params)

    return request

def figgy_uri(figgy_id):
    return f"https://figgy-staging.princeton.edu/concern/raster_resources/{figgy_id}/mosaic.json"

def figgy_s3_url(figgy_id):
    http = urllib3.PoolManager()
    resp = http.request('GET', figgy_uri(figgy_id))
    return json.loads(resp.data.decode('utf8'))["uri"]
