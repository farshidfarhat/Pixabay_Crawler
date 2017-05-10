import os
import re
import sys
import time
import json
import errno
import random
import socket
#import fcntl
import struct
import signal
import urllib
import requests
import urllib
from random import randint
from pathlib import Path
from flask import Flask,render_template,request
from bs4 import BeautifulSoup
from StringIO import StringIO
#from fhp.api.five_hundred_px import *
#from fhp.helpers.authentication import *

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def initialize():
	signal.signal(signal.SIGINT , signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)
	signal.signal(signal.SIGSEGV, signal_handler)
	try:
		thip = open(sys.argv[1]+"thiplist.tmp", 'r');
		lines = thip.readlines()
		thip.close()
		notme = 0;
		for line in lines:
			print(line)
			if(line == whoami+"\n"):
				notme = 1;
				break
		if(notme == 1):
			print("There is a similar thread on the line!")
			sys.exit()
	except IOError:
		print("There is no thiplist.tmp!")
	with open(sys.argv[1]+"thiplist.tmp", 'a') as thip:
		thip.write(whoami+"\n")
		thip.close()

def finalize():
	global lock_path
	global lock_file
	with open(sys.argv[1]+"thiplist.tmp", 'r') as thip:
		lines = thip.readlines()
		thip.close()
	with open(sys.argv[1]+"thiplist.tmp", 'w') as thip:
		for line in lines:
			if(line != whoami+"\n"):
				thip.write(line)
		thip.close()
	if lock_file:
		#print("lock_file = "+str(lock_file))
		try:
			os.close(lock_file)
		except IOError:
			print("lock_path was closed before!")
		if (Path(lock_path).is_file()):
			os.remove(lock_path)
			print(" >>> "+lock_path+" removed!")
		lock_file = 0

def signal_handler(signal, frame):
	finalize()
	print(" >>> "+whoami+" STOPPED BY Ctrl+C!")
	sys.exit(0)

whoami = get_ip_address()  # '192.168.0.110'
#CONSUMER_KEY = get_consumer_key()
#CONSUMER_SECRET = get_consumer_secret()

def main():
	initialize()
	global imid
	global lock_path
	global lock_file
	lock_file = 0
	#api = FiveHundredPx(CONSUMER_KEY,CONSUMER_SECRET)
	#term_kw = sys.argv[2]
	#if(len(sys.argv) > 3): # if tags are fed
	#	tags_kw = sys.argv[3]
	#else:
	#	tags_kw = None
	pagenum = int(sys.argv[2])
	while pagenum > 0:
		lock_path = sys.argv[1]+str(pagenum)+".tmp"
		if not(Path(lock_path).is_file()):
			try:
				lock_file = os.open(lock_path, os.O_CREAT|os.O_EXCL|os.O_RDWR)
				url = "https://pixabay.com/en/photos/?image_type=photo&pagi="+str(pagenum)
				print url
				url_content = urllib.urlopen(url)
				soup = BeautifulSoup(url_content,'html.parser')
				hrefs = soup.find_all('a',attrs={'href': re.compile('/en/')})
				for link in hrefs:
					purl = 'https://pixabay.com' + link['href']
					print purl
					purl_content = urllib.urlopen(purl)
					psoup = BeautifulSoup(purl_content,'html.parser')
					pdlinks = psoup.find_all('input', attrs={'type':'radio','name':'download','data-perm':'check'})
					pdltags = psoup.find_all('p', attrs={'class':'tags'})
					if(len(pdlinks) == 2):
						pHR1 = sys.argv[1]+"original/"+pdlinks[0]['value']
						pHR2 = sys.argv[1]+"original/"+pdlinks[1]['value']
						pTAG = sys.argv[1]+"tags/"    +pdlinks[0]['value']+".txt"
						if not(Path(pHR1).is_file() or Path(pHR2).is_file()):# or Path(pTAG).is_file()):
							#lock_file = os.open(lock_path, os.O_CREAT|os.O_EXCL|os.O_RDWR)
							time.sleep(1+randint(0,2))
							print(whoami+" is downloading "+pdlinks[0]['value'])
							urllib.urlretrieve('https://pixabay.com/en/photos/download/' + pdlinks[0]['value'],pHR1)
							print(whoami+" is downloading "+pdlinks[1]['value'])
							urllib.urlretrieve('https://pixabay.com/en/photos/download/' + pdlinks[1]['value'],pHR2)
							#metafile = open(pTAG, 'w')
							#metafile.write(pdltags)
							#metafile.close()
						else:
							print(whoami+" is skipping "+pdlinks[0]['value']+" as redundant!")
					else:
						print(whoami+" is skipping "+str(link)+" as no photo link!")
				print(whoami+" has just finished page #"+str(pagenum)+"!")
				os.close(lock_file)
				lock_file = 0
				os.remove(lock_path)
			except IOError:
				print(whoami+" is skipping page #"+str(pagenum)+" as an exception!")
		else:
			print(whoami+" is skipping page #"+str(pagenum)+" as busy!")
		pagenum = pagenum + 1
	signal.pause()
	finalize()

if __name__ == '__main__':
	main()


