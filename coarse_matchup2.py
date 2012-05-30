#!/usr/bin/env python

import os, sys, csv
from SOAPpy.WSDL import Proxy
from datetime import datetime, timedelta
import elementtree.ElementTree as ET


# NOAA data file for LAX
NOAA_file = os.path.join("data", "NOAA", "36258.csv")

def main():

    # get proxy
    wsdl = sys.argv[1]
    proxy = Proxy(wsdl)

    # read in NOAA data
    f = open(NOAA_file)
    reader = csv.DictReader(f)
    for row in reader:
        # get lat/lon
        noaa_lat = float(row['LATITUDE'])
        noaa_lon = float(row['LONGITUDE'])

        # bbox
        minLat = noaa_lat - 3.
        maxLat = noaa_lat + 3.
        minLon = noaa_lon - 3.
        maxLon = noaa_lon + 3.
        
        break

    #minLat = -90
    #maxLat = 90
    #minLon = -180
    #maxLon = 180

    # get start and end date surrounding NOAA date
    start_dt = datetime(2010, 1, 1)
    end_dt = datetime(2010, 12, 31)
    print start_dt, end_dt
    print minLat, maxLat, minLon, maxLon

    # get matching AIRS metadata info
    #results = proxy.geoRegionQuery("AIRS", None, None, "2010-01-01T00:00:00Z",
    #                               "2010-01-01T00:01:00Z", -180, 180, -90, 90,
    #                               "Large")
    results = proxy.geoRegionQuery("AIRS", None, None, 
        "%04d-%02d-%02dT%02d:%02d:00Z" % (start_dt.year, start_dt.month, start_dt.day, start_dt.hour, start_dt.minute),
        "%04d-%02d-%02dT%02d:%02d:00Z" % (end_dt.year, end_dt.month, end_dt.day, end_dt.hour, end_dt.minute), minLat, maxLat, minLon, maxLon,
        "Large")
    print results

    xmlFile = "AIRS.xml"
    f = open(xmlFile, 'w')
    f.write(results)
    f.close() 
    tree = ET.parse(xmlFile)
    matches = tree._root.getchildren()
    if len(matches) > 0:
        print "NOAA data:", row['DATE'], row['LATITUDE'], row['LONGITUDE'], row['HLY-TEMP-NORMAL']
        #print results
        print len(matches)
        print "matched AIRS:", len(matches)

    # cleanup
    f.close()

if __name__ == "__main__":
    main()
