#!/usr/bin/python3 
# -*- coding: iso-8859-15 -*-
# -------------------------- importing the requests library --------------------
#from pynput.keyboard import Key, Controller
#from pynput import keyboard
import requests 
import ntplib
import ftplib
#import ftplib.FTP_TLS
from ftplib import FTP
from contextlib import closing
import time
from time import sleep
import serial
import numpy as geek
import array
import sys
import os, subprocess
from sys import argv
import socket
import atexit
import codecs
import shutil
#from gpiozero import PWMLED
import RPi.GPIO as GPIO
#from RPLCD.gpio import CharLCD
#import mysql.connector
import ADS1256

#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  
# --------------------------------- setup HW -----------------------------------
#INPUT
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
#GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#OUTPUT
GPIO.setup(13,GPIO.OUT)     # LCD backlight
GPIO.output(13,GPIO.LOW)

# Define GPIO to LCD mapping
LCD_RS = 17
LCD_E  = 22
LCD_D4 = 19
LCD_D5 = 26
LCD_D6 = 21
LCD_D7 = 20
LED_ON = 15
RW = 27

# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
GPIO.setup(RW,GPIO.OUT)
GPIO.output(RW,GPIO.LOW)
    
# define HX711 pin
DT = 10
SCK = 9

# --------- Config DB ------------
config = {
  'user': 'xxxxx',
  'password': 'xxxxxx',
  'host': '127.0.0.1',
  'database': 'xxxxxx'
}

# --- Setting global variables ---
filename = ''
Time = ''
fix = ''
lat = ''
ns = ''
lon = ''
eo = ''
speed = ''
track = ''
datatoday = ''
magnetic = ''
mag_eo = ''
status = ''
utc = ''
lat2 = ''
ns2 = ''
lon2 = ''
eo2 = ''
quality = ''
sat = ''
hdop = ''
alt = ''
unialt = ''
diff = ''
unidiff = ''
agedata = ''
diffref = ''
Time zone = 0       # time zone
gapprog = 5    # constant for interval between two registers
ch1 = ""       # variable name ch1
ch2 = ""       # variable name ch2
ch3 = ""       # variable name ch3
ch4 = ""       # variable name ch4
ch5 = ""       # variable name ch5
ch6 = ""       # variable namee ch6
mul1 = 1         # multiply ch1
mul2 = 1         # multiply ch2
mul3 = 1         # multiply ch3
mul4 = 1         # multiply ch4
mul5 = 1         # multiply ch5
mul6 = 1         # multiply ch6
add1 = 1         # add ch1
add2 = 1         # add ch2
add3 = 1         # add ch3
add4 = 1         # add ch4
add5 = 1         # add ch5
add6 = 1         # add ch6
volt1 = 0
volt2 = 0
volt3 = 0
volt4 = 0
volt5 = 0
volt6 = 0
realtimech = 1   # channel number in realtime graph
vbatshutdown = 9.8 # minimum voltage below which automatic shutdown occurs
fileswap = "/var/www/html/tmp/swappa.txt"
fileram = "/var/www/html/tmp/realtime.txt"
filegraph1 = "/var/www/html/tmp/graph1.txt"
pathdati = "/var/www/html/dati/"
pathusb = "/average/pi/agrhysmo/data/"
filestore = ""

IDbox = "452136"                           # box identifier
url = "http://www.xxxxxxxx.com/testring.php" #page to send
idkey = ''                  #id user
idpsw = 'xxxxxxxxx'                  #id password    
serverftp = 'xxxxxxxxx.agr.unipi.it'
serverpath = './ftp'
userftp = 'xxxxxxxx'
pswdftp = 'xxxxxxxx'
enableftp = 0                      # 1 = ftp sending enabled
# --------------------------------------------
#lcd = CharLCD(numbering_mode=GPIO.BCM, cols=20, rows=4, pin_rs=17, pin_rw=27,
#              pin_e=22, pins_data=[19, 26, 21, 20], pin_backlight=None,)
rfidstring = ""
arrival = ""                       # RFID arrival date and time YYYY-MM-DD hh:mm:ss
memo = list()
IPAddr = ""

