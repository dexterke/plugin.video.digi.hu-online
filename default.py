#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# 2018 Dexterke, SECRET LABORATORIES  <dexterkexnet@yahoo.com>
####################################################

import HTMLParser
import os
import re
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import time
import requests
import threading

## Settings
settings = xbmcaddon.Addon(id='plugin.video.digi.hu-online')
cfg_dir = xbmc.translatePath(settings.getAddonInfo('profile'))
login_User = settings.getSetting('login_User')
login_Password = settings.getSetting('login_Password')
debug_Enabled = settings.getSetting('debug_Enabled')
osdInfo_Enabled = settings.getSetting('popup_Enabled')

mainHost = 'digionline.hu'
digiHost = 'online.digi.hu'
wwwebURL = 'https://digionline.hu'
loginURL = 'https://digionline.hu/login'
userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15'
session = None
conn_type = 'close'
#conn_type = 'keep-alive'
pollTimer = 300
log_File   = os.path.join(cfg_dir, 'plugin_video_digionline.hu.log')
html_f_1   = os.path.join(cfg_dir, str(mainHost) + '_1.html')
html_f_2   = os.path.join(cfg_dir, str(mainHost) + '_2.html')
html_f_3   = os.path.join(cfg_dir, str(mainHost) + '_3.html')
playlist   = os.path.join(cfg_dir, 'playList.m3u8')
playFile   = os.path.join(cfg_dir, 'playFile.url')
epochTst   = os.path.join(cfg_dir, 'epoch.txt')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')
addon_thumb = os.path.join(settings.getAddonInfo('path'), 'icon.png')
addon_fanart = os.path.join(settings.getAddonInfo('path'), 'fanart.jpg')
header = {
  'Host': mainHost,
  'Connection': conn_type,
  'Upgrade-Insecure-Requests': '1',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'User-Agent': userAgent,
  'Accept-Language': 'en-ie',
  'DNT': '1',
  'Accept-Encoding': 'identity',
  }


def setIcon(thumb_file):
  thumb_file_name = thumb_file.replace(' ', '')[:-4].upper()
  try:
    thumb_file_name = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', thumb_file)
  except:
    thumb_file_name = movies_thumb
  return thumb_file_name


