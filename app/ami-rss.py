from logzero import logger
import logging
import logzero
from urllib.parse import urlparse
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from concurrent.futures.thread import ThreadPoolExecutor
import re
import socket
import json
import time
import signal
import os
import boto3
import uuid
from datetime import datetime
from feedgen.feed import FeedGenerator
import requests
from models import Record
import settings

requested_to_quit = False


def main():
    logger.info("starting...")

    setup_signal_handling()

    global db
    db = settings.get_database()

    while lifecycle_continues():
        lifecycle()

        if settings.SLEEP_SECONDS == 0:
            logger.info("exiting after running once, as SLEEP_SECONDS is 0.")
            exit(0)

        if lifecycle_continues():
            logger.info("sleeping for %s seconds..." % settings.SLEEP_SECONDS)
            for _ in range(settings.SLEEP_SECONDS):
                if lifecycle_continues():
                    time.sleep(1)


def lifecycle_continues():
    return not requested_to_quit


def signal_handler(signum, frame):
    logger.info("Caught signal %s" % signum)
    global requested_to_quit
    requested_to_quit = True


def setup_signal_handling():
    logger.info("setting up signal handling")
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def write_to_file_or_s3(uri, body):
    logger.debug(f"writing to file URI {uri}.xml")

    if uri.lower().startswith("s3://"):
        s3 = boto3.resource("s3")
        parse_result = urlparse(uri)
        bucket = parse_result.netloc
        key = parse_result.path.lstrip("/") + ".xml"
        logger.debug(f"s3 bucket: {bucket} key: {key}")
        s3_object = s3.Object(bucket, key)
        s3_object.put(Body=body)
        if settings.S3_SET_PUBLIC_ACL:
            logger.debug("putting s3 acl for public-read")
            object_acl = s3.ObjectAcl(bucket, key)
            object_acl.put(ACL='public-read')
    else:
        with open(f"{uri}.xml", "w") as file:
            file.write(body)


def get_now_as_timestamp():
    return datetime.now()


def lifecycle():
    global db

    logger.debug(f"getting response for {settings.REGION}")
    ssm = boto3.client("ssm")
    ssm_response = ssm.get_parameters(
        Names=[
            settings.SSM_PATH
        ],
        WithDecryption=False
    )

    logger.debug(f"ssm response: {ssm_response}")

    record = get_record_from_ssm_response(
        region=settings.REGION,
        timestamp=str(get_now_as_timestamp()),
        response=ssm_response
    )

    if record is None:
        logger.info(f"could not find a value for path {settings.SSM_PATH}")
        return

    if db.exists(record):
        logger.info("already seen this record")
        return

    db.save(record)
    announce(record.get_content())

    if len(settings.BASE_URL) > 0:
        feed_string = generate_feed(region=settings.REGION)
        logger.debug(f"feed_string: {feed_string}")
        write_to_file_or_s3(uri=f"{settings.RESULTS_FOLDER}{settings.SSM_PATH}", body=feed_string.decode("utf-8"))


def announce(message):
    logger.debug(f"announce({message})")
    if settings.ENABLE_SLACK:
        slack_announce(message)


def slack_announce(message):
    posted_message = f"{settings.SLACK_MESSAGE_PREFIX}{message}"
    logger.debug(f"slack_announce({settings.SLACK_WEBHOOK_URL}, {posted_message}")
    _ = requests.post(settings.SLACK_WEBHOOK_URL, json={"text": posted_message, "link_names": 1})


def get_record_from_ssm_response(region, timestamp, response):
    logger.debug(f"get_record_from_ssm_response({region}, ...)")
    if "Parameters" not in response or len(response["Parameters"]) != 1 or "Value" not in response["Parameters"][0]:
        logger.info("invalid response received")
        return None

    param = response["Parameters"][0]

    id = region + "_" + param["Name"] + "_" + str(param["Version"])

    record = Record(
        id=id,
        timestamp=timestamp,
        region=region,
        row=json.loads(param["Value"])
    )

    logger.debug(f"parsed record: {record.as_dict()}")
    return record


def generate_feed(region):
    global db

    logger.debug("generate_feed()")
    records = db.top()

    fg = FeedGenerator()
    fg.id(f"{settings.BASE_URL}/")
    fg.title(f"Latest AMIs for {region}")
    fg.author({"name": "AMI-RSS", "email": "ami-rss@fractos.com"})
    fg.description(f"A list of the latest AWS AMI IDs for {region}")
    fg.link(href=settings.BASE_URL)
    fg.language("en")

    for record_raw in records:
        if settings.DEBUG:
            for key in record_raw.keys():
                logger.debug(f"raw: key: {key}={record_raw[key]}")

        record = Record(row=record_raw)
        logger.debug(f"adding entry for {record.as_dict()}")
        fe = fg.add_entry()
        fe.id(f"{settings.BASE_URL}/record/{record.id}")
        fe.title(record.image_name)
        fe.content(content=record.get_content())
        # fe.link(href=result.content)

    if settings.FEED_FORMAT == "rss":
        return fg.rss_str(pretty=True)
    # else...
    return fg.atom_str(pretty=True)


if __name__ == "__main__":
    if settings.DEBUG:
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    main()