status = 0                         # state 0 = idle 1 = record
Button = 0                         # button pressed on keyboard
posx = 0                          # X position on LCD
keyboarddata = ""                 # data string written on LCD

# --------------------------------------------
#keyboard = Controller()

# -------- SERIAL SETUP ----------
ser1 = serial.Serial('/dev/ttyAMA0', baudrate=9600,
                     parity=serial.PARITY_NONE,
                     stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS,
                     xonxoff=False,
                     rtscts=False,
                     dsrdtr=False,
                     timeout=1
                     )
time.sleep(1)

# ---------------------------------
def loadconfig():
    mydb = mysql.connector.connect(**config)     # open DB
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM setup")
    for row in cursor.fetchall():
        print (row)
        url = str(row[5])
        idkey = str(row[6])
        idpsw = str(row[7])
        serverftp = str(row[8])
        serverpath = str(row[9])
        userftp = str(row[10])
        pswftp = str(row[11])
    cursor.close()
    mydb.close()                                 # close DB

# -------------------------------------
def puls1(channel):
    GPIO.remove_event_detect(channel) 
    waitril(channel)
    GPIO.add_event_detect(channel, GPIO.FALLING, callback=puls1, bouncetime=10)
    
# -------------------------------------
def puls2(channel):
    GPIO.remove_event_detect(channel)
    GPIO.add_event_detect(channel, GPIO.FALLING, callback=puls2, bouncetime=10)
    
# -------------------------------------    
def puls3(channel):
    global stato
    GPIO.remove_event_detect(channel) 
    GPIO.add_event_detect(channel, GPIO.FALLING, callback=puls3, bouncetime=10)
    
# -------------------------------------    
def waitril(pin):
    countpuls = 0
    while (countpuls < 10):
        time.sleep(0.01)
        if (GPIO.input(pin) == 0):
            countpuls = 0
        else:
            countpuls+=1

# -------------------------------------    
def getdecimal(c1, c2):
    if ((c1 >= 48) and (c1 <= 57)):
        temp = (c1 - 48)
    else:
        temp = (c1 - 55)
    temp *= 16
    if ((c2 >= 48) and (c2 <= 57)):
        return (temp +c2 - 48)
    else:
        return (temp +c2 - 55)

# ------------------------------------
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# -------------------------------------
def sendhttp(dataora, rfid):
    mydata = {'dati': dataora + ';' + rfid + ';',
              'idkey': idkey,
              'idpsw': idpsw  }
    x = requests.post(url, data = mydata) 
    #print(x.status_code) 
    if x.status_code != 200:
        print("Invio non riuscito")
    else:
        print (mydata)
        
# ---- Send file to server via FTP ----
def sendfileftp(filessname):
    global serverftp, userftp, pswdftp, serverpath, IDbox
    try:
        ftp = FTP(serverftp)  
        ftp.login(user=userftp, passwd=pswdftp)
        #print (ftp.pwd())
        ftp.cwd(serverpath)
        #print (ftp.pwd())
        #ftp.set_pasv(False)
        #print (ftp.dir())
        #ftp.encoding = "utf-8"
        ftp.storbinary(f'STOR {os.path.split(filessname)[1]}', 
                               open(filessname, 'rb'))
        ftp.quit()
    except:
        print('Could not send ftp.')
        
# ----------- time sync ---------------
def synctime(proof):
    while (proof > 0):  # exits here if it is synchronized or after test times
        try:
            client = ntplib.NTPClient()
            response = client.request('europe.pool.ntp.org', version=3)
            ofs = response.offset
            os.system('sudo date ' + time.strftime('%m%d%H%M%Y.%S',
                       time.localtime(response.tx_time)))
            print('Time sync done ' + str(ofs))
            break
        except:
            print('Could not sync with time server.')
            proof -= 1
    sleep(1)
# ----------- time sync with gps ---------------
def synctime_gps(datanow):
    try:
        ofs = -0.0085
        os.system('sudo date ' + datanow)
        print('Time sync gps done ' + str(ofs))
    except:
        print('Could not sync with gps.')
    sleep(1)
