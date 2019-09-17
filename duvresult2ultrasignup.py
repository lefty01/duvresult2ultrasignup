#!/usr/bin/env python3

# copyright (c) 2019 andreas loeffler

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import csv
import argparse

parser = argparse.ArgumentParser(description='convert duv stat results to csv list suitable to upload to ultrasignup')
parser.add_argument('-e', '--event', required=True,
                        help='DUV event ID')
parser.add_argument('-y', '--year',  type=int, required=True,
                        help='year of the event (to get runners age)')
args = parser.parse_args()

event_year = args.year
eventid = str(args.event)

duv = 'http://statistik.d-u-v.org/getresultevent.php?event='
result_file = 'results-event-' + eventid + '.csv'
event_url = duv + eventid

print("getting results for event #" + eventid + " from url: " + event_url)

# FIXME handle error
resp = 'n/a'
resp = requests.get(event_url)
soup = BeautifulSoup(resp.text, "html.parser")

results = soup.find("tbody", id="EvtRslt")
#print("result list:\n" + str(results))


# [0] place:          <td nowrap='nowrap' align='center'>1</td>
# [1] time:           <td nowrap='nowrap' align='right'>12:24:50 h&nbsp;</td>
# [2]!first,last: <td nowrap='nowrap' align='left'><a href='getresultperson.php?runner=123456'>&nbsp;xxxxxxxx, xxxxxx</a></td>
#    <td nowrap='nowrap' align='left'> &nbsp;</td>
# [4] state: ?        <td nowrap='nowrap' align='center'>GER&nbsp;</td>
# [5] age:            <td nowrap='nowrap' align='center'>19xx</td>
# [6] gender:         <td nowrap='nowrap' align='center'>M</td>
#    <td nowrap='nowrap' align='center'>n</td>
#    <td nowrap='nowrap' align='center'>Mxx&nbsp;</td>
#    <td nowrap='nowrap' align='center'>1</td>
#    <td nowrap='nowrap' align='right'>9.264</td>
#    <td nowrap='nowrap' align='right'>10:38:29 h</td>




output_rows = []
for results_row in results.findAll('tr'):
    cols = results_row.findAll('td')
    output_row = []

    place = cols[0].text
    time = cols[1].text.split()[0]
    last, first = [s.strip() for s in cols[2].text.split(',')]
    # age: get year of event then time diff current year - year of event
    age = event_year - int(cols[5].text.strip())
    gender = cols[6].text.strip()
    state  = cols[4].text.strip()
    
    # print("place:  " + place)
    # print("time:   " + time)
    # print("first:  " + first)
    # print("last:   " + last)
    # print("age:    " + str(age))
    # print("gender: " + gender)
    # print("state:  " + state)
    # print("")

    output_row.append(place)
    output_row.append(time)
    output_row.append(first)
    output_row.append(last)
    output_row.append(str(age))
    output_row.append(gender)
    output_row.append(state)

    output_rows.append(output_row)
    print("out row: " + str(output_row))


with open(result_file, 'w', encoding='utf-8') as f:
    writer = csv.writer(f)
    # csv minimum headers required: place, time|distance, first, last, age, gender
    # todo: distance for times event eg. 24h runs
    writer.writerow(['place', 'time', 'first', 'last', 'age', 'gender'])
    writer.writerows(output_rows)
