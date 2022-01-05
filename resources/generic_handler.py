from urllib.parse import parse_qs, urlencode
import urllib3
import json

class GenericHandler:
    def __init__(self, stage):
        self.stage = stage

    def s3_root(self):
        if self.stage == "production":
            return "s3://figgy-geo-production"
        else:
            return "s3://figgy-geo-staging"

    def handle(self, event, context):
      request = event['Records'][0]['cf']['request']
      params = {k : v[0] for k, v in parse_qs(request['querystring']).items()}

      if ('id' in params and 'url' not in params):

              if ('mosaicjson' in request['uri']):
                  # Strategy - if it's Mosaic URL, then fetch S3 URL from
                  # https://map-tiles.princeton.edu/resources/<id>,
                  # which caches data from
                  # https://figgy.princeton.edu/concern/raster_resources/<id>/mosaic.json,
                  # parse JSON and get URI parameter.
                  item_id = params['id']
                  item_url = self.s3_url(item_id)
              else:
                  file_name = 'display_raster.tif'
                  item_id = params['id']
                  item_url = f"{self.s3_root()}/{item_id[0:2]}/{item_id[2:4]}/{item_id[4:6]}/{item_id}/{file_name}"


              # Replace id param with url param
              params['url'] = item_url
              params.pop('id')
              request['querystring'] = urlencode(params)

      return request

    def resource_uri(self, resource_id):
        if self.stage == "production":
            return f"https://map-tiles.princeton.edu/resources/{resource_id}"
        else:
            return f"https://map-tiles-staging.princeton.edu/resources/{resource_id}"

    def s3_url(self, resource_id):
        http = urllib3.PoolManager()
        resp = http.request('GET', self.resource_uri(resource_id))
        return json.loads(resp.data.decode('utf8'))["uri"]
