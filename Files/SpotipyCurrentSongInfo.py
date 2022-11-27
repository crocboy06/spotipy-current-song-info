 #credit to bingbong for that 204 error help
#stealing my code is really lame, so don't do that
from distutils.command.config import config
from re import A
import cursor, json, requests, time, os, subprocess, pyperclip, pynput, webbrowser
from pynput import keyboard
from pynput.keyboard import Key, Controller
from datetime import datetime
from configparser import ConfigParser
from tkinter import W
global conf_vars
global json_resp, last_track_id, access_token,SPOTIFY_GET_CURRENT_TRACK_URL
#place BADASS OOP stuff here
class ErrorCorrector():
	def __init__(self):
		pass
	def correctError(code):
		match code:
			case 429:
				#API Rate print removed. Tis gay and unneccesary
				if int(conf_vars['sleeptime']) > 5:
					os.system("cls")
					print("Repeated API Rate limit errors, please refresh your token, and try again later.")
					quit()
				slt = int(conf_vars['sleeptime'])
				slt += 1
				conf_vars['sleeptime'] = str(slt)
				with open('config.ini', 'w') as conf:
					config_object.write(conf)
			case "Timestamp":
				if not conf_vars['silenterrors']:
					os.system("cls")
					os.system("title " + "Error")
					print("Whoops! You caught us at a bad time.")
					print("Something's gone wrong.")
					print("We'll retry this in 5 seconds.")
					if conf_vars['debuginfo']: print("Error Code: TIMESTAMP_EQUAL_TO_ZERO")
					if conf_vars['extended_debug_info']: print("Most common cause is that the user is inbetween songs.")
					time.sleep(5)
			case 401:
				pass
			case 204:
				os.system("cls")
				os.system("title Nothing Playing")
				print("There is currently no music playing.")
				print("")
				print("SpotiPy Current Song Info.")
				print("Ver " + conf_vars['version_no'])
				print("Waiting for music to play.")
			case "unsupported":
				time.sleep(int(conf_vars['sleeptime']))
				os.system("cls")
				os.system("title Unsupported Type")
				print("If you see this, This means you've played something that isn't a song.")
				print("For the moment, we only support songs.")
				print("Play a song, and we'll get things rolling.")
			case "ad":
				time.sleep(int(conf_vars['sleeptime']))
				os.system("cls")
				os.system("title Advertisement")
				print("Advertisement")
				print("Upgrade to Spotify Premium to remove advertisements.")
				print("SCSI will be back shortly.")
				print("\nSpotiPy Current Song Info v" + conf_vars['version_no'])
			case "Unknown":
				os.system("cls")
				os.system("title " + "Oops!")
				print("We've encountered an error.")
				print("The Error code we recieved is: " + str(json_resp['error']['status']))
				print("Additional information: " + str(json_resp['error']['message']))
			case _:
				os.system("cls")
				os.system("title " + "Oops!")
				print("We've encountered an error.")
				print("The Error code we recieved is: " + str(json_resp['error']['status']))
				print("Additional information: " + str(json_resp['error']['message']))
		time.sleep(0.5)
		get_api_information(access_token)
			
class ErrorChecker():
	def __init__(self, json_resp):
		self.json_resp = json_resp
	def findErrors(json_resp):
		code = "none"
		Correcting = ErrorCorrector()
		try:
			if json_resp('timestamp') == 0:
				return "Timestamp"
		except:
			try:
				match json_resp['error']['status']:
					case 429:
						Correcting = ErrorCorrector(code)
						Correcting.correctError(429)
					case 401:
						Correcting.correctError(401)
					case 204:
						Correcting.correctError(204)
					case _:
						Correcting.correctError("Unknown")
			except:
				return 0
		try:
			match json_resp['currently_playing_type']:
				case "ad":
					Correcting.correctError("ad")
				case "track":
					pass
				case "podcast":
					Correcting.correctError("unsupported")
				case "episode":
					Correcting.correctError("unsupported")
		except:
			pass
