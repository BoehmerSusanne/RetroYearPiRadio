# -*- coding: utf-8 -*-
import glob
import random
import pygame 
import time
import RPi.GPIO as gpio
	
	
pygame.init()
pygame.mixer.init()


# Festlegung der Nutzung der vorgegebenen Nummerierung der GPIOs
gpio.setmode(gpio.BCM)

# Namen von True und False zum besseren Verständnis festlegen
HIGH = True  # 3,3V Pegel (high)
LOW  = False # 0V Pegel (low)

# Music Files 
noise = glob.glob("MP3/*.mp3")
soundfile1960 = glob.glob("MP3/1960/*.mp3")
soundfile1970 = glob.glob("MP3/1970/*.mp3")
soundfile1980 = glob.glob("MP3/1980/*.mp3")
soundfile1990 = glob.glob("MP3/1990/*.mp3")
soundfile2000 = glob.glob("MP3/2000/*.mp3")
soundfile2010 = glob.glob("MP3/2010/*.mp3")

isPause = False
playNext = False

lastPlayed = "LEER"
songPlayed = "LEER"

songCounter = 0


# Konfiguration Eingangskanal und GPIOs von Frequenz
CH 		= 0  # Analog/Digital-Channel
CLK     = 18 # Clock
DIN     = 24 # Digital in
DOUT    = 23 # Digital out
CS      = 25 # Chip-Select

# Konfiguration Eingangskanal und GPIOs von Volume
CH_V 	= 1  # Analog/Digital-Channel
CLK_V   = 18 # Clock
DIN_V   = 24 # Digital in
DOUT_V  = 23 # Digital out
CS_V    = 25 # Chip-Select


BACK 	= 16
PLAY 	= 20
FORWARD = 21

# Pin-Programmierung
gpio.setup(CLK,	 gpio.OUT)
gpio.setup(DIN,	 gpio.OUT)
gpio.setup(DOUT, gpio.IN)
gpio.setup(CS,   gpio.OUT)

gpio.setup(CLK_V,	 gpio.OUT)
gpio.setup(DIN_V,	 gpio.OUT)
gpio.setup(DOUT_V, gpio.IN)
gpio.setup(CS_V,   gpio.OUT)

