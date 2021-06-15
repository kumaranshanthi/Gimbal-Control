import os, time, math, glob, re
import pyexiv2, datetime, argparse
import fractions, dateutil.parser, shutil
import serial
class Fraction(fractions.Fraction):
    """Only create Fractions from floats.
    >>> Fraction(0.3)
    Fraction(3, 10)
    >>> Fraction(1.1)
    Fraction(11, 10)
    """

    def __new__(cls, value, ignore=None):
        """Should be compatible with Python 2.6, though untested."""
        return fractions.Fraction.from_float(value).limit_denominator(99999)

def decimal_to_dms(decimal):
    """Convert decimal degrees into degrees, minutes, seconds.
    >>> decimal_to_dms(50.445891)
    [Fraction(50, 1), Fraction(26, 1), Fraction(113019, 2500)]
    >>> decimal_to_dms(-125.976893)
    [Fraction(125, 1), Fraction(58, 1), Fraction(92037, 2500)]
    """
    remainder, degrees = math.modf(abs(decimal))
    remainder, minutes = math.modf(remainder * 60)
    return [Fraction(n) for n in (degrees, minutes, remainder * 60)]

_last_position = None

def set_gps_location(file_name, lat, lng, alt):
    """
    see: http://stackoverflow.com/questions/453395/what-is-the-best-way-to-geotag-jpeg-images-with-python
    
    Adds GPS position as EXIF metadata
    Keyword arguments:
    file_name -- image file 
    lat -- latitude (as float)
    lng -- longitude (as float)
    """

    m = pyexiv2.ImageMetadata(file_name)
    m.read()

    m["Exif.GPSInfo.GPSLatitude"] = decimal_to_dms(lat)
    m["Exif.GPSInfo.GPSLatitudeRef"] = 'N' if lat >= 0 else 'S'
    m["Exif.GPSInfo.GPSLongitude"] = decimal_to_dms(lng)
    m["Exif.GPSInfo.GPSLongitudeRef"] = 'E' if lng >= 0 else 'W'
    m["Exif.Image.GPSTag"] = 654
    m["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
    m["Exif.GPSInfo.GPSVersionID"] = '2 0 0 0'
   # m["Exif.Image.DateTime"] = datetime.datetime.fromtimestamp(t)

    try:
      m["Exif.GPSInfo.GPSAltitude"] = Fraction(alt)
    except Exception:
      pass

    m.write()

def parseGPS(ser):
    data = ser.readline()
    #data=str(data,'utf-8')
   # print ("raw:",data)
    if data[0:6] == "$GPGGA":
        s = data.split(",")
       # print(s)
        if s[7] == '0':
            print ("no satellite data available")
            return        
        time = s[1][0:2] + ":" + s[1][2:4] + ":" + s[1][4:6]
        lat = decode(s[2])
        dirLat = s[3]
        lon = decode(s[4])
        dirLon = s[5]
        alt = s[9] + " m"
        sat = s[7]
       
       # print ("Time(UTC): %s-- Latitude: %s(%s)-- Longitude:%s(%s) -- Altitute:%s--(%s satellites)" %(time, lat, dirLat, lon, dirLon, alt, sat) )
        return lat, lon
def decode(coord):
    decimal_value = float(coord)/100.00
    degrees = int(decimal_value)
    mm_mmmm = float(coord)-(degrees*100)
    position = degrees + mm_mmmm/60
    position = format(position, '.4f')
    return position