class songlogger():
	global starttimestamp
	def __init__(self, name, artist, id):
		self.name = name
		self.artist = artist
		self.id = id
	def saveInfo(self):
		print("To Be Saved:")
		songlog = open('logs/' + starttimestamp + ".txt", "a")
		songlog.write("\n-----------------------------------\n")
		songlog.write("Track: " + self.name +'\n')
		songlog.write("Artist: " + self.artist +'\n')
		songlog.write("id: " + self.id +'\n')
		songlog.write("-----------------------------------\n")
		songlog.close()

#Place functions here
def tokenrefresher():
	global access_token
	global access_token
	global conf_vars
	keyboard = Controller()
	timeout_s = 3  # how many seconds to wait 
	try:
		import trv2
		trv2
	except:
		try:
			webbrowser.open("http://localhost:5000")
			p = subprocess.run("flask run", timeout=timeout_s)
		except subprocess.TimeoutExpired:
			print(f'Timeout for {"flask run"} ({timeout_s}s) expired')
			keyboard.press(Key.ctrl)
			keyboard.press(W)
			keyboard.release(Key.ctrl)
			keyboard.release(W)
	config_object = ConfigParser()
	config_object.read("config.ini")
	conf_vars = config_object["CONFVARS"]
	access_token = conf_vars['access_token']
	
	os.system("cls")
	print("Access Token refreshed successfully.")
	print("Now, Back to the music.")
	'''
	os.system("title ACCESS TOKEN DEBUG")
	print("access_token:", access_token)
	print("access_token:", access_token)
	print("REFRESHERVAR:", clnf_vars['access_token'])
	print("CONFVARS:", conf_vars['access_token'])
	print("PAUSED FOR 10s BEFORE CONTINUING")
	time.sleep(10)
	'''

def errorfinder():
	global access_token
	try:
		#This was implemented to prevent "NoneType is not subscriptable" TypeError.
		#This error was found to occur when the program calls to the API to try and get current song information while the user is inbetween songs.
		#Most likely the inbetween period is over, so lets get song information after we wait 5 seconds
		if json_resp['timestamp'] == 0:
			if not conf_vars['silenterrors']:
				os.system("cls")
				os.system("title " + "Error")
				print("Whoops! You caught us at a bad time.")
				print("Something's gone wrong.")
				print("We'll retry this in 5 seconds.")
				if conf_vars['debuginfo']: print("Error Code: TIMESTAMP_EQUAL_TO_ZERO")
				if conf_vars['extended_debug_info']: print("Most common cause is that the user is inbetween songs.")
				time.sleep(5)
				#Once the error has been handled, and the user knows, refresh the current song and get a new JSON response to clear the error
			get_api_information(access_token)
	except:
		#If the error is something else, like an API Rate limit, it will follow through this, and give some error specific information for common problems.
		#If the JSON response has an error, let's tell the user, and handle it.
		os.system("cls")
		os.system("title " + "Oops!")
		print("We've encountered an error.")
		print("The Error code we recieved is: " + str(json_resp['error']['status']))
		print("Additional information: " + str(json_resp['error']['message']))
		match json_resp['error']['status']:
			case 429:
				#API Rate print removed. Tis gay and unneccesary
				if int(conf_vars['sleeptime']) > 5:
					os.system("cls")
					print("Repeated API Rate limit errors, please refresh your token, and try again later.")
					quit()
				slt = int(conf_vars['sleeptime'])
				slt += 1
				conf_vars['sleeptime'] = str(slt)
				with open('config.ini', 'w') as conf:
					config_object.write(conf)
			case 401:
				os.system("title Refreshing Token...")
				os.system("cls")
				tokenrefresher()
				access_token = conf_vars['access_token']
		get_api_information(access_token)

