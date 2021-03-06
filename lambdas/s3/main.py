from pymemcache.client.base import Client
import logging
import argparse
import urllib2
import urllib
import json
import base64
import boto3

API_BASE = 'https://dashboard.cash4code.net/score'
client = Client(('doesntmattertome.nfzrko.cfg.euc1.cache.amazonaws.com', 11211))
s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return process_message(json.loads(response['Body']))
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

def get_message(msg_id):
    parts = client.get(msg_id)
    if parts is None:
        return [None, None]
    return json.loads(parts)

def save_message(msg_id, parts):
    client.set(msg_id, json.dumps(parts))

def process_message(msg):
    """
    processes the messages by combining and appending the kind code
    """
    msg_id = msg['Id'] # The unique ID for this message
    part_number = msg['PartNumber'] # Which part of the message it is
    data = msg['Data'] # The data of the message

    # Try to get the parts of the message from the MESSAGES dictionary.
    # If it's not there, create one that has None in both parts
    # parts = MESSAGES.get(msg_id, [None, None])
    parts = get_message(msg_id)

    if None not in parts:
        print "Duplicated request, ignoring"
        return "OK"

    # store this part of the message in the correct part of the list
    parts[part_number] = data

    # store the parts in MESSAGES
    # MESSAGES[msg_id] = parts
    save_message(msg_id, parts)

    # if both parts are filled, the message is complete
    if None not in parts:
        # app.logger.debug("got a complete message for %s" % msg_id)
        print "have both parts"
        # We can build the final message.
        result = parts[0] + parts[1]
        # sending the response to the score calculator
        # format:
        #   url -> api_base/jFgwN4GvTB1D2QiQsQ8GHwQUbbIJBS6r7ko9RVthXCJqAiobMsLRmsuwZRQTlOEW
        #   headers -> x-gameday-token = API_token
        #   data -> EaXA2G8cVTj1LGuRgv8ZhaGMLpJN2IKBwC5eYzAPNlJwkN4Qu1DIaI3H1zyUdf1H5NITR
        url = API_BASE + '/' + msg_id
        print url
        print result
        req = urllib2.Request(url, data=result, headers={'x-gameday-token':'cd4f1809dc'})
        resp = urllib2.urlopen(req)
        resp.close()

    return 'OK'