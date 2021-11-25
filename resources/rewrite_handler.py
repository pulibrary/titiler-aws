from urllib.parse import urlparse, unquote, quote_plus
from pathlib import PurePosixPath

# This is a viewer request function
def handler(event, context):
    request = event['Records'][0]['cf']['request']

    url = urlparse(request['uri'])
    path = PurePosixPath(unquote(url.path)).parts
    action = path[2]
    s3_access = 'public'
    s3_root = 's3://pul-tile-images/'
    s3_basepath = f'/{path[1][0:2]}/{path[1][2:4]}/{path[1][4:6]}/{path[1]}/'
    if action == 'mosaicjson':
        file_name = 'mosaic.json'
    else:
        file_name = 'display_raster.tif'

    s3_path = s3_root + s3_access + s3_basepath + file_name
    qs= 'url=' + quote_plus(s3_path)

    # Process path
    path = list(path)
    path.pop(0)
    path.pop(0)

    request['uri'] = url._replace(path='/' + '/'.join(path))
    if 'querystring' in request:
        request['querystring'] = request['querystring'] + '&' + qs
    else:
        request['querystring'] =  qs
    print(request['uri'])
    print(request['querystring'])

    return request