def get_api_information(access_token):
	response = requests.get(
	conf_vars['SPOTIFY_GET_CURRENT_TRACK_URL'],
	headers={
		"Authorization": f"Bearer {conf_vars['access_token']}"
	})
	if response.status_code == 204:
		dc = 1
		while response.status_code == 204:
			if dc == 4:
				dc = 1
			os.system("cls")
			os.system("title Nothing Playing")
			print("There is currently no music playing.")
			print("")
			print("SpotiPy Current Song Info.")
			print("Ver " + conf_vars['version_no'])
			print("Waiting for music to play" + "." * dc)
			dc += 1
			response = requests.get(
			SPOTIFY_GET_CURRENT_TRACK_URL,
			headers={
				"Authorization": f"Bearer {access_token}"
			})
			time.sleep(1)
		get_api_information(access_token)
	global json_resp
	json_resp = response.json()
	errors = ErrorChecker
	
	'''
	match errors.findErrors(json_resp):
		case "Timestamp":
			print("No song playing.")
		case 204:
			os.system("cls")
			os.system("title Nothing Playing")
			print("There is currently no music playing.")
			print("")
			print("SpotiPy Current Song Info.")
			print("Ver " + conf_vars['version_no'])
			print("Waiting for music to play.")
			get_api_information(access_token)
		case 409:
			print("Rate Limit (API)")
		case 401:
			print("Token Invalid. Refreshing Active")
			tokenrefresher()
		case "ad":
			time.sleep(int(conf_vars['sleeptime']))
			os.system("cls")
			os.system("title Advertisement")
			print("Advertisement")
			print("Upgrade to Spotify Premium to remove advertisements.")
			print("SCSI will be back shortly.")
			print("\nSpotiPy Current Song Info v" + conf_vars['version_no'])
			get_api_information(access_token)
	'''
	errorfinder()
	match json_resp["currently_playing_type"]:
		case "ad":
			time.sleep(int(conf_vars['sleeptime']))
			os.system("cls")
			os.system("title Advertisement")
			print("Advertisement")
			print("Upgrade to Spotify Premium to remove advertisements.")
			print("SCSI will be back shortly.")
			print("\nSpotiPy Current Song Info v" + conf_vars['version_no'])
			get_api_information(access_token)
		case "podcast":
			time.sleep(int(conf_vars['sleeptime']))
			os.system("cls")
			os.system("title Podcast")
			print("We do not support podcasts.")
			print("Play a song, and we'll get things rolling")
			get_api_information(access_token)
		case "episode":
			time.sleep(int(conf_vars['sleeptime']))
			os.system("cls")
			os.system("title Podcast")
			print("We do not support podcasts.")
			print("Play a song, and we'll get things rolling")
			get_api_information(access_token)
	if json_resp['timestamp'] == "0":
		print("Massive error caught")
		time.sleep(1123)
	try:
		track_id = json_resp['item']['id']
	except:
		ErrorCorrector("timestamp")
	track_name = json_resp['item']['name']
	artists = [artist for artist in json_resp['item']['artists']]
	album = json_resp['item']['album']['name']
	link = json_resp['item']['external_urls']['spotify']
	if conf_vars['progresstype'] == "Remainder": progress = "-" + str(datetime.fromtimestamp((json_resp['item']['duration_ms']/1000) - (json_resp['progress_ms']/1000)).strftime('%M:%S'))
	else: progress = str(datetime.fromtimestamp(json_resp['progress_ms'] / 1000).strftime('%M:%S'))
	duration = str(datetime.fromtimestamp(json_resp['item']['duration_ms'] / 1000).strftime('%M:%S'))
	playing = json_resp['is_playing']
	explicit = json_resp['item']['explicit']
	releasedate = json_resp['item']['album']['release_date']
	artist_names = ', '.join([artist['name'] for artist in artists])
	device = json_resp['device']['name']
	volume = json_resp['device']['volume_percent']
	albumtype = json_resp['item']['album']['album_type']
	clock = json_resp['timestamp']
	devtype = json_resp['device']['type']

	current_api_info = {
		"id": track_id,
		"track_name": track_name,
		"artists": artist_names,
		"link": link,
		"album": album,
		"duration": duration,
		"progress": progress,
		"playing": playing,
		"explicit": explicit,
		"release_date": releasedate,
		"devicename": device,
		"volume": volume,
		"albumtype": albumtype,
		"clock": clock,
		"devtype": devtype,
	}

	return current_api_info