def ROOT():
  addDir('AMC', 'https://digionline.hu/player/243', setIcon('amc.png'))
  addDir('Cool TV', 'https://digionline.hu/player/245', setIcon('cool-tv.png'))
  addDir('Paramount Channel', 'https://digionline.hu/player/282', setIcon('paramount-channel.png'))
  addDir('FEM', 'https://digionline.hu/player/257', setIcon('fem3.png'))
  addDir('Film +', 'https://digionline.hu/player/259', setIcon('film.png'))
  addDir('Mozi +', 'https://digionline.hu/player/271', setIcon('mozi.png'))
  addDir('PRIME', 'https://digionline.hu/player/284', setIcon('prime.png'))
  addDir('Comedy Central', 'https://digionline.hu/player/244', setIcon('comedy-central.png'))
  addDir('Humor +', 'https://digionline.hu/player/262', setIcon('humor.png'))
  addDir('Izaura TV', 'https://digionline.hu/player/263', setIcon('izaura.png'))
  addDir('Sorozat +', 'https://digionline.hu/player/301', setIcon('sorozat.png'))
  addDir('Film Now', 'https://digionline.hu/player/258', setIcon('film-now.png'))

  addDir('RTL Gold', 'https://digionline.hu/player/242', setIcon('rtl-gold.png'))
  addDir('RTL Spike', 'https://digionline.hu/player/285', setIcon('rtl-spike.png'))
  addDir('RTL II', 'https://digionline.hu/player/286', setIcon('rtlii.png'))
  addDir('RTL +', 'https://digionline.hu/player/302', setIcon('rtlp.png'))
  addDir('SuperTV2', 'https://digionline.hu/player/291', setIcon('supertv2.png'))
  addDir('TV2 HD', 'https://digionline.hu/player/297', setIcon('tv2-hd.png'))
  addDir('Duna HD', 'https://digionline.hu/player/253', setIcon('duna-hd.png'))
  addDir('Duna World', 'https://digionline.hu/player/254', setIcon('duna-world-hd.png'))
  addDir('M1 HD', 'https://digionline.hu/player/266', setIcon('m1-hd.png'))
  addDir('M2 HD', 'https://digionline.hu/player/267', setIcon('m2-hd.png'))
  addDir('M5 HD', 'https://digionline.hu/player/269', setIcon('m5-hd.png'))

  addDir('Spektrum', 'https://digionline.hu/player/288', setIcon('spektrum.png'))
  addDir('Digi Life', 'https://digionline.hu/player/247', setIcon('digi-life.png'))
  addDir('Digi World', 'https://digionline.hu/player/251', setIcon('digi-world.png'))
  addDir('TLC', 'https://digionline.hu/player/295', setIcon('tlc.png'))
  addDir('TV Paprika', 'https://digionline.hu/player/296', setIcon('tv-paprika.png'))
  addDir('Lichi TV', 'https://digionline.hu/player/265', setIcon('lichi-tv.png'))
  addDir('Discovery Channel ', 'https://digionline.hu/player/252', setIcon('discovery-channel.png'))
  addDir('Nat. Geographic', 'https://digionline.hu/player/276', setIcon('nat-geo-hd.png'))
  addDir('Nat. Geo. Wild', 'https://digionline.hu/player/278', setIcon('nat-geo-wild-hd.png'))
  addDir('Digi Animal World', 'https://digionline.hu/player/246', setIcon('digi-animal-world.png'))
  addDir('History Channel', 'https://digionline.hu/player/261', setIcon('history.png'))
  addDir('Viasat History', 'https://digionline.hu/player/298', setIcon('viasat-history.png'))
  addDir('Viasat Nature', 'https://digionline.hu/player/299', setIcon('viasat-nature.png'))

  ## Kidz
  addDir('Nickelodeon', 'https://digionline.hu/player/281', setIcon('nickelodeon.png'))
  addDir('Minimax', 'https://digionline.hu/player/270', setIcon('minimax-c8.png'))
  addDir('Kiwi TV', 'https://digionline.hu/player/264', setIcon('kiwi-tv.png'))
  # 'M2' could be here

  ## Music
  addDir('Hit Music Channel', 'https://digionline.hu/player/260', setIcon('h-t-music-channel.png'))
  addDir('Music Channel', 'https://digionline.hu/player/274', setIcon('music-channel.png'))
  addDir('MTV Hungary', 'https://digionline.hu/player/272', setIcon('mtv-europe.png'))
  addDir('Zenebutik', 'https://digionline.hu/player/300', setIcon('zenebutik.png'))
  addDir('Sláger TV', 'https://digionline.hu/player/287', setIcon('slager-tv.jpg'))
  addDir('Muzsika TV', 'https://digionline.hu/player/275', setIcon('muzsika-tv.png'))

  ## Sport
  addDir('M4 Sport', 'https://digionline.hu/player/268', setIcon('m4-sport-hd.png'))
  addDir('Digi Sport 1', 'https://digionline.hu/player/248', setIcon('digi-sport-1-hd.png'))
  addDir('Digi Sport 2', 'https://digionline.hu/player/249', setIcon('digi-sport-2-hd.png'))
  addDir('Digi Sport 3', 'https://digionline.hu/player/250', setIcon('digi-sport-3-hd.png'))
  addDir('Eurosport 1', 'https://digionline.hu/player/255', setIcon('eurosport-hd.png'))
  addDir('Eurosport 2', 'https://digionline.hu/player/256', setIcon('eurosport-2-hd.png'))
  addDir('SPORT1', 'https://digionline.hu/player/289', setIcon('sport1.png'))
  addDir('SPORT2', 'https://digionline.hu/player/290', setIcon('sport2.png'))
  addDir('The Fishing & Hunting', 'https://digionline.hu/player/292', setIcon('the-fishing-amp-hunting-hd.jpg'))


