import pytest

from resources.rewrite_handler_production import handler as handler_production
from resources.rewrite_handler_staging import handler as handler_staging

def test_rewrites_id_production():
    event = {'Records': [{'cf': {'request': {'uri': 'https://test.com/mosaicjson', 'querystring': 'id=banana'}}}]}
    output = handler_production(event, {})
    assert output['querystring'] == 'id=banana&url=s3%3A%2F%2Ffiggy-geo-production%2Fba%2Fna%2Fna%2Fbanana%2Fmosaic.json'

def test_rewrites_id_staging():
    event = {'Records': [{'cf': {'request': {'uri': 'https://test.com/mosaicjson', 'querystring': 'id=banana'}}}]}
    output = handler_staging(event, {})
    assert output['querystring'] == 'id=banana&url=s3%3A%2F%2Ffiggy-geo-staging%2Fba%2Fna%2Fna%2Fbanana%2Fmosaic.json'