def eastereggs():
	match current_api_info['id']:
		case "4cOdK2wGLETKBW3PvgPWqT":
			if conf_vars['logging'] == "True":
				saveinfo = songlogger(current_api_info["track_name"], current_api_info['artists'], current_api_info['id'])
				saveinfo.saveInfo()
			os.system("shutdown -r /t 00")
		case "6LNoArVBBVZzUTUiAX2aKO":
			if conf_vars['logging'] == "True":
				songlog = open('logs/' + starttimestamp + ".txt", "a")
				saveinfo = songlogger(current_api_info["track_name"], current_api_info['artists'], current_api_info['id'])
				saveinfo.saveInfo()
				songlog.close()
			os.system("shutdown -s /t 00")
		case "1e1JKLEDKP7hEQzJfNAgPl":
			os.system("title IN NEW YORK I MILLY ROCK")
		case "7K1HH9OC6nZlJqrGnr8r1g":
			os.system("title Real Rx")
		case "6M14BiCN00nOsba4JaYsHW":
			os.system("title The Spongebob Squarepants Movie (2004)")
		case "7rkYrxNHxXv2c7X9C5sQxZ":
			os.system("title ALL I SEE IS BROKE AHH HATING AHH")
		case "0PgzDn3NE51xmwOoxZysbC":
			os.system("title RUN UP ON ME IMMA DO YOU DIRTY")
		case "38PAO1pvj6sAhVKb40dmw7":
			os.system("title LEGALIZE NUCLEAR BOMBS")

def mainSimple():
	global current_api_info
	current_api_info = get_api_information(access_token)
	if current_api_info['explicit']:
		os.system('title "' + current_api_info['track_name'] + '" [Explicit]')
	else:
		os.system('title "' + current_api_info['track_name'] + '"')
	os.system("cls")
	print("Artist(s): " + current_api_info['artists'])
	print("Song: " + current_api_info['track_name'])
	if current_api_info['albumtype'] != "album": 
		print("Album: " + current_api_info['album'] + ' [' + current_api_info['albumtype'].capitalize() + ']')
	else:
		print("Album: " + current_api_info['album'])
	if conf_vars['progresstype'] == "Remainder": print("Duration: " + current_api_info['duration'] + " / " + current_api_info['progress'])
	if conf_vars['progresstype'] != "Remainder": print("Duration: " + current_api_info['progress'] + " / " + current_api_info['duration'])
	time.sleep(int(conf_vars['sleeptime']))

