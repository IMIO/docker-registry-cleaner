#!/usr/bin/env python
import requests
import argparse
import json
import sys
import datetime
import re


def get_args():
    parser = argparse.ArgumentParser(description='Docker registry cleaner')
    parser.add_argument("registry",
                        help="the registry")
    parser.add_argument("image", nargs='?',
                        help="Image")
    parser.add_argument("tags", nargs='*',
                        help="tags")
    return parser.parse_args()


def get_older_than(days=90):
    return datetime.date.today()-datetime.timedelta(days)


def is_outdated(tag, older_than):
    date = tag[:8]
    return datetime.datetime.strptime(date, '%Y%m%d').date() < days


def is_valid(tag):
    # return True if the tag correspond to our format YYYYMMDD-version
    return re.match('\d{8}-\d+', tag)


args = get_args()
if len(sys.argv) == 2:
    url = 'https://{}/v2/_catalog'.format(args.registry)
    r = requests.get(url)
    if r.status_code:
        print('\n'.join(json.loads(r.text)['repositories']))
    else:
        print('No images found')
elif len(sys.argv) == 3:
    url = 'https://{}/v2/{}/tags/list'.format(args.registry, args.image)
    r = requests.get(url)
    try:
        tags = json.loads(r.text)['tags']
    except KeyError:
        tags = []
    if tags:
        tags.sort()
        days = get_older_than()
        invalid_tags = []
        outdated_tags = []
        ok_tags = []
        for tag in tags:
            if is_valid(tag):
                if is_outdated(tag, days):
                    outdated_tags.append(tag)
                else:
                    ok_tags.append(tag)
            else:
                invalid_tags.append(tag)
        if outdated_tags:
            print("OUTDATED:\n{}".format(' '.join(outdated_tags)))
        if invalid_tags:
            print("INVALIDS:\n{}".format(' '.join(invalid_tags)))
        if ok_tags:
            print("OK:\n{}".format(' '.join(ok_tags)))
    else:
        print("No tags found")
else:
    for tag in args.tags:
        url = 'https://{}/v2/{}/manifests/{}'.format(
                args.registry,
                args.image,
                tag)
        r = requests.head(url)
        if r.status_code == 200 and r.headers['Docker-Content-Digest']:
            digest = r.headers['Docker-Content-Digest']
            url = 'https://{}/v2/{}/manifests/{}'.format(
                    args.registry,
                    args.image,
                    digest)
            headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
            r = requests.request('DELETE', url, headers=headers)
            if r.status_code == 202:
                print('Delete OK for {}/{}:{}'.format(
                    args.registry,
                    args.image,
                    tag))
        else:
            print('Cannot retrieve Docker-Content-Digest for {}/{}:{}'.format(
                  args.registry,
                  args.image,
                  tag))
            print('Status: ', r.status_code)
            print(r.headers)
