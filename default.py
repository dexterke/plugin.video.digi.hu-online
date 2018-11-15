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
#import socket, ssl
import requests


## Settings
settings = xbmcaddon.Addon(id='plugin.video.digi.hu-online')
login_User = settings.getSetting('login_User')
login_Password = settings.getSetting('login_Password')
debug_Enabled = settings.getSetting('debug_Enabled')
osdInfo_Enabled = settings.getSetting('popup_Enabled')

mainHost = 'digionline.hu'
digiHost = 'online.digi.hu'
wwwebURL = 'http://digionline.hu'
loginURL = 'http://digionline.hu/login'
userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15'

conn_type = 'close'
#conn_type = 'keep-alive'

log_File = os.path.join(settings.getAddonInfo('path'), 'resources', 'plugin_video_digi.hu-online.log')
html_f_1 = os.path.join(settings.getAddonInfo('path'), 'resources', str(mainHost) + '_1.html')
html_f_2 = os.path.join(settings.getAddonInfo('path'), 'resources', str(mainHost) + '_2.html')
html_f_3 = os.path.join(settings.getAddonInfo('path'), 'resources', str(mainHost) + '_3.html')
playlist = os.path.join(settings.getAddonInfo('path'), 'resources', 'playList.m3u8')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')
addon_thumb = os.path.join(settings.getAddonInfo('path'), 'icon.png')
addon_fanart = os.path.join(settings.getAddonInfo('path'), 'fanart.jpg')


def setIcon(thumb_file):
  thumb_file_name = thumb_file.replace(' ', '')[:-4].upper()
  try:
    thumb_file_name = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', thumb_file)
  except:
    thumb_file_name = movies_thumb
  return thumb_file_name


def ROOT():
  addDir('AMC', 'http://digionline.hu/player/42', setIcon('amc.png'))
  addDir('Cool TV', 'http://digionline.hu/player/34', setIcon('cool-tv.png'))
  addDir('Paramount Channel', 'http://digionline.hu/player/35', setIcon('paramount-channel.png'))
  addDir('FEM', 'http://digionline.hu/player/206', setIcon('fem3.png'))
  addDir('Film +', 'http://digionline.hu/player/32', setIcon('film.png'))
  addDir('Mozi +', 'http://digionline.hu/player/214', setIcon('mozi.png'))
  addDir('PRIME', 'http://digionline.hu/player/225', setIcon('prime.png'))
  addDir('Comedy Central', 'http://digionline.hu/player/10', setIcon('comedy-central.png'))
  addDir('Humor +', 'http://digionline.hu/player/211', setIcon('humor.png'))
  addDir('Izaura TV', 'http://digionline.hu/player/212', setIcon('izaura.png'))
  addDir('Film Now', 'http://digionline.hu/player/232', setIcon('film-now.png'))

  addDir('RTL Klub', 'http://digionline.hu/player/37', setIcon('rtl-klub.png'))
  addDir('RTL Spike', 'http://digionline.hu/player/219', setIcon('rtl-spike.png'))
  addDir('RTL II', 'http://digionline.hu/player/29', setIcon('rtlii.png'))
  addDir('SuperTV2', 'http://digionline.hu/player/208', setIcon('supertv2.png'))
  addDir('TV2 HD', 'http://digionline.hu/player/204', setIcon('tv2-hd.png'))
  addDir('Duna HD', 'http://digionline.hu/player/43', setIcon('duna-hd.png'))
  addDir('Duna World', 'http://digionline.hu/player/44', setIcon('duna-world-hd.png'))
  addDir('M1 HD', 'http://digionline.hu/player/39', setIcon('m1-hd.png'))
  addDir('M2 HD', 'http://digionline.hu/player/42', setIcon('m2-hd.png'))
  addDir('M5 HD', 'http://digionline.hu/player/132', setIcon('m5-hd.png'))

  addDir('Spektrum', 'http://digionline.hu/player/130', setIcon('spektrum.png'))
  addDir('Digi Life', 'http://digionline.hu/player/12', setIcon('digi-life.png'))
  addDir('Digi World', 'http://digionline.hu/player/1', setIcon('digi-world.png'))
  addDir('TLC', 'http://digionline.hu/player/215', setIcon('tlc.png'))
  addDir('TV Paprika', 'http://digionline.hu/player/23', setIcon('tv-paprika.png'))
  addDir('Lichi TV', 'http://digionline.hu/player/227', setIcon('lichi-tv.png'))
  addDir('Discovery Channel ', 'http://digionline.hu/player/203', setIcon('discovery-channel.png'))
  addDir('Nat. Geographic', 'http://digionline.hu/player/220', setIcon('nat-geo-hd.png'))
  addDir('Nat. Geo. Wild', 'http://digionline.hu/player/222', setIcon('nat-geo-wild-hd.png'))
  addDir('Digi Animal World', 'http://digionline.hu/player/7', setIcon('digi-animal-world.png'))
  addDir('History Channel', 'http://digionline.hu/player/45', setIcon('history.png'))
  addDir('Viasat History', 'http://digionline.hu/player/4', setIcon('viasat-history.png'))
  addDir('Viasat Nature', 'http://digionline.hu/player/21', setIcon('viasat-nature.png'))

  ## Kidz
  addDir('Nickelodeon', 'http://digionline.hu/player/207', setIcon('nickelodeon.png'))
  addDir('Minimax', 'http://digionline.hu/player/226', setIcon('minimax-c8.png'))
  addDir('Kiwi TV', 'http://digionline.hu/player/213', setIcon('kiwi-tv.png'))

  ## Music
  addDir('Hit Music Channel', 'http://digionline.hu/player/2', setIcon('h-t-music-channel.png'))
  addDir('Music Channel', 'http://digionline.hu/player/5', setIcon('music-channel.png'))
  addDir('MTV Hungary', 'http://digionline.hu/player/228', setIcon('mtv-europe.png'))
  addDir('Zenebutik', 'http://digionline.hu/player/216', setIcon('zenebutik.png'))

  ## Sport
  addDir('M4 Sport', 'http://digionline.hu/player/41', setIcon('m4-sport-hd.png'))
  addDir('Digi Sport 1', 'http://digionline.hu/player/26', setIcon('digi-sport-1-hd.png'))
  addDir('Digi Sport 2', 'http://digionline.hu/player/27', setIcon('digi-sport-2-hd.png'))
  addDir('Digi Sport 3', 'http://digionline.hu/player/131', setIcon('digi-sport-3-hd.png'))
  addDir('Eurosport 1', 'http://digionline.hu/player/205', setIcon('eurosport-hd.png'))
  addDir('Eurosport 2', 'http://digionline.hu/player/210', setIcon('eurosport-2-hd.png'))
  addDir('SPORT1', 'http://digionline.hu/player/126', setIcon('sport1.png'))
  addDir('SPORT2', 'http://digionline.hu/player/118', setIcon('sport2.png'))
  #addDir('TEST', 'http://digionline.hu/player/13', setIcon('movies.png'))


