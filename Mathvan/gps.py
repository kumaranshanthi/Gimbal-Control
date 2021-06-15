import serial
import glob
#port =glob.glob('/dev/ttyUSB[0-9]*') # Raspberry Pi 2
#port = "/dev/ttyS0"    # Raspberry Pi 3
port='/dev/ttyUSB0'
print(port)
def parseGPS(data):
    #data=str(data,'utf-8')
    print ("raw:",data)
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


    

ser = serial.Serial(port, baudrate = 9600, timeout = 0.5)
gps_data="$GPGGA,210230,3855.4487,N,09446.0071,W,1,07,1.1,370.5,M,-29.5,M,,*7A"
while True:
    ser.write(str.encode(gps_data))
    data = ser.readline()
    lat,lon=parseGPS(data)
    print lat,lon
