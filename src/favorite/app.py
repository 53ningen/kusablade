#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import requests
from TwitterAPI import TwitterAPI
from logging import getLogger, StreamHandler, DEBUG

import os

twitter_account = os.environ['TwitterAccount']
consumer_key = os.environ['TwitterConsumerKey']
consumer_secret= os.environ['TwitterConsumerSecret']
access_token_key = os.environ['TwitterAccessTokenKey']
access_token_secret = os.environ['TwitterAccessTokenSecret']

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

twitter = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

def lambda_handler(event, context):
        for r in event['Records']:
            body = json.loads(r['body'])
            if body['user']['screen_name'] == twitter_account:
                continue
            status_id = body['id']
            try:
                r = twitter.request('favorites/create', {'id': status_id})
            except requests.RequestException as e:
                logger.error(e)
                raise e
            content = json.loads(r.response.content.decode())
            if r.status_code < 200 or r.status_code >= 300:
                logger.error(content)
            else:
                logger.debug(content)
        return {
            "statusCode": 200,
        }