def addDir(name, url, iconimage):
    iconimage = urllib.unquote(urllib.unquote(iconimage))
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&name=" + urllib.quote_plus(name) + "&thumb=" + urllib.quote_plus(iconimage)
    listedItem = xbmcgui.ListItem(name, iconImage=movies_thumb, thumbnailImage=iconimage)
    itemInfo = {
      'type': 'Video',
      'genre': 'Live Stream',
      'title': name,
      'playcount': '0'
	}
    listedItem.setInfo('video', itemInfo)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=listedItem)
    write2file(log_File, "addDir: '" + name + "', '" + url + "', '" + iconimage, 'a', 0, 0)
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
  write2file(log_File, "getParams: " + str(param) , 'a', 0, 1)
  return param


## Load HTML, extract playlist URL & 'now playing' info
def processHTML(url):
    global result
    global nowPlaying_Info
    global req
    req = None
    f = HTMLParser.HTMLParser()
    url = f.unescape(url)
    match = None
    token = None
    link = None

    write2file(log_File, "processHTML received URL: " + url, 'a', 1	, 0)
    ################### Step 1 #########################
    ## Load login URL to acquire cookies
    headers = {
      'Connection': conn_type,
      #'Content-Length': '54',
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
	write2file(html_f_1, req.content, 'w', 0, 0)
	## Get _token in order to add its value to the next HTTP Header
	match = re.compile('name="_token" value="(.+?)"').findall(req.content)
	write2file(log_File, "processHTML match: " + str(match[0]), 'a', 0, 0)

    except Exception as err:
	write2file(log_File, "processHTML ERROR: could not fetch " + str(loginURL) + " - " + str(err), 'a', 0, 1)
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
	#'Content-Length': '54',
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
	  write2file(html_f_2, req.content, 'w', 0, 0)

      except Exception as err:
	xbmcgui.Dialog().ok('Error', 'Could not perfom login: ' + str(err))
	write2file(log_File, "processHTML ERROR: Could not perform login: " + str(err), 'a', 0, 1)

      if sp_code != 200:
	    write2file(log_File, "processHTML ERROR: Could not perfom login: HTTP code: " + str(sp_code), 'a', 0, 1)
	    xbmcgui.Dialog().ok('Error', 'Could not perfom login: HTTP code ' + str(sp_code))

      else:
	try:
	  ## Check _token make sure we can go on
	  token = re.compile('name="_token" value="(.+?)"').findall(req.content)
	  write2file(log_File, "processHTML token: " + str(token[0]), 'a', 0, 0)

	except Exception as err:
	    write2file(log_File, "processHTML ERROR: Could not perform login: regex" + str(err), 'a', 0, 1)
	    xbmcgui.Dialog().ok('Error', 'Could not perfom login: regex ' + str(err))

    ################### Step 3 #########################
    ## Load URL
    if token is not None and sp_code == 200:
      headers = {
	'Host': mainHost,
	'Connection': conn_type,
	'Upgrade-Insecure-Requests': '1',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'User-Agent': userAgent,
	'Accept-Language': 'en-ie',
	'DNT': '1',
	'Accept-Encoding': 'identity',
	  }
      try:
	  req = session.get(url, headers=headers)
	  html_text_data_3 = req.content
	  log_http(url, req, 'GET')
	  write2file(html_f_3, req.content, 'w', 0, 0)

	  if req.status_code != 200:
	      write2file(log_File, "processHTML ERROR: could not fetch " + str(url) + ", HTTP Code " + str(req.status_code), 'a', 0, 1)
	      xbmcgui.Dialog().ok('Error', 'Could not fetch ' + str(url) + "\nHTTP code " + str(req.status_code))

      except:
	  write2file(log_File, "processHTML ERROR: could not fetch " + str(url), 'a', 0, 1)
	  xbmcgui.Dialog().ok('Error', 'Could not fetch ' + str(url))

      try:
	  ## Extract 'now-playing' title
	  if osdInfo_Enabled == "true":
	    myInfo = re.compile('<div class="col-xs-10 col-sm-9 col-md-9 col-lg-9 program__program_name">\n[\s]+([őöüóúőéáűíŐÖÜÓÚŐÉÁŰÍA-Za-z0-9\t\s\-\)(`;:.!,]+)<\/div>').findall(html_text_data_3)
	    nowPlaying_Info = str(myInfo[0].split("\n")[0])
	    write2file(log_File, "processHTML nowPlayingTitle: " + nowPlaying_Info, 'a', 0, 0)

      except:
	    nowPlaying_Info = " - "
	    write2file(log_File, "processHTML ERROR: could not detect nowPlaying_Info", 'a', 0, 1)

      if req.status_code == 200:
	## Extract 'Restricted Access' warning, some channels require premium subscription
	if re.compile('<div class="modal-body">Nem rendelkezik előfizetéssel az adás megtekintésére.<\/div>').findall(html_text_data_3):
	  write2file(log_File, "processHTML Warning: Access Restricted (Nem rendelkezik ... blabla)", 'a', 0, 1)
	  xbmcgui.Dialog().ok('Warning', 'Nem rendelkezik előfizetéssel az adás megtekintésére')

	try:
	    ## Search for the playlist in the returned HTML document
	    ## e.g. createDefaultPlayer('http://online.digi.hu/api/streams/playlist/42/72cb73b6274e93e15b8e1d435f4ad235.m3u8',channel,'http://online.digi.hu/api/feedback','');
	    regxp = re.compile('(http:\/\/[A-Za-z0-9.\/]+.m3u8)').findall(html_text_data_3)
	    link = str(regxp[0])
	    write2file(log_File, "processHTML regxp: " + str(regxp), 'a', 0, 1)

	    if "http://" not in link:
	      link = "".join(("http:", link))

	except:
	    write2file(log_File, "processHTML ERROR: could not detect playlist URL", 'a', 0, 1)
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
	      write2file(log_File, "----- --- Playlist" + '\n' + req.content + "----- END Playlist", 'a', 0, 0)
	      write2file(playlist, req.content, 'w', 0, 0)

	  except:
	      write2file(log_File, "processHTML ERROR: could not acquire playlist", 'a', 0, 1)
	      xbmcgui.Dialog().ok('Error', 'Could not acquire playlist')
	      return False

      return link


def parseInput(url):
    global result
    result = None
    item = None

    logMyVars()
    write2file(log_File, "parseInput received URL: " + url, 'a', 0, 0)
    link = processHTML(url)

    ## Build ListItem
    if result is not None:
      try:
	item = xbmcgui.ListItem(path=link, iconImage=addon_thumb, thumbnailImage=nowPlayingThumb)
	itemInfo = {
	  'type': 'Video',
	  'genre': 'Live Stream',
	  'title': nowPlayingTitle,
	  'playcount': '0'
	}
	item.setInfo('video', itemInfo)
	if debug_Enabled == 'true':
	  write2file(log_File, "parseInput link " + str(link) , 'a', 0, 0)

      except:
	write2file(log_File, "parseInput: Could not access media", 'a', 0, 1)
	xbmcgui.Dialog().ok('Error', 'Could not access media')

    ################### Step 5 #########################
    ## Play stream
    if item is not None and result is not None:
      write2file(log_File, "xbmc.Player().play(" + link + "," + str(item) + ")", 'a', 0, 0)
      xbmcplugin.setContent(int(sys.argv[1]), 'movies')
      xbmc.Player().play(link, item)
      if osdInfo_Enabled == "true":
	xbmc.executebuiltin("Notification(" + nowPlayingTitle + ", " + nowPlaying_Info + ")")


## Debug
def write2file(myFile, text, append, header, footer):
    ## append: w = write, a = append
    if debug_Enabled == "true":
      try:
	  file = open(myFile, append)
	  if header == 1:
	    file.write('-------------------------------------------- ' + '\n')
	  file.write(text)
	  if footer == 1:
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
  write2file(log_File, text, 'a', 0, 1)

## Blabla & cleanup
def logMyVars():
  if debug_Enabled == "true":
    text = "osdInfo_Enabled: " + str(osdInfo_Enabled) + "\nuserAgent: " + userAgent
    write2file(log_File, text + str(login_User), 'w', 1, 1)
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

xbmcplugin.endOfDirectory(int(sys.argv[1]))
