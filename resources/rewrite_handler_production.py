from generic_handler import GenericHandler

# This is a viewer request function that rewrites id parameters to url parameters.
# Examples:
#   https://map-tiles.princeton.edu/mosaicjson?id=1234567 ->
#   https://map-tiles.princeton.edu/mosaicjson?url=s3://figgy-geo-production/12/34/56/1234567/mosaic.json
#
#   https://map-tiles.princeton.edu/cog?id=1234567 ->
#   https://map-tiles.princeton.edu/cog?url=s3://figgy-geo-production/12/34/56/1234567/display_raster.tif
def handler(event, context):
    handler = GenericHandler("production")
    return handler.handle(event, context)