def addDir(name, url, iconimage):
    iconimage = urllib.unquote(urllib.unquote(iconimage))
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&name=" + urllib.quote_plus(name) + "&thumb=" + urllib.quote_plus(iconimage)
    listedItem = xbmcgui.ListItem(name, path=u, iconImage=movies_thumb, thumbnailImage=iconimage)
    listedItem.setInfo('video', {'type': 'video', 'mediatype': 'video', 'genre': 'Live Stream', 'title': name, 'playcount': '0'})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=listedItem, isFolder=False)
    write2file(log_File, "addDir: '" + name + "', '" + url + "', '" + iconimage, 'a', 0, 0, 0)
    ##
    return ok


def getParams():
  param = []
  paramstring = sys.argv[2]
  if len(paramstring) >= 2:
      params = sys.argv[2]
      cleanedparams = params.replace('?', '')
      if (params[len(params) - 1] == '/'):
	  params = params[0:len(params) - 2]
      pairsofparams = cleanedparams.split('&')
      param = {}
      for i in range(len(pairsofparams)):
	  splitparams = {}
	  splitparams = pairsofparams[i].split('=')
	  if (len(splitparams)) == 2:
	      param[splitparams[0]] = splitparams[1]
  #-----------------------------------------------------------------------------------------------------------
  #'url': 'http%3A%2F%2Fdigionline.hu%2Ftv%SOME%2Btv%2F', 'name': 'SOME+TV'
  #-----------------------------------------------------------------------------------------------------------
  write2file(log_File, "getParams: " + str(param) , 'a', 0, 1, 0)
  ##
  return param


def getNowPlayingInfo(html_text):
    nowPlaying = ''
    try:
	## Extract 'now-playing' title
	myInfo = re.compile('<div class="col-xs-10 col-sm-9 col-md-9 col-lg-9 program__program_name">\n[\s]+([őöüóúőéáűíŐÖÜÓÚŐÉÁŰÍA-Za-z0-9\t\s\-\)(`;:.!,]+)<\/div>').findall(html_text)
	nowPlaying = str(myInfo[0].split("\n")[0])
	write2file(log_File, "getNowPlayingInfo nowPlaying: " + nowPlaying, 'a', 0, 0, 0)
    except Exception as err:
	write2file(log_File, "getNowPlayingInfo ERROR: " + str(err), 'a', 0, 1, 0)
    ##
    return nowPlaying


