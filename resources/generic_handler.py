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
              if ('mosaicjson' in request['uri'] or 'cog' in request['uri']):
                  # Strategy - fetch S3 URL from
                  # https://figgy.princeton.edu/concern/raster_resources/<id>/mosaic.json,
                  # parse JSON and get URI parameter.
                  item_id = params['id']
                  item_url = self.s3_url(item_id)

              # Replace id param with url param
              params['url'] = item_url
              params.pop('id')

      # Add rescale parameter to ensure tile images are rendered correctly
      if ('rescale' not in params):
          params['rescale'] = '0,255'

      request['querystring'] = urlencode(params)
      return request

    def resource_uri(self, resource_id):
        if self.stage == "production":
            return f"https://figgy.princeton.edu/tilemetadata/{resource_id}"
        else:
            return f"https://figgy-staging.princeton.edu/tilemetadata/{resource_id}"

    def s3_url(self, resource_id):
        http = urllib3.PoolManager()
        resp = http.request('GET', self.resource_uri(resource_id))
        return json.loads(resp.data.decode('utf8'))["uri"]