gpio.setup(BACK,   gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(PLAY,   gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(FORWARD,gpio.IN, pull_up_down=gpio.PUD_UP)

############################################################################

# SCI Funktion
def getAnalogData(adCh, CLKPin, DINPin, DOUTPin, CSPin):
    # Pegel definieren
    gpio.output(CSPin,   HIGH)    
    gpio.output(CSPin,   LOW)
    gpio.output(CLKPin,  LOW)
        
    cmd = adCh
    cmd |= 0b00011000 # Kommando zum Abruf der Analogwerte des Datenkanals adCh

    # Bitfolge senden
    for i in range(5):
        if (cmd & 0x10): # 4. Bit prüfen und mit 0 anfangen
            gpio.output(DINPin, HIGH)
        else:
            gpio.output(DINPin, LOW)
        # Clocksignal negative Flanke erzeugen   
        gpio.output(CLKPin, HIGH)
        gpio.output(CLKPin, LOW)
        cmd <<= 1 # Bitfolge eine Position nach links verschieben
            
    # Datenabruf
    adchvalue = 0 # Wert auf 0 zurücksetzen
    for i in range(11):
        gpio.output(CLKPin, HIGH)
        gpio.output(CLKPin, LOW)
        adchvalue <<= 1 # 1 Postition nach links schieben
        if(gpio.input(DOUTPin)):
            adchvalue |= 0x01
    time.sleep(0.05)
    return adchvalue

############################################################################

def play(soundfile):
	global songCounter
	songCounter+=1
	if (songCounter >= len(soundfile)): 
		songCounter = 0
	global songPlayed, lastPlayed
	if (songPlayed is not None): 
		lastPlayed = songPlayed
	songPlayed = soundfile[songCounter]
	print("Play " + str(songPlayed))
	pygame.mixer.music.load(songPlayed)
	pygame.mixer.music.play()
	
def playLast(frequency):
	global songCounter
	songCounter-=1
	if (songCounter < 0):
		songCounter = 0
	elif (songCounter >= len(frequency)):
		songCounter = 0
	
	if (lastPlayed is not None and lastPlayed in frequency): 
		songPlayed = frequency[songCounter]
		print("Play " + str(songPlayed))
		pygame.mixer.music.load(songPlayed)
		pygame.mixer.music.play()
	else:
		pygame.mixer.music.rewind()
	
def pauseplay(isPause):
	if not isPause: 
		print("stoping")
		pygame.mixer.music.pause()
	else:
		print("resume")
		pygame.mixer.music.unpause()
	time.sleep(0.01)
	
	
############################################################################

	
	
while True:
	# Erster Start des Players
	if (not pygame.mixer.music.get_busy()):
		# setVolume
		volumeValue = getAnalogData(CH_V, CLK_V, DIN_V, DOUT_V, CS_V)
		pygame.mixer.music.set_volume(volumeValue*0.001)
		potiValue = getAnalogData(CH, CLK, DIN, DOUT, CS)
		print "Not busy"
		if (30 <= potiValue < 125):
			frequency = soundfile2010
			play(frequency)
		elif (135 <= potiValue < 180):
			frequency = soundfile2000
			play(frequency)
		elif (185 <= potiValue < 255):
			frequency = soundfile1990
			play(frequency)
		elif (265 <= potiValue < 320):
			frequency = soundfile1980
			play(frequency)
		elif (330 <= potiValue < 385):
			frequency = soundfile1970
			play(frequency)
		elif (395 <= potiValue < 445):
			frequency = soundfile1960
			play(frequency)
		elif (455 <= potiValue < 490):
			frequency = soundfile1950
			play(frequency)
		else:
			play(noise)
			#print("**************************************************")

	while(pygame.mixer.music.get_busy()):
		potiValue = getAnalogData(CH, CLK, DIN, DOUT, CS)
		time.sleep(0.0001)
		
		# Pause Button
		pauseButton = gpio.input(PLAY)
		if  pauseButton == 0:
			pauseplay(isPause)
			isPause = not isPause
			time.sleep(0.0001)
			
		#Next Button
		nextButton = gpio.input(FORWARD)
		if nextButton == 0:
			print "Next Song"
			isPause = False
			play(frequency)	
			time.sleep(0.0001)

		backButton = gpio.input(BACK)
		if backButton == 0:
			print "Last Song"
			isPause = False
			playLast(frequency)	
			time.sleep(0.0001)
		
		# setVolume
		volumeValue = getAnalogData(CH_V, CLK_V, DIN_V, DOUT_V, CS_V)
		print(volumeValue)
		pygame.mixer.music.set_volume(volumeValue*0.001)
		
		
		# Änderung der Jahreszahlen
		diff = abs(potiValue - getAnalogData(CH, CLK, DIN, DOUT, CS))
		if not isPause and diff > 10: 
			#print "alt Poti " + str(potiValue) + " vs neuer " + str(getAnalogData(CH, CLK, DIN, DOUT, CS)) + "  DIFF: " + str(diff)

			if (30 <= getAnalogData(CH, CLK, DIN, DOUT, CS) < 125):
				frequency = soundfile2010
				play(frequency)
			elif (135 <= getAnalogData(CH, CLK, DIN, DOUT, CS) < 180):
				frequency = soundfile2000
				play(frequency)
			elif (185 <= getAnalogData(CH, CLK, DIN, DOUT, CS) < 255):
				frequency = soundfile1990
				play(frequency)
			elif (265 <= getAnalogData(CH, CLK, DIN, DOUT, CS) < 320):
				frequency = soundfile1980
				play(frequency)
			elif (330 <= getAnalogData(CH, CLK, DIN, DOUT, CS) < 385):
				frequency = soundfile1970
				play(frequency)
			elif (395 <= getAnalogData(CH, CLK, DIN, DOUT, CS) < 445):
				frequency = soundfile1960
				play(frequency)
			elif (455 <= getAnalogData(CH, CLK, DIN, DOUT, CS) < 499):
				frequency = soundfile1950 
				play(frequency)
			else:
				play(noise)
				#print("**************************************************")
				


		