## Load HTML, extract playlist URL & 'now playing' info
def processHTML(url):
    global session
    global result
    global nowPlaying_Info
    f = HTMLParser.HTMLParser()
    url = f.unescape(url)
    req = None
    match = None
    token = None
    link = None

    write2file(log_File, "processHTML received URL: " + url, 'a', 1, 0, 0)
    ################### Step 1 #########################
    ## Load login URL to acquire cookies
    headers = {
      'Connection': conn_type,
      'Upgrade-Insecure-Requests': '1',
      'Referer': loginURL,
      'User-Agent': userAgent,
      'Origin': wwwebURL,
      'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
      'Accept-Encoding': 'identity',
      'Accept-Language': 'en-ie',
      'X-Requested-With': 'XMLHttpRequest',
      'DNT': '1',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Host': mainHost
	}
    try:
	session = requests.Session()
	req = session.get(loginURL, headers=headers)
	log_http(loginURL, req, 'GET')
	write2file(html_f_1, req.content, 'w', 0, 0, 0)
	## Get _token for next HTTP Header
	match = re.compile('name="_token" value="(.+?)"').findall(req.content)
	write2file(log_File, 'processHTML match: ' + str(match[0]), 'a', 0, 0, 0)
    except Exception as err:
	write2file(log_File, "processHTML ERROR: could not fetch " + str(loginURL) + " - " + str(err), 'a', 0, 1, 0)
	xbmcgui.Dialog().ok('Error', 'Could not fetch ' + str(loginURL) + " - " + str(err))

    ################### Step 2 #########################
    ## Login
    if match is not None and req.status_code == 200 :
      xbmc.executebuiltin("Notification(Digi-Online.hu, " + nowPlayingTitle + ")")
      headers = {
	'Host': mainHost,
	'Accept': '*/*',
	'X-Requested-With': 'XMLHttpRequest',
	'Accept-Language': 'en-ie',
	'Accept-Encoding': 'identity',
	'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Origin': wwwebURL,
	'User-Agent': userAgent,
	'Referer': loginURL,
	'DNT': '1',
	'X-CSRF-TOKEN': str(match[0]),
	'Connection': conn_type
	}
      try:
	  req = session.post(loginURL, headers=headers, data={'email': login_User, 'password': login_Password, 'accept': '1' })
	  sp_code = req.status_code
	  log_http(loginURL, req, 'POST')
	  write2file(html_f_2, req.content, 'w', 0, 0, 0)
      except Exception as err:
	xbmcgui.Dialog().ok('Error', 'Could not perfom login: ' + str(err))
	write2file(log_File, "processHTML ERROR: Could not perform login: " + str(err), 'a', 0, 1, 0)

      if sp_code != 200:
	    write2file(log_File, "processHTML ERROR: Could not perfom login: HTTP code: " + str(sp_code), 'a', 0, 1, 0)
	    xbmcgui.Dialog().ok('Error', 'Could not perfom login: HTTP code ' + str(sp_code))
      else:
	try:
	  ## Extract _token
	  token = re.compile('name="_token" value="(.+?)"').findall(req.content)
	  write2file(log_File, "processHTML token: " + str(token[0]), 'a', 0, 0, 0)
	except Exception as err:
	    write2file(log_File, "processHTML ERROR: Could not perform login: regex" + str(err), 'a', 0, 1, 0)
	    xbmcgui.Dialog().ok('Error', 'Could not perfom login: regex ' + str(err))

    ################### Step 3 #########################
    ## Load URL
    if token is not None and sp_code == 200:
      try:
	  req = session.get(url, headers=header)
	  html_text_data_3 = req.content
	  log_http(url, req, 'GET')
	  write2file(html_f_3, req.content, 'w', 0, 0, 0)

	  if req.status_code != 200:
	      write2file(log_File, "processHTML ERROR: could not fetch " + str(url) + ", HTTP Code " + str(req.status_code), 'a', 0, 1, 0)
	      xbmcgui.Dialog().ok('Error', 'Could not fetch ' + str(url) + "\nHTTP code " + str(req.status_code))
      except:
	  write2file(log_File, "processHTML ERROR: could not fetch " + str(url), 'a', 0, 1, 0)
	  xbmcgui.Dialog().ok('Error', 'Could not fetch ' + str(url))

      nowPlaying_Info = getNowPlayingInfo(html_text_data_3)
      if req.status_code == 200:
	## Extract 'Restricted Access' warning, some channels require premium subscription
	if re.compile('<div class="modal-body">Nem rendelkezik előfizetéssel az adás megtekintésére.<\/div>').findall(html_text_data_3):
	  write2file(log_File, "processHTML Warning: Access Restricted (Nem rendelkezik ... blabla)", 'a', 0, 1, 0)
	  xbmcgui.Dialog().ok('Warning', 'Nem rendelkezik előfizetéssel az adás megtekintésére')

	try:
	    ## Search for the playlist in the returned HTML document
	    ## e.g. createDefaultPlayer('https://online.digi.hu/api/streams/playlist/42/72cb73b6274e93e15b8e1d435f4ad235.m3u8',channel,'https://online.digi.hu/api/feedback','');
	    regxp = re.compile('(https:\/\/[A-Za-z0-9.\/]+.m3u8)').findall(html_text_data_3)
	    link = str(regxp[0])
	    write2file(log_File, "processHTML regxp: " + str(regxp), 'a', 0, 1, 0)

	    if "https://" not in link:
	      link = "".join(("https:", link))
	except:
	    write2file(log_File, "processHTML ERROR: could not detect playlist URL", 'a', 0, 1, 0)
	    xbmcgui.Dialog().ok('Error', 'could not detect playlist URL')

	################### Step 4 #########################
	## Acquire playlist
	if link is not None:
	  headers = {
	    'Host': digiHost,
	    'DNT': '1',
	    #'X-Playback-Session-Id': '56AFC239-C047-44BC-868F-038B28C79F25',
	    'Accept-Language': 'en-ie',
	    'Upgrade-Insecure-Requests': '1',
	    'Accept': '*/*',
	    'User-Agent': userAgent,
	    'Referer': wwwebURL,
	    'Accept-Encoding': 'identity',
	    'Connection': conn_type
	    }
	  try:
	      req = session.get(link, headers=headers)
	      result = req.content
	      log_http(link, req, 'GET')
	      write2file(log_File, "----- --- Playlist" + '\n' + req.content + "----- END Playlist", 'a', 0, 0, 0)
	      write2file(playlist, req.content, 'w', 0, 0, 0)
	      write2file(playFile, url, 'w', 0, 0, 1)
	  except:
	      write2file(log_File, "processHTML ERROR: could not acquire playlist", 'a', 0, 1, 0)
	      xbmcgui.Dialog().ok('Error', 'Could not acquire playlist')
	      return False
      ##
      return link


