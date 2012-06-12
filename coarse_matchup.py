#!/usr/bin/env python

import os, sys, csv, re, calendar
from SOAPpy.WSDL import Proxy
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import numpy as N


#compiled regular expressions
ISO_DT_RE = re.compile(r'^(\d{4})[/-](\d{2})[/-](\d{2})[\s*T](\d{2}):(\d{2}):(\d{2})(?:\.\d+)?Z?$')
ISO_DT_ONLY_RE = re.compile(r'^(\d{4})[/-](\d{2})[/-](\d{2})$')
NOAA_DT_RE = re.compile(r'^(\d{4})(\d{2})(\d{2})\s+(\d{2}):(\d{2})$')


# NOAA data file for LAX
NOAA_file = os.path.join("data", "NOAA", "36258.csv")


def getISOTimeElts(dtStr):
    """
    Return tuple of (year,month,day,hour,minute,second) from date time string.
    """

    match = ISO_DT_RE.match(dtStr)
    if match: year, month, day, hour, minute, second = map(int,match.groups())
    else:
        match = ISO_DT_ONLY_RE.match(dtStr)
        if match:
            year, month, day = map(int,match.groups())
            hour, minute, second = 0,0,0
        else: raise RuntimeError("Failed to recognize date format: %s" % dtStr)
    return year, month, day, hour, minute, second

def getDatetime(dtStr):
    """Return datetime object from date time string."""

    year, month, day, hour, minute, second = getISOTimeElts(dtStr)
    return datetime.datetime(year=year, month=month, day=day,
                             hour=hour,minute=minute, second=second)

def getEpoch(timeStr):
    """Return epoch from a time string: '%Y-%m-%d %H:%M:%S'."""

    return float(calendar.timegm(getISOTimeElts(timeStr)))

def getNOAATimeElts(dtStr):
    """
    Return tuple of (year,month,day,hour,minute) from NOAA date time string.
    """

    match = NOAA_DT_RE.match(dtStr)
    if match: year, month, day, hour, minute = map(int,match.groups())
    else: raise RuntimeError("Failed to recognize date format: %s" % dtStr)
    return year, month, day, hour, minute, 0

def getNOAAEpoch(timeStr):
    """Return epoch from a time string: '%Y%m%d %H:%M'."""

    return float(calendar.timegm(getNOAATimeElts(timeStr)))

def getNOAARows(file):
    """Return data rows from NOAA file."""

    with open(file) as f:
        rows = [row for row in csv.DictReader(f)]
    return rows
 
def main():

    # get proxy
    wsdl = sys.argv[1]
    proxy = Proxy(wsdl)

    # read in NOAA data
    rows = getNOAARows(NOAA_file)

    #get bbox with slop
    noaa_lat = float(rows[0]['LATITUDE'])
    noaa_lon = float(rows[0]['LONGITUDE'])
    min_lat = noaa_lat - 3.
    max_lat = noaa_lat + 3.
    min_lon = noaa_lon - 3.
    max_lon = noaa_lon + 3.
    #print noaa_lat, noaa_lon

    # get start and end date of NOAA data
    str_dt = datetime(*getNOAATimeElts(rows[0]['DATE']))
    end_dt = datetime(*getNOAATimeElts(rows[-1]['DATE']))
    #print str_dt, end_dt

    # get matching AIRS metadata info
    results = proxy.geoRegionQuery("AIRS", None, None, 
                                   str_dt.isoformat(), 
                                   end_dt.isoformat(),
                                   min_lat, max_lat, 
                                   min_lon, max_lon,
                                   "Large")

    #write GRQ xml results to file
    xml_file = "AIRS.xml"
    with open(xml_file, 'w') as f:
        f.write(results)

    #parse xml
    root = ET.parse(xml_file).getroot()
    matches = root.getchildren()
    #print len(rows), len(matches)
    #print "matched AIRS:", len(matches)

    #create AIRS start/end time array
    sfns = "http://sciflo.jpl.nasa.gov/2006v1/sf"
    airs_times = []
    for match in matches:
        airs_str_epoch = getEpoch(match.find('{%s}starttime' % sfns).text)
        tmp_dt = match.find('{%s}endtime' % sfns).text
        airs_end_epoch = getEpoch(match.find('{%s}endtime' % sfns).text)
        airs_times.append([airs_str_epoch, airs_end_epoch])
    airs_times = N.array(airs_times)
    print airs_times.shape
    print airs_times

    #find matchup by time
    coarse_match = []
    for row in rows:
        noaa_epoch = getNOAAEpoch(row['DATE'])
        time_match = N.where(
                     (
                        (noaa_epoch >= airs_times[:, 0]) &
                        (noaa_epoch <= airs_times[:, 1])
                     ) == True)[0]
        if len(time_match) > 0:
            airs_match = matches[time_match]
            for url in airs_match.findall('{%s}urls/{%s}url' % (sfns, sfns)):
                if url.text.startswith('file://'): continue
                if 'L2.RetStd' in url.text:
                    coarse_match.append({time_match[0]: url.text})
                    break
    print "Total coarse match:", len(coarse_match)
    print coarse_match

if __name__ == "__main__":
    main()