# ----------- time sync with web ---------------
def synctime_web(datanow):
    try:
        ofs = -0.008562564849853516
        os.system('sudo date ' + datanow)
        print('Time sync web done ' + str(ofs))
    except:
        print('Could not sync with web.')
    sleep(1)        
# -------SERIAL RX GPS NMEA183 --------------
def rxgps():
    global nomefile, ora, fix, lat, ns, lon, eo, speed, track
    global dataoggi, magnetic, mag_eo, status
    global utc, lat2, ns2, lon2, eo2, quality, sat, hdop, alt
    global unialt, diff, unidiff, agedata, diffref
    global fuso, pathdati
    #nmea183 = "101222,155052.00,4337.69779,N,01017.75544,E,6.8,07" 
    Received = 0
    rx1 = 0
    rx2 = 0
    while (ricevuto == 0):
        date = ser1.readline()
        date = date[0:-4]
        ck = date[-1]
        if (ck == 42):
            date = data.decode('utf-8','strict')
            gps = data.split(',')
            tipe = gps[0]
            if (tipo == "$GPRMC"):
                Time = gps[1]
                fix = gps[2]
                lat = gps[3]
                ns = gps[4]
                lon = gps[5]
                eo = gps[6]
                speed = gps[7]
                track = gps[8]
                dataoggi = gps[9]
                magnetic = gps[10]
                mag_eo = gps[11]
                status = gps[12]
                if (fix == 'A'):
                    rx1 = 1
            
            if (tipo == "$GPGGA"):
                utc = gps[1]
                lat2 = gps[2]
                ns2 = gps[3]
                lon2 = gps[4]
                eo2 = gps[5]
                quality = gps[6]
                sat = gps[7]
                hdop = gps[8]
                alt = gps[9]
                unialt = gps[10]
                diff = gps[11]
                unidiff = gps[12]
                agedata = gps[13]
                diffref = gps[14]
                rx2 = 1
    
            if ((rx1 == 1) and (rx2 == 1)):
                gg = datetoday[0:2]
                mm = datetoday[2:4]
                aa = datetoday[4:6]
                hh = time[0:2]
                mi = time[2:4]
                ss = time[4:6]
                hh = int(hh)+time zone
                if (hh < 0):
                    hh = hh + 24
                hh = str(hh)
                if (len(hh) < 2):
                    hh = "0" + hh
                ora = hh + mi + ss
                filename = pathdati + IDbox + '-20' + aa + mm + gg + hh
                           + mi + ss + '.csv'
                
                lat1 = lat[0:2]                          # convert latitude
                lat2 = lat[2:4]
                lat3 = lat[5:10]
                lat2 = lat2+lat3
                lat3 = str(int(lat2)*500/3)
                lat3 = lat3[0:8]
                lat = lat1+"."+lat3
    
                lon1 = lon[1:3]                         # convert longitude
                lon2 = lon[3:5]
                lon3 = lon[6:11]
                lon2 = lon2+lon3
                lon3 = str(int(lon2)*500/3)
                lon3 = lon3[0:8]
                lon = lon1+"."+lon3
                
                received = 1

    return (datetoday+','+time+','+str(lat)+','+ns+','+str(lon)+','+eo+',
            '+str(alt)+','+str(sat))

#--- checksum calculation in nmea183 ---
def cksum(string_input):
    # attention, for simplicity exceptions are not handled
    payload_start = string_input.find('$') + 1  
    # finds the first character after $
    payload_end   = string_input.find('*')      
    # find the character *
    payload = string_input [ payload_start : payload_end ]   
    # data to XOR
    ck = 0
    for ch in payload:      # checksum calculation cycle
        ck = ck ^ ord(ch)   # XOR
    str_ck = '%02X' % ck    # conv. the value in a 2-character string
    return str_ck

        
# --- COPY FILE TO USB KEY ---
def file2usb():
    global pathdati, pathusb
    esito2 = True
    for filename in os.listdir(pathdati):
        source = pathdati + filename
        destination = pathusb + filename
        outcome = True
        try:
            shutil.copy2(source, destination)
        except shutil.Error as e:
            print("Error: %s" % e)
            outcome = False
            outcome2 = False
        except IOError as e:
            print("Error: %s" % e.strerror)
            outcome = False
            outcome2 = False
        if esito is True:
            print("copied data files")
        else:
            print("data files NOT copied")
    return outcome2
        
# ----- VIEW ON LCD --------
def view(indx):
    if (indx == 0):
        lcd_init()
        lcd_string("AgrHySMo EM38",LCD_LINE_1,4)
        lcd_string("Waiting for NTP",LCD_LINE_2,3)
    elif (indx == 1):
        lcd_string("IP:                 ",LCD_LINE_2,0)
        lcd_string("IP: " + IPAddr,LCD_LINE_2,0)
        lcd_string("Waiting for GPS",LCD_LINE_3,3)    
    elif (indx == 2):
        lcd_string(datanow+"  "+oranow,LCD_LINE_1,0)    
        lcd_string("Lat: "+lat+" "+ns,LCD_LINE_2,0)
        lcd_string("Lon: "+lon+" "+eo,LCD_LINE_3,0)
        v5 = str(volt5)
        xxx = v5.split(".")
        v5 = xxx[0]
        lcd_string("Value: %s    "%(v5),LCD_LINE_4,0)
        if (registra == 1):
            lcd_string("REG",LCD_LINE_4,17)
        else:
            lcd_string("IDL",LCD_LINE_4,17)
    elif (indx == 3):
        lcd_init()
        lcd_string("AgrHySMo EM38",LCD_LINE_1,4)
        lcd_string("CLOSING",LCD_LINE_2,6)
        lcd_string("LOW  BATTERY",LCD_LINE_4,4)
    elif (indx == 4):
        lcd_init()
        lcd_string("  TRANSFER TO USB   ",LCD_LINE_2,0)
    elif (indx == 5):
        lcd_init()
        lcd_string(" TRANSFERED TO USB  ",LCD_LINE_3,0)
    elif (indx == 6):
        lcd_init()
        lcd_string("FILE TRANSFER  ERROR",LCD_LINE_3,0)

# --------------------------------    

def LCD_Clear():
    LCD_Write(0x01,0)
#---
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
 
  GPIO.output(LCD_RS, mode) # RS
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  lcd_toggle_enable()
#--- 
def lcd_toggle_enable():
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
#--- 
def lcd_string(message,line,col):
#  message = message.rjust(LCD_WIDTH," ")
  lcd_byte(line + col, LCD_CMD)
  lunga = len(message) 
  for i in range (lunga):
    lcd_byte(ord(message[i]),LCD_CHR)

# ----- READ CONFIGURATION FILE --------
def ReadConfig():
    global gapprog, fuso, ch1, ch2, ch3, ch4, ch5, ch6, mul1, mul2, mul3
    global mul4, mul5, mul6, add1, add2, add3, add4, add5, add6, realtimech
    cfg = open("/var/www/html/config/setup.cfg", "r")   # read gap
    strin = cfg.readline()
    xx = strin.split(";")
    gapprog = int(xx[0])                       # gap
    fuso = int(xx[1])                          # time change
    ch1 = xx[2]                          
    ch2 = xx[3]                          
    ch3 = xx[4]                          
    ch4 = xx[5]                          
    ch5 = xx[6]                          
    ch6 = xx[7]
    mul1 = xx[8]
    mul2 = xx[9]
    mul3 = xx[10]
    mul4 = xx[11]
    mul5 = xx[12]
    mul6 = xx[13]
    add1 = xx[14]
    add2 = xx[15]
    add3 = xx[16]
    add4 = xx[17]
    add5 = xx[18]
    add6 = xx[19]
    realtimech = xx[20]
    cfg.close()

# ----- READ NET FTP CONFIGURATION FILE --------
def ReadNet():
    global serverftp, userftp, pswdftp, serverpath, IDbox, enableftp
    cfg = open("/var/www/html/config/net.cfg", "r")
    strin = cfg.readline()
    xx = strin.split(";")
    IDbox = xx[0]
    serverftp = xx[1]                
    serverpath = xx[2]                          
    userftp = xx[3]                   
    pswdftp = xx[4]
    enableftp = xx[5]     
    cfg.close()
   
    serverftp = "xxxxxxxxxx"
    serverpath = "xxxxxxxxxx"
    userftp = "xxxxxxxxxx"
    pswdftp = "xxxxxxxxxx"
    
# -------- WRITE FILES FROM RAM TO SD ---------    
def ram2sd():            
    global fileswap, filestore, fileswap
    if os.path.isfile(fileswap):
        try:
            f2 = open(filestore, "a")    
            with open(fileswap, "r") as file:
               for line in file:
                   f2.write(line)
               f2.close()
               os.remove(fileswap)
        except:
            print('Could not copy ram file to SD.')


# ----- INTERRUPT SETUP ----------
#GPIO.add_event_detect(23, GPIO.FALLING, callback=puls1, bouncetime=10)  
#GPIO.add_event_detect(24, GPIO.FALLING, callback=puls2, bouncetime=300)  
#GPIO.add_event_detect(25, GPIO.FALLING, callback=puls3, bouncetime=300)  

###################################
#           PROGRAM               #
###################################
#loadconfig();                         # initialize setup variables
GPIO.output(13,GPIO.HIGH)              # turn on LCD backlight
lcd_init()                             # initialize display
view (0)                          # welcome message
synctime(3)                            # sync time by NTP max 3 times
IPAddr = get_ip()                      # searches and displays IP addresses
view (1)
print("IP Address is: " + IPAddr) 
datetime = time.strftime("%Y%m%d%H%M%S")
print (datetime)

ADC = ADS1256.ADS1256()                # initializes A/D converter
ADC.ADS1256_init()                     #

if not os.path.exists("/var/www/html/config/setup.cfg"):
    f = open("/var/www/html/config/setup.cfg", "w")    
    f.write("5;1;ch1;ch2;ch3;ch4;ch5;ch6;10.15;1;1;1;1;1;0;0;0;0;0;0;1")
    f.close()
    os.system('sudo chown www-data.www-data /var/www/html/config/setup.cfg')
    os.system('sudo chmod 666 /var/www/html/config/setup.cfg')
ReadConfig()

if not os.path.exists("/var/www/html/config/net.cfg"):
    f = open("/var/www/html/config/net.cfg", "w")    
    f.write("000000;http://xxxxxxxxxx.agr.unipi.it;./ftp;xxxxxxxxxx;xxxxxxxxxx")
    f.close()
    os.system('sudo chown www-data.www-data /var/www/html/config/net.cfg')
    os.system('sudo chmod 666 /var/www/html/config/net.cfg')
ReadNet()

ser1.isOpen()
ser1.reset_output_buffer()
ser1.reset_input_buffer()
data = ser1.readline()
ser1.reset_input_buffer()

nmea183 = rxgps()                # wait nmea rx for datetime synchronization
stringa = nmea183.split(',')
datetime = stringa[0]
ora = string[1]
gg = datetime[0:2]
mm = datetime[2:4]
aa = datetime[4:6]
hh = time[0:2]
mi = time[2:4]
ss = time[4:6]
if (len(hh) < 2):
    hh = "0" + hh
syncgps = mm+gg+hh+mi+"20"+aa+"."+ss      
# synchronize date and time with GPS (including time zone)
#print (syncgps)
synctime_gps(syncgps)

#---------------------------------------------------------------------------------
gapreg = 0                      # interval between two recordings
registra = 0
ctrsec = 0                      # counter in seconds for writing from RAM to SD
ctrbatlow = 0                   # low battery counter in seconds
usbloop = 0
esito = True
graph1= ["null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null",
         "null","null","null","null","null","null","null","null","null","null"];
#------------------------------------------
while True:                               # infinite work cycle

    nmea183 = rxgps()
    time.sleep(0.03)
    ctrsec = ctrsec + 1                           
    ReadConfig()

    if (GPIO.input(25) == 0):                     # START / STOP button test
        press = 1
        for k in range (5):
            time.sleep(0.02)
            if (GPIO.input(25) == 1):
                press = 0
        if (press == 1):        
            if (record == 1):
                record = 0
                lcd_string("IDL",LCD_LINE_4,17)
                ram2sd()
                ReadNet()
                if (enableftp == "1"):
                    sendfileftp(filestore)
            else:
                lcd_string("REG",LCD_LINE_4,17)
                filestore = nomefile
                ctrsec = 0
                gapreg = 0
                f = open(filestore, "w")     # open new storage file
                myinit = 'Date,Time,Latitude,N/S,Longitude,E/W,Altitude,NumSat,'
                          +ch1+','+ch2+','+ch3+','+ch4+','+ch5+','+ch6+'\n' 
                f.write(myinit)
                f.close()
                registra = 1
        waitril(25)                           # waiting for button release
    
    gg = datetime[0:2]                        # prepare date for viewing
    mm = datetime[2:4]
    aa = datetime[4:6]
    datanow = gg+"/"+mm+"/20"+aa
    
    hh = time[0:2]                             # prepare now for viewing
    mi = time[2:4]
    ss = time[4:6]
    oranow = hh+":"+mi+":"+ss

    ADC_Value = ADC.ADS1256_GetAll()          # acquire voltages from converter
    volt0 = round(ADC_Value[0]*5.0/0x7fffff*float(mul1)+float(add1),6) # Vbatt
    volt1 = round(ADC_Value[1]*5.0/0x7fffff*float(mul2)+float(add2),6) # Temp
    volt2 = round(ADC_Value[2]*5.0/0x7fffff*float(mul3)+float(add3),6)
    volt3 = round(ADC_Value[3]*5.0/0x7fffff*float(mul4)+float(add4),6) # lum.
    volt4 = round(ADC_Value[4]*5.0/0x7fffff*float(mul5)+float(add5),6)
    volt5 = round(ADC_Value[5]*5.0/0x7fffff*float(mul6)+float(add6),6) # em38

    volt1 = 1.585 - volt1
    volt1 = round(volt1 / 8.2 *1024, 2)
    
    mydatafile = datanow+','+oranow+','+lat+','+ns+','+lon+','+eo+','+alt+',
                 '+sat+','+str(volt0)+','+str(volt1)+','+str(volt2)+',
                 '+str(volt3)+','+str(volt4)+','+str(volt5)
    mydatafile = mydatafile + '\n'

    visualizza(2)

    if (record == 1):
        gapreg = gapreg + 1             # test if time to record
        if (gapreg >= gapprog):
            gapreg = 0
            f = open(fileswap, "a")     # update ram file for swap on SD
            f.write(mydatafile)
            f.close()
        if (ctrsec >= 60):              # time in sec. between SD storages
            ctrsec = 0
            ram2sd()
    else:
        destination = pathusb + "test.txt"
        try:
            f = open(destination, "w")
        except:
            usbloop = 0
        else:
            if (usbloop != 10):
                f.close()
                view (4)
                outcome = file2usb()
                sleep(2)
                if (outcome):
                    view(5)
                else:
                    view(6)
                sleep(5)
                usbloop = 10

    f = open(fileram, "w")        # update ram file for realtime
    f.write(mydatafile)
    f.close()

    graph1.append(graph1.pop(0))
    if (realtimech == "1"):
        graph1[99] = volt0
    elif (realtimech == "2"):
        graph1[99] = volt1
    elif (realtimech == "3"):
        graph1[99] = volt2
    elif (realtimech == "4"):
        graph1[99] = volt3
    elif (realtimech == "5"):
        graph1[99] = volt4
    elif (realtimech == "6"):
        graph1[99] = volt5
    f = open(filegraph1, "w")       # update ram file for graph
    f.write(str(graph1))
    f.close()

#---
    if (volt0 < vbatshutdown):      # low battery test for at least X seconds
        ctrbatlow = ctrbatlow + 1
        GPIO.output(13,GPIO.LOW)    # turn off LCD backlight
        if (ctrbatlow >= 20):       # yes
            ram2sd()
            view(3)           # closing message
            sleep(3)
            os.system("shutdown -h now")
            break
    else:
        ctrbatlow = 0
        GPIO.output(13,GPIO.HIGH)   # turn on LCD backlight

# end loop while
#------------------------------------------
view(3)            # closing message
GPIO.output(13,GPIO.LOW) # turn off LCD backlight
f.close()
ser.close()
GPIO.cleanup()

Zone