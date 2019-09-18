#!/usr/bin/env python3

# copyright (c) 2019 andreas loeffler

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import csv
import argparse
from unidecode import unidecode
import sys

umlautDictionary = {
    u'Ä': 'Ae',
    u'Ö': 'Oe',
    u'Ü': 'Ue',
    u'ä': 'ae',
    u'ö': 'oe',
    u'ü': 'ue',
    u'ß': 'ss'
}

def tr_umlaut(s):
    umap = { ord(key):str(val) for key, val in umlautDictionary.items() }
    return s.translate(umap)


parser = argparse.ArgumentParser(description='convert duv stat results to csv list suitable to upload to ultrasignup')
parser.add_argument('-e', '--event', required=True, help='DUV event ID')
parser.add_argument('-y', '--year', type=int, help='year of the event (to get runners age)')
parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbose output (-vv increase verbosity')
parser.add_argument('-d', '--debug',   action='store_true', help='Print debug output')
args = parser.parse_args()

eventid = str(args.event)
duv = 'http://statistik.d-u-v.org/getresultevent.php?event='
event_url = duv + eventid

if args.verbose:
    print("getting results for event #" + eventid + " from url: " + event_url)


# FIXME handle error
resp = 'n/a'
resp = requests.get(event_url)
soup = BeautifulSoup(resp.text, "html.parser")


# todo: figure out event "type" i.e. distance race, timed event (eg. 24h) or backyard


# note: that the duv site/table layout might change in the future
# get event year from webpage, assume forth table contains race info
# (event name, date, distance,...) try to get event year from this table
table4 = soup.findAll('table')[3]
date_row = table4.findAll('tr')[0]
date1 = date_row.findAll('td')[0].text.strip()
date2 = date_row.findAll('td')[1].text.strip()
if date1 == "Date:":
    try:
        event_year = int(date2.split('.')[-1])
    except ValueError:
        print("Warn: could not get event year from result page", file=sys.stderr)
        if not args.year:
            print("Try specifying the year via --year option", file=sys.stderr)
            sys.exit(1)

    if args.verbose:
        print("Found event Year: " + str(event_year) + " (" + date2 + ")")

if args.year:
    if event_year:
        print("Warn: overriding event year: " + str(event_year), file=sys.stderr)
    event_year = args.year

result_file = 'results-event-' + eventid + '-' + str(event_year) + '.csv'
if args.verbose:
    print("Writing results to file: " + result_file)

# get event name and print if verbose
event_row = table4.findAll('tr')[1]
if event_row.findAll('td')[0].text.strip() == "Event:":
    event_name = event_row.findAll('td')[1].text.strip()
    if args.verbose:
        print("Event: " + event_name)

# get result table, actually get table body only by id
results = soup.find("tbody", id="EvtRslt")
if args.debug:
    print("result list:\n" + str(results))


output_rows = []
for results_row in results.findAll('tr'):
    cols = results_row.findAll('td')
    output_row = []

    place = cols[0].text
    time = cols[1].text.split()[0]
    name = cols[2].findAll('a')[0].text
    last, first = [unidecode(tr_umlaut(s.strip())) for s in name.split(',')]
    # I found runners without birthday ... ultra-runners are strange people ;)
    try:
        runner_yob = int(cols[5].text.strip())
    except ValueError:
        print("Warn: no year of birth for runner: " + name + ", skipping", file=sys.stderr)
        continue

    age = event_year - runner_yob
    gender = cols[6].text.strip()
    state  = cols[4].text.strip() # fixme: country!! GER vs DEU ?!!
    # todo: could try to extract city from "club" field (indicated via *cityname)
    
    output_row.extend((place, time, first, last, str(age), gender, state))
    output_rows.append(output_row)

    if args.verbose > 1:
        print("Found: " + str(output_row))


with open(result_file, 'w') as f:
    writer = csv.writer(f)
    # csv minimum headers required: place, time|distance, first, last, age, gender
    # todo: distance for times event eg. 24h runs
    writer.writerow(['place', 'time', 'first', 'last', 'age', 'gender', 'state'])
    writer.writerows(output_rows)