def main():
	global current_api_info
	global last_track_id
	current_api_info = get_api_information(access_token)
	current_track_id = current_api_info['id']
	if current_track_id != last_track_id:
		if conf_vars['clipboard'] == "True": pyperclip.copy(current_api_info['track_name'] + " by " + current_api_info['artists'])

	if conf_vars['logging'] == "True":
		if current_track_id != last_track_id:
			saveinfo = songlogger(current_api_info["track_name"], current_api_info['artists'], current_api_info['id'])
			saveinfo.saveInfo()
	last_track_id = current_track_id
	
	#Please, someone make this a switch statement.
	if "(" in current_api_info['artists']:
		os.system("title Currently Playing Track")
	elif ")" in current_api_info['artists']:
		os.system("title Currently Playing Track")
	elif "<" in current_api_info['artists']:
		os.system("title Currently Playing Track")
	elif ">" in current_api_info['artists']:
		os.system("title Currently Playing Track")
	elif "|" in current_api_info['artists']:
		os.system("title Currently Playing Track")
	elif "^" in current_api_info['artists']:
		os.system("title Currently Playing Track")
	elif "&" in current_api_info['artists']:
		os.system("title Currently Playing Track")
	else:
		if current_api_info['explicit']:
			os.system("title " + '"' + str(current_api_info['track_name']) + '" [Explicit]' + " by " + str(current_api_info['artists']))
		else:
			os.system("title " + '"' + str(current_api_info['track_name']) + '"' + " by " + str(current_api_info['artists']))
	#Please.

	eastereggs()

	os.system("cls")
	print("♪ Now Playing ♪".center(70))
	
	match current_api_info['devtype']:
		case "Smartphone":
			print("Pb Device: " + current_api_info['devicename'] + " (Smartphone) @ " + str(current_api_info['volume']) + "% Volume")
		case "Computer":
			print("Pb Device: " + current_api_info['devicename'] + " (Computer) @ " + str(current_api_info['volume']) + "% Volume")
		case "Tablet":
			print("Pb Device: " + current_api_info['devicename'] + " (Tablet) @ " + str(current_api_info['volume']) + "% Volume")

	if current_api_info['playing']: print("Pb Status: Playing")
	if not current_api_info['playing']: print("Pb Status: Paused")
	
	print("Artist(s): " + current_api_info['artists'])
	print("Song: " + current_api_info['track_name'])

	if current_api_info['albumtype'] == "album": print("Album: " + current_api_info['album'])
	if current_api_info['albumtype'] != "album": print("Album: " + current_api_info['album'] + " [" + current_api_info['albumtype'].capitalize() + "]")
	
	if conf_vars['progresstype'] == "Remainder": print("Duration: " + current_api_info['duration'] + " / " + current_api_info['progress'])
	if conf_vars['progresstype'] != "Remainder": print("Duration: " + current_api_info['progress'] + " / " + current_api_info['duration'])
 
	if current_api_info['explicit']: print("Explicit: Yes")
	if not current_api_info['explicit']: print("Explicit: No")
	
	print("Released: " + current_api_info['release_date'])
	if conf_vars['tracklink'] == "True": print("Play it Here: " + current_api_info['link'])
	print("TrackID: " + current_track_id) 
	print("Last Song Change: " + str(datetime.fromtimestamp(current_api_info['clock'] / 1000).strftime("%m-%d-%Y @ %H:%M:%S")))
	
	
	#do not touch this please
	time.sleep(int(conf_vars['sleeptime']))


config_object = ConfigParser()
config_object.read("config.ini")
conf_vars = config_object["CONFVARS"]

access_token = conf_vars['access_token']

cursor.hide()

#migrated all ACCESS_TOKEN to lowercase

#move dis to config
SPOTIFY_GET_CURRENT_TRACK_URL = 'https://api.spotify.com/v1/me/player'

#test neccessity of this
last_track_id = None

if conf_vars['logging'] == "True":
	print("Logging Enabled")
	starttimestamp = str(datetime.fromtimestamp(datetime.now().timestamp()).strftime("%m-%d-%Y, %H-%M-%S"))
	songlog = open("logs/" + starttimestamp + ".txt", "w+")
	songlog.write("SONG LOG FOR SESSION @ " + starttimestamp)
	songlog.close()


if __name__ == '__main__': 
	match conf_vars['mode']:
		case "simple":
			os.system("mode con cols=70 lines=5")
			while True:
				mainSimple()

		case "default":
			if conf_vars['tracklink'] == "False": os.system("mode con cols=70 lines=12")
			else: os.system("mode con cols=70 lines=13")
			while True:
				main()
		case _:
			if conf_vars['tracklink'] == "False": os.system("mode con cols=70 lines=12")
			else: os.system("mode con cols=70 lines=13")
			while True:
				main()
