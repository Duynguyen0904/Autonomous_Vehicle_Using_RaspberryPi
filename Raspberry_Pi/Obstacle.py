from rplidar import *
import time
import serial

ser = serial.Serial('PORT',115200, timeout=1) # Change 'PORT' to PORT_Raspberry_Pi connected to arduino instead
def run_rplidar():
    lidar = RPLidar('PORT',115200, 2) # Change 'PORT' to PORT_Raspberry_Pi connected to lidar instead
    lidar.connect()
    try:
        lidar.connect()
        lidar.start_motor()
        while True:
            for scan in lidar.iter_scans():  # Scan and process data from RPLIDAR
                if len(scan) > 200:
                    scan = scan[100:]
                objects_in_angle = get_objects_in_custom_angle(scan, start_angle=0, end_angle=181)
                if objects_in_angle:
                    print("Objects detected in custom angle:")
                    distance = round(float(objects_in_angle[-1][1]/10),2)
                    print(f"Distance: {distance} cm")                
                    send_to_arduino(lidar, ser, distance)
                    ser.flushInput()
                    time.sleep(.1)
    except RPLidarException:
        lidar.stop()
        run_rplidar()
        time.sleep(0.0001)
    except KeyboardInterrupt:
        print('Stopping RPLIDAR...')
        lidar.stop()
        lidar.disconnect()

def get_objects_in_custom_angle(scan_data, start_angle, end_angle):
    objects = []
    for (_, angle, distance) in scan_data:
        if start_angle <= angle <= end_angle:
            objects.append((angle, distance))
    return objects

def send_to_arduino(lidar ,serial_connection ,data):
    print(data)
    if data > 40:
        serial_connection.write(b"1") #should be converted to string
    else:
        serial_connection.write(b"2") #should be converted to string
        lidar.stop()
    
if __name__ == '__main__':
    run_rplidar()