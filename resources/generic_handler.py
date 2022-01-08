from urllib.parse import parse_qs, urlencode
import urllib3
import json


class GenericHandler:
    def __init__(self, stage):
        self.stage = stage
        self.item_id = ""

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
                  self.item_id = params['id']
                  item_url = self.resource_uri()
              else:
                  file_name = 'display_raster.tif'
                  self.item_id = params['id']
                  item_url = f"{self.s3_root()}/{self.item_id[0:2]}/{self.item_id[2:4]}/{self.item_id[4:6]}/{self.item_id}/{file_name}"


              # Replace id param with url param
              params['url'] = item_url
              params.pop('id')
              request['querystring'] = urlencode(params)

      return request

    def resource_uri(self):
        if self.stage == "production":
            return f"https://map-tiles.princeton.edu/resources/{self.item_id}"
        else:
            return f"https://map-tiles-staging.princeton.edu/resources/{self.item_id}"