def parseInput(url):
    global result
    result = None
    item = None
    logMyVars()
    write2file(log_File, "parseInput received URL: " + url, 'a', 0, 0, 0)
    link = processHTML(url)

    ## Build ListItem
    if result is not None:
      try:
	item = xbmcgui.ListItem(path=link, iconImage=addon_thumb, thumbnailImage=nowPlayingThumb)
	item.setInfo('video', {'mediatype': 'video', 'type': 'video', 'genre': 'Live Stream', 'title': nowPlayingTitle + ' - ' + nowPlaying_Info, 'playcount': '1' })
	item.setLabel(nowPlayingTitle)
	item.setLabel2(nowPlaying_Info)
	write2file(log_File, "parseInput link: " + str(link), 'a', 0, 1, 0)
      except:
	write2file(log_File, "parseInput: Could not access media", 'a', 0, 1, 0)
	xbmcgui.Dialog().ok('Error', 'Could not access media')

    ################### Step 5 #########################
    ## Play stream
    if item is not None and result is not None:
      write2file(log_File, "xbmc.Player().play(" + link + ", item)", 'a', 0, 1, 0)
      xbmcplugin.setContent(int(sys.argv[1]), 'videos')
      xbmc.Player().play(link, item)
      if osdInfo_Enabled == "true":
	xbmc.executebuiltin("Notification(" + nowPlayingTitle + ", " + nowPlaying_Info + ")")

      time.sleep(60)
      curr = current()
      if curr is not None:
	try:
	  write2file(log_File, "XBMC now playing: '" + str(curr) + "'", 'a', 1, 1, 0)
	  pollThread = threading.Thread(name=url, target=poller, args=())
	  pollThread.start()
	except Exception as err:
	  write2file(log_File, "err: " + str(err), 'a', 1, 1, 0)


def current():
    try:
        return xbmc.Player().getPlayingFile()
    except RuntimeError:
        return None


