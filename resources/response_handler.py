import json

CONTENT = """
<\!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Simple Lambda@Edge Static Content Response</title>
</head>
<body>
    <p>Hello from Lambda@Edge!</p>
</body>
</html>
"""

# This is an origin response function
def handler(event, context):
    response = {
        'status': '200',
        'statusDescription': 'OK',
        'headers': {
            'cache-control': [
                {
                    'key': 'Cache-Control',
                    'value': 'max-age=100'
                }
            ],
            "content-type": [
                {
                    'key': 'Content-Type',
                    'value': 'text/html'
                }
            ]
        },
        'body': CONTENT
    }
    return response

    # request = event['Records'][0]['cf']['request']
    # response = event['Records'][0]['cf']['response']
    #
    # if not ('WMTSCapabilities' in request['uri']):
    #     return response
    # #
    # # domain = event['Records'][0]['cf']['config']['distributionDomainName']
    # # url = 'https://' + domain
    # # response['body'] = re.sub('http(.*?)amazonaws\.com', url, response['body'])
    # #
    # # return response
    #
    # uri = "Request uri: " + request['uri']
    # domain = "Distribution domain: " + event['Records'][0]['cf']['config']['distributionDomainName']
    # url = 'Processed url: https://' + domain
    # not_updated_body = "Original body: " + response['body']
    # updated_body = 'Updated body: ' + re.sub('http(.*?)amazonaws\.com', url, response['body'])
    #
    # text = uri + '\n' + domain + '\n' + url + '\n' + not_updated_body + '\n' + updated_body
    #
    # response = {
    #         'status': '200',
    #         'body': text
    #     }
    # return response
