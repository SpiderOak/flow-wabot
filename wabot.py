# A simple WolframAlpha Bot for Semaphor
# Change:
# bot_name = bot semaphor username
# bot_ping = bot semaphor alias
# app_key = WolframAlpha API Key

from flow import Flow
import csv
import json
import random
import time
import wolframalpha

# Edit these three variables:
bot_name = ""
bot_ping = ""
app_key = ""
#############################

responses = "responses.csv"
client = wolframalpha.Client(app_key)
flow = Flow(bot_name)
current_time = int(round(time.time() * 1000))

with open(responses, 'r') as csvin:
    reader = csv.DictReader(csvin)
    data = {k.strip(): [v] for k, v in reader.next().items()}
    for line in reader:
        for k, v in line.items():
            k = k.strip()
            data[k].append(v)


@flow.message
def check_message(notif_type, data):
    regular_messages = data["regularMessages"]
    for message in regular_messages:
        cid = message["channelId"]
        channel = flow.get_channel(cid)
        msg_time = message["creationTime"]
        if is_it_for_me(flow.account_id(), channel, message) and msg_time > current_time:
            msg = message["text"]
            oid = channel["orgId"]
            display_name = json.loads(flow.get_user_profile(message['senderAccountId']))['displayName']
            msg_split = msg.split(' ', 1)
            # We assume that, if the bot's name is in the message, it'll be at the beginning.
            # If it is, we remove it before sending to WolframAlpha.
            if bot_ping.lower() in msg_split[0].lower():
                msg = msg_split[1]
            try:
                print msg
                res = client.query(msg)
                flow.send_message(oid, cid, "@" + display_name + ": " + next(res.results).text)
            except:
                flow.send_message(oid, cid, "@" + display_name + ": " + random_response("negative"))
        else:
            continue


def random_response(response):
    return random.choice(data[response])


def is_dm(channel):
    return len(channel['purpose']) > 0


def is_it_for_me(account_id, channel, message):
    # If it's my message, ignore it
    if message["senderAccountId"] == account_id:
        return False
    # If it's a direct message, then we care about it
    if is_dm(channel):
        return True
    # Am I highlighted?
    other_data = message['otherData']
    if len(other_data) > 0:
        # dirty way to figure out if we are being highlighted
        if account_id.lower() in other_data.lower():
            return True
    return False


# Main loop to process notifications.
print("Listening for incoming messages... (press Ctrl-C to stop)")
flow.process_notifications()
