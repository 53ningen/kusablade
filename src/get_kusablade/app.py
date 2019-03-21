#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from TwitterAPI import TwitterAPI
from logging import getLogger, StreamHandler, DEBUG
import boto3

import os

favorite_topic_arn = os.environ['FavoriteTopicArn']
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
sns = boto3.client('sns')

def lambda_handler(event, context):
    try:
        items = twitter.request('search/tweets', {
            'q': '草ブレード OR "草ブレ" OR 草ブレーダー',
            'count': 100,
            'tweet_mode': 'extended',
            'result_type': 'recent',
        })
    except requests.RequestException as e:
        logger.error(e)

    ids = []
    for item in items:
        ids.append(item['id_str'])

    try:
        items = twitter.request('statuses/lookup', {
            'id': ','.join(ids)
        })
    except requests.RequestException as e:
        logger.error(e)

    sum = 0
    queued = 0
    for item in items:
        sum += 1
        if not item['favorited'] and item['in_reply_to_status_id'] is None:
            j = json.dumps(item, ensure_ascii=False)
            logger.debug(j)
            res = sns.publish(
                TopicArn=favorite_topic_arn,
                Message=j,
            )
            logger.info(res)
            queued += 1
    res = {
        'sum': sum,
        'queued_count': queued,
    }
    logger.info(json.dumps(res))
    return res