def loadURL(url):
      global session
      try:
	  req = session.get(url, headers=header)
	  html_text = req.content
	  info = getNowPlayingInfo(html_text)
	  item = xbmcgui.ListItem()
	  item.setPath(xbmc.Player().getPlayingFile())
	  item.setLabel(nowPlayingTitle)
	  item.setLabel2(info)
	  item.setInfo('video', {'mediatype': 'video', 'type': 'video', 'genre': 'Live Stream', 'title': nowPlayingTitle + ' - ' + info, 'playcount': '1' })
	  try:
	      xbmc.Player().updateInfoTag(item)
	  except Exception as err:
	      write2file(log_File, "loadURL xbmc.Player().ERROR: " + str(err), 'a', 0, 1, 0)

	  if req.status_code != 200:
	      write2file(log_File, "loadURL ERROR: could not fetch " + str(url) + ", HTTP Code " + str(req.status_code), 'a', 0, 1, 0)
      except Exception as err:
	  write2file(log_File, "loadURL ERROR: " + str(err), 'a', 0, 1, 0)


def poller():
    cnt = 0
    now = int(time.time())
    epoch = None
    write2file(epochTst, str(now), 'w', 0, 0, 1)
    while True:
      cnt+=1
      try:
	  with open(epochTst, 'r') as file:
	    epoch = file.read().replace('\n', '')
      except:
	break

      curr = current()
      if curr is not None:
	if (str(now) == str(epoch)) and (digiHost in curr):
	  text = None
	  try:
	    with open(playFile, 'r') as file:
		text = file.read().replace('\n', '')
	    if text is not None:
		time.sleep(1)
	    if cnt == pollTimer:
	      link = loadURL(text)
	      cnt = 0
	  except Exception as err:
	    break
	else:
	  write2file(log_File, "poller closing: URL changed, now: " + str(now) + ", epoch: " + str(epoch) + ", curr: " + str(curr), 'a', 0, 1, 0)
	  break
      else:
	write2file(log_File, "poller closing: player stopped, now: " + str(now) + ", epoch: " + str(epoch) + ", curr: " + str(curr), 'a', 0, 1, 0)
	break


## Debug
def write2file(myFile, text, append, header, footer, force):
    ## append: w = write, a = append
    if debug_Enabled == "true" or force:
      try:
	  file = open(myFile, append)
	  if header:
	    file.write('-------------------------------------------- ' + '\n')
	  file.write(text)
	  if footer:
	    file.write('\n' + '-------------------------------------------- ')
	  file.write('\n')
	  file.close()
      except IOError:
	xbmcgui.Dialog().ok('Error', 'Could not write to logfile')


## Debug
def log_http(link, session, method):
  text = "processHTML HTTP " + method + " " + link + "\n" + "processHTML status_code: " + str(session.status_code) + "\n"
  for cookie in (session.cookies):
    text = text + "processHTML cookie: " + str(cookie.__dict__) + '\n'
  write2file(log_File, text, 'a', 0, 1, 0)


## Blabla & cleanup
def logMyVars():
  if debug_Enabled == "true":
    text = "osdInfo_Enabled: " + str(osdInfo_Enabled) + "\nuserAgent: " + userAgent
    write2file(log_File, text + '\nUser: ' + str(login_User) + '\nPasswd: ' + str(login_Password), 'w', 1, 1, 0)
  else:
    try:
      if os.path.isfile(log_File):
	os.remove(log_File)
      if os.path.isfile(html_f_1):
	os.remove(html_f_1)
      if os.path.isfile(html_f_2):
	os.remove(html_f_2)
      if os.path.isfile(html_f_3):
	os.remove(html_f_3)
      if os.path.isfile(playlist):
	os.remove(playlist)
    except:
      xbmcgui.Dialog().ok('Error', 'Could not clean logs')


####################################################
#### RUN Addon ###
logMyVars()
params = getParams()
url = None
nowPlayingThumb = None
nowPlayingTitle = None
nowPlaying_Info = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass

try:
  nowPlayingTitle = urllib.unquote_plus(params["name"])
except:
  nowPlayingTitle = str(url)

try:
  nowPlayingThumb = urllib.unquote_plus(params["thumb"])
except:
  nowPlayingThumb = movies_thumb

if url is None or len(url) < 1:
  ROOT()
else:
  parseInput(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]), updateListing=True)
