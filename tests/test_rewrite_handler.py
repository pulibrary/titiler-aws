import pytest

from urllib3_mock import Responses
from resources.rewrite_handler_production import handler as handler_production
from resources.rewrite_handler_staging import handler as handler_staging

responses = Responses('urllib3')

@responses.activate
def test_rewrites_mosaic_id_production():
    responses.add('GET', '/resources/banana',
            body='{"uri": "s3://figgy-geo-production/ba/na/na/banana/mosaic-34.json"}',
            status=200,
            content_type='application/json')
    event = {'Records': [{'cf': {'request': {'uri': 'https://test.com/mosaicjson', 'querystring': 'id=banana'}}}]}
    output = handler_production(event, {})
    assert output['querystring'] == 'url=s3%3A%2F%2Ffiggy-geo-production%2Fba%2Fna%2Fna%2Fbanana%2Fmosaic-34.json'

# Don't re-process URL if one is given.
def test_keeps_existing_uri_production():
    event = {'Records': [{'cf': {'request': {'uri':
      'https://test.com/mosaicjson', 'querystring': 'id=banana&url=test' }}}]}
    output = handler_production(event, {})
    assert output['querystring'] == 'id=banana&url=test'

# Don't re-process URL if one is given.
def test_keeps_existing_uri_staging():
    event = {'Records': [{'cf': {'request': {'uri':
      'https://test.com/mosaicjson', 'querystring': 'id=banana&url=test' }}}]}
    output = handler_staging(event, {})
    assert output['querystring'] == 'id=banana&url=test'

def test_rewrites_cog_id_production():
    event = {'Records': [{'cf': {'request': {'uri': 'https://test.com/cog', 'querystring': 'id=banana'}}}]}
    output = handler_production(event, {})
    assert output['querystring'] == 'url=s3%3A%2F%2Ffiggy-geo-production%2Fba%2Fna%2Fna%2Fbanana%2Fdisplay_raster.tif'

@responses.activate
def test_rewrites_mosaic_id_staging():
    responses.add('GET', '/resources/banana',
            body='{"uri": "s3://figgy-geo-staging/ba/na/na/banana/mosaic-34.json"}',
            status=200,
            content_type='application/json')
    event = {'Records': [{'cf': {'request': {'uri': 'https://test.com/mosaicjson', 'querystring': 'id=banana'}}}]}
    output = handler_staging(event, {})
    assert output['querystring'] == 'url=s3%3A%2F%2Ffiggy-geo-staging%2Fba%2Fna%2Fna%2Fbanana%2Fmosaic-34.json'

def test_rewrites_cog_id_staging():
    event = {'Records': [{'cf': {'request': {'uri': 'https://test.com/cog', 'querystring': 'id=banana'}}}]}
    output = handler_production(event, {})
    assert output['querystring'] == 'url=s3%3A%2F%2Ffiggy-geo-production%2Fba%2Fna%2Fna%2Fbanana%2Fdisplay_raster.tif'
