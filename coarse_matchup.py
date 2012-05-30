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

        # get ISO 8601 datetime from NOAA data
        yy = int(row['DATE'][0:4])
        mm = int(row['DATE'][4:6])
        dd = int(row['DATE'][6:8])
        hh = int(row['DATE'][9:11])
        mn = int(row['DATE'][12:14])
        dt = datetime(year=yy, month=mm, day=dd, hour=hh, minute=mn)
    
        # get start and end date surrounding NOAA date
        start_dt = dt - timedelta(seconds=3600)
        end_dt = dt + timedelta(seconds=3600)
        print start_dt, end_dt

        # get lat/lon
        noaa_lat = float(row['LATITUDE'])
        noaa_lon = float(row['LONGITUDE'])

        # bbox
        minLat = noaa_lat - 3.
        maxLat = noaa_lat + 3.
        minLon = noaa_lon - 3.
        maxLon = noaa_lon + 3.
        #minLat = -90
        #maxLat = 90
        #minLon = -180
        #maxLon = 180
    
        # get matching AIRS metadata info
        #results = proxy.geoRegionQuery("AIRS", None, None, "2010-01-01T00:00:00Z",
        #                               "2010-01-01T00:01:00Z", -180, 180, -90, 90,
        #                               "Large")
        results = proxy.geoRegionQuery("AIRS", None, None, 
            "%04d-%02d-%02dT%02d:%02d:00Z" % (start_dt.year, start_dt.month, start_dt.day, start_dt.hour, start_dt.minute),
            "%04d-%02d-%02dT%02d:%02d:00Z" % (end_dt.year, end_dt.month, end_dt.day, end_dt.hour, end_dt.minute), minLat, maxLat, minLon, maxLon,
            "Large")

        xmlFile = "AIRS.xml"
        f = open(xmlFile, 'w')
        f.write(results)
        f.close() 
        tree = ET.parse(xmlFile)
        root = tree.getroot()
        matches = tree._root.getchildren()

        if len(matches) > 0:
            print "NOAA data:", row['DATE'], row['LATITUDE'], row['LONGITUDE'], row['HLY-TEMP-NORMAL']
            #print results
            print len(matches)
            print "matched AIRS:", len(matches)
            
 
            for result in root.getchildren():
                print result.find('{http://sciflo.jpl.nasa.gov/2006v1/sf}objectid').text
                print result.find('{http://sciflo.jpl.nasa.gov/2006v1/sf}starttime').text
                print result.find('{http://sciflo.jpl.nasa.gov/2006v1/sf}endtime').text
                print result.find('{http://sciflo.jpl.nasa.gov/2006v1/sf}latMin').text
                print result.find('{http://sciflo.jpl.nasa.gov/2006v1/sf}latMax').text
                print result.find('{http://sciflo.jpl.nasa.gov/2006v1/sf}lonMin').text
                print result.find('{http://sciflo.jpl.nasa.gov/2006v1/sf}lonMax').text

    # cleanup
    f.close()

if __name__ == "__main__":
    main()
