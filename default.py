#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Add-on 'plugin.video.digi.hu-online'.

This file is subject to the terms and conditions defined in
file 'LICENSE', which is part of this source code package.
2018 Dexterke, SECRET LABORATORIES  <dexterkexnet@yahoo.com>
"""

import html
import logging
import os
import re
import shutil
import sys
import threading
import time
import urllib
from logging.handlers import RotatingFileHandler

import requests

import xbmc

import xbmcaddon

import xbmcgui

import xbmcplugin

import xbmcvfs


"""Settings."""
settings = xbmcaddon.Addon(id='plugin.video.digi.hu-online')
cfg_dir = xbmcvfs.translatePath(settings.getAddonInfo('profile'))
cache_dirname = 'artwork'
cache_dir = None
login_user = settings.getSetting('login_User')
login_passwd = settings.getSetting('login_Password')
debug_enabled = settings.getSetting('debug_Enabled')
osdinfo_enabled = settings.getSetting('popup_Enabled')

main_host = 'digionline.hu'
digi_host = 'online.digi.hu'
www_url = 'https://digionline.hu'
login_url = 'https://digionline.hu/login'
user_agent = (
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit'
  '/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15'
)
header_ctype = 'application/x-www-form-urlencoded; charset=UTF-8'
header_accept = (
  'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
)

play_file = os.path.join(cfg_dir, 'play_file.url')
epoch_tst = os.path.join(cfg_dir, 'epoch.txt')
channel_dir_file = os.path.join(cfg_dir, 'channels.html')
channel_file = os.path.join(cfg_dir, 'last_channel.html')

default_thumb = os.path.join(
  settings.getAddonInfo('path'), 'resources', 'media', 'tv.png',
)

session = None
"""conn_type = 'keep-alive'"""
conn_type = 'close'
poll_time = 300
header = {
  'Host': main_host,
  'Connection': conn_type,
  'Upgrade-Insecure-Requests': '1',
  'Accept': header_accept,
  'User-Agent': user_agent,
  'Accept-Language': 'en-ie',
  'DNT': '1',
  'Accept-Encoding': 'identity',
}

logger = logging.getLogger('plugin_video_digionline.hu')
log_file = os.path.join(cfg_dir, 'plugin_video_digionline.hu.log')
handler = RotatingFileHandler(
    log_file,
    mode='a',
    maxBytes=104857600,
    backupCount=2,
    encoding='UTF-8',
    delay=False,
)
logformat = '%(asctime)s %(name)s %(levelname)s - %(message)s'
log_datefmt = '%Y-%m-%d %H:%M:%S'
handler.setFormatter(logging.Formatter(logformat, datefmt=log_datefmt))

logger.addHandler(handler)
logger.propagate = True

if debug_enabled.lower() == 'true':
    logger.setLevel(logging.DEBUG)
else:
    handler.setLevel(logging.INFO)


def write2file(myfile, text, mode, encode='utf-8'):
    """Mode: w = write, a = append."""
    try:
        file = open(myfile, mode, encoding=encode)
        file.write(text)
        file.write('\n')
        file.close()
    except IOError:
        msg = f'Could not write to file "{myfile}"'
        logger.error(msg)
        xbmcgui.Dialog().ok('Error', msg)


def get_cache_path(file_name):
    """Set art/icon."""
    file_path = None
    try:
        file_path = os.path.join(cache_dir, file_name)
    except Exception:
        file_path = default_thumb

    logger.debug(f'file_name: {file_name}, path: {file_path}')
    return file_path


def get_params():
    """Get parameters."""
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
    """
    --------------------------------------------------------------------
    'url': 'http%3A%2F%2Fdigionline.hu%2Ftv%S%2Btv%2F', 'name': 'S+TV'
    --------------------------------------------------------------------
    """
    logger.debug(f'get_params return: {param}')
    return param


def get_currently_playing():
    """Get currently playing."""
    try:
        return xbmc.Player().getPlayingFile()
    except RuntimeError:
        return None


def get_nowplaying_info(bytz):
    """Detect 'now-playing info'."""
    info = ''
    text = bytz.decode('utf-8')
    pattern = (
      '<div class="col-xs-10 col-sm-9 col-md-9 col-lg-9 program__'
      'program_name">\n\\s+([őöüóúőéáűíŐÖÜÓÚŐÉÁŰÍ\\D.a-zA-Z]+)</div>'
    )
    try:
        data = re.compile(pattern).findall(text)
        info = str(data[1].split('\n')[0])
    except Exception as err:
        logger.error(f'Could not detect now-playing info: {err}')

    logger.debug(f'get_nowplaying_info: "{info}"')
    return info


def poller():
    """Poll HTML."""
    cnt = 0
    now = int(time.time())
    epoch = None
    write2file(epoch_tst, str(now), 'w')
    logger.debug(f'Starting poller. Epoch time {now}')
    while True:
        cnt += 1
        try:
            with open(epoch_tst, 'r') as file:
                epoch = int(file.read().replace('\n', ''))
        except Exception:
            break

        curr = get_currently_playing()
        if curr is not None:
            if now == epoch and digi_host in curr:
                # logger.debug(f'get_currently_playing: {curr}')
                text = None
                try:
                    with open(play_file, 'r') as file:
                        text = file.read().replace('\n', '')
                        if text is not None:
                            time.sleep(1)
                        if cnt == poll_time:
                            reload_url(text)
                            cnt = 0
                except Exception:
                    break
            else:
                logger.debug(
                  f'Closing poller, URL changed. Poller timestamp: {now},'
                  f' epoch timestamp: {epoch}, currently playing: {curr}',
                )
                break
        else:
            logger.debug('Closing poller, player stopped.')
            break


def login_digihu():
    """Perform login."""
    global session

    req = None
    match = None
    token = None
    sp_code = None

    """Load login URL, acquire session cookies."""
    headers = {
      'Connection': conn_type,
      'Upgrade-Insecure-Requests': '1',
      'Referer': login_url,
      'User-Agent': user_agent,
      'Origin': www_url,
      'Content-type': header_ctype,
      'Accept-Encoding': 'identity',
      'Accept-Language': 'en-ie',
      'X-Requested-With': 'XMLHttpRequest',
      'DNT': '1',
      'Accept': header_accept,
      'Host': main_host,
    }
    try:
        session = requests.Session()
        req = session.get(login_url, headers=headers)
        logger.debug(f'HTTP GET {login_url}: {req}')
        logger.debug(req.content)

        """Decode '_token' required for the next HTTP header"""
        mytxt = str(req.content)
        match = re.compile('name="_token" value="(.+?)"').findall(mytxt)
    except Exception as err:
        msg = f'Could not fetch "{login_url}": {err}'
        xbmcgui.Dialog().ok('Error', msg)

    """Execute login."""
    if match is not None and req.status_code == 200:
        logger.debug(f'Acquired token: {match}')
        if osdinfo_enabled:
            xbmc.executebuiltin(
              f'Notification(Digi-Online.hu, {now_playing_title})',
            )
        headers = {
          'Host': main_host,
          'Accept': '*/*',
          'X-Requested-With': 'XMLHttpRequest',
          'Accept-Language': 'en-ie',
          'Accept-Encoding': 'identity',
          'Content-type': header_ctype,
          'Origin': www_url,
          'User-Agent': user_agent,
          'Referer': login_url,
          'DNT': '1',
          'X-CSRF-TOKEN': str(match[0]),
          'Connection': conn_type,
        }
        try:
            req = session.post(
              login_url,
              headers=headers,
              data={
                'email': login_user,
                'password': login_passwd,
                'accept': '1',
              },
            )

            logger.debug(f'HTTP GET {login_url}: {req} - {req.content}')

        except Exception as err:
            msg = f'Login error: {err}'
            logger.error(msg)
            xbmcgui.Dialog().ok('Error', msg)

        sp_code = req.status_code
        if sp_code != 200:
            msg = f'Login failed. HTTP status code: {req.status_code}'
            logger.error(msg)
            xbmcgui.Dialog().ok('Error', msg)
        else:
            try:
                """Acquire login token."""
                mtxt = str(req.content)
                regxp = re.compile('name="_token" value="(.+?)"').findall(mtxt)
                token = str(regxp[0])
            except Exception as err:
                msg = f'Failed to acquire login token: {err}'
                logger.error(msg)
                xbmcgui.Dialog().ok('Error', msg)

    return {'token': token, 'status_code': sp_code}


def add_dir(name, url, iconimage):
    """Add directory items."""
    iconimage = urllib.parse.unquote(iconimage)
    u = (
        sys.argv[0] +
        '?url=' + urllib.parse.quote_plus(url) +
        '&name=' + urllib.parse.quote_plus(name) +
        '&thumb=' + urllib.parse.quote_plus(iconimage)
    )
    listitem = xbmcgui.ListItem(name)
    listitem.setArt({'thumb': iconimage, 'icon': default_thumb})
    listitem.setInfo(
        'video', {
            'mediatype': 'video',
            'genre': 'Live Stream',
            'title': name,
            'playcount': '0',
        },
    )
    xbmcplugin.addDirectoryItem(
        handle=int(sys.argv[1]), url=u, listitem=listitem,
    )


def show_root():
    """
    Show add-on root directory.

    <div class="col-xs-3 col-sm-2 col-md-2 col-lg-2 channels__logo">
                <a href="https://digionline.hu/player/267">
            <img src="https://online.digi.hu/cache/api/programs/m2-hd.png">
        </a>

    <div class="vertical-align-bottom pull-left">
        <div class="channels__name ">
            AMC
        </div>
    """
    login_data = login_digihu()
    logger.debug(f'login_data: {login_data}')
    if login_data['token'] is not None and login_data['status_code'] == 200:
        url = 'https://digionline.hu/csatornak'
        try:
            req = session.get(url, headers=header)
            if req.status_code != 200:
                msg = (
                    f'Could not fetch {url}, '
                    f'HTTP status code: {req.status_code}',
                )
                logger.error(msg)
                xbmcgui.Dialog().ok('Error', msg)
            else:
                html_text = req.content.decode('utf-8')
                write2file(channel_dir_file, html_text, 'w')

                pattern_t = (
                  '<div class="vertical-align-bottom pull-left">\n\\s+<div '
                  'class="channels__name ">\n\\s+(.+)\n\\s+</div>'
                )
                channels = re.compile(pattern_t).findall(html_text)
                logger.debug(f'channels found: {len(channels)} - {channels}')

                pattern_c = (
                  '<div class="col-xs-3 col-sm-2 col-md-2 col-lg-2 '
                  'channels__logo">\n\\s+<a '
                  'href="(https://digionline.hu/player/[0-9]+)">'
                  '\n\\s+<img src="(https://(.+).[a-zA-Z]{3})">\n\\s+</a>'
                )
                channel_data = re.compile(pattern_c).findall(html_text)
                logger.debug(
                  f'channel data: {len(channel_data)} - {channel_data}',
                )

                if len(channels) != len(channel_data):
                    msg = 'Error decoding channel listing'
                    logger.warning(msg)
                    xbmcgui.Dialog().ok('Warning', msg)

                for item in channel_data:
                    ind = channel_data.index(item)
                    channel_url = list(channel_data[ind])[0]
                    icon_url = list(channel_data[ind])[1]
                    title = channels[ind]
                    icon_file = icon_url.split('/')[-1]
                    icon_path = get_cache_path(icon_file)
                    if not os.path.isfile(icon_path):
                        r = session.get(icon_url, stream=True)
                        r.raw.decode_content = True
                        with open(icon_path, 'wb') as f:
                            shutil.copyfileobj(r.raw, f)

                    logger.debug(
                      f'add_dir({title}, {channel_url}, {icon_path})',
                    )
                    add_dir(title, channel_url, icon_path)

        except Exception as err:
            msg = f'Plugin error: {err}'
            logger.error(msg)
            xbmcgui.Dialog().ok('Error', msg)

    logger.debug(f'\n---End show_root---')


def process_digihu(url):
    """Load URL, detect playlist + 'now playing info'."""
    global session
    global result
    global now_playing_info
    url = html.unescape(url)
    req = None
    link = None

    login_data = login_digihu()
    logger.debug(f'login_data: {login_data}')
    if login_data['token'] is not None and login_data['status_code'] == 200:
        """Load URL."""
        try:
            req = session.get(url, headers=header)
            logger.debug(f'HTTP GET {url}: {req} - {req.content}')
            if req.status_code != 200:
                msg = (
                    f'Could not fetch {url}, '
                    f'HTTP status code: {req.status_code}',
                )
                logger.error(msg)
                xbmcgui.Dialog().ok('Error', msg)
            else:
                write2file(channel_file, req.content.decode('utf-8'), 'w')
        except Exception as err:
            msg = f'Could not fetch "{url}": {err}'
            xbmcgui.Dialog().ok('Error', msg)

        now_playing_info = get_nowplaying_info(req.content)
        if req.status_code == 200:
            """
            Detect 'Restricted Access' warning,
            some channels require premium subscription.
            """
            warn = 'Nem rendelkezik előfizetéssel az adás megtekintésére.'
            ptrn = f'<div class="modal-body">{warn}</div>'
            text = req.content.decode('utf-8')
            if re.compile(ptrn).findall(text):
                logger.warning(warn)
                xbmcgui.Dialog().ok('Warning', warn)
            else:
                try:
                    """
                    Search for m3u8 playlist in the HTML document:
                    createDefaultPlayer(
                      'https://online.digi.hu/api/streams/playlist/42/72cb73b6274e93e15b8e1d435f4ad235.m3u8',
                      channel,
                      'https://online.digi.hu/api/feedback',''
                    );
                    """
                    mytxt = str(req.content)
                    ptrn = '(https://[A-Za-z0-9./]+.m3u8)'
                    regxp = re.compile(ptrn).findall(mytxt)
                    link = str(regxp[0])
                    if 'https://' not in link:
                        link = ''.join(('https:', link))
                    logger.debug(f'Detected link: {link}')
                except Exception as err:
                    msg = f'Could not detect playlist info: {err}'
                    logger.error(msg)
                    xbmcgui.Dialog().ok('Error', msg)

                """Acquire playlist."""
                if link is not None:
                    headers = {
                      'Host': digi_host,
                      'DNT': '1',
                      # 'X-Playback-Session-Id': '56AFC239-C047-44BC-868F-038B28C79F25',
                      'Accept-Language': 'en-ie',
                      'Upgrade-Insecure-Requests': '1',
                      'Accept': '*/*',
                      'User-Agent': user_agent,
                      'Referer': www_url,
                      'Accept-Encoding': 'identity',
                      'Connection': conn_type,
                    }
                    try:
                        req = session.get(link, headers=headers)
                        result = req.content
                        logger.debug(f'HTTP GET {link}: {req.content}')
                        write2file(play_file, link, 'w')
                    except Exception as err:
                        msg = f'Could not acquire playlist: {err}'
                        logger.error(msg)
                        xbmcgui.Dialog().ok('Error', msg)
    return link


def parse_input(url):
    """Parse URL inout."""
    global result
    result = None
    listitem = None
    init_plugin()
    logger.debug(f'parse_input received URL {url}')
    link = process_digihu(url)

    """Build ListItem."""
    if result is not None:
        try:
            listitem = xbmcgui.ListItem(path=link)
            listitem.setArt(
                {'thumb': now_playing_thumb, 'icon': default_thumb},
            )
            listitem.setInfo(
                'video', {
                  'mediatype': 'video',
                  'genre': 'Live Stream',
                  'title': f'{now_playing_title} - {now_playing_info}',
                  'playcount': '1',
                },
            )
            listitem.setLabel(now_playing_title)
            listitem.setLabel2(now_playing_info)
        except Exception as err:
            msg = f'Could not access media: {err}'
            logger.error(msg)
            xbmcgui.Dialog().ok('Error', msg)

    """Play stream."""
    if listitem is not None and result is not None:
        logger.debug(f'Acquired link: {link}')
        xbmcplugin.setContent(int(sys.argv[1]), 'videos')
        xbmc.Player().play(link, listitem)
        if osdinfo_enabled:
            xbmc.executebuiltin(
                f'Notification({now_playing_title}, {now_playing_title})',
            )
        """Start poller."""
        time.sleep(60)
        curr = get_currently_playing()
        if curr is not None:
            try:
                logger.debug(f'now playing: {curr}')
                polling_thread = threading.Thread(
                    name=url, target=poller, args=(),
                )
                polling_thread.start()
            except Exception as err:
                logger.error(err)


def reload_url(url):
    """Load URL."""
    global session
    try:
        req = session.get(url, headers=header)
        html_text = req.content
        info = get_nowplaying_info(html_text)
        list_item = xbmcgui.ListItem()
        list_item.setPath(xbmc.Player().getPlayingFile())
        list_item.setLabel(now_playing_title)
        list_item.setLabel2(info)
        list_item.setInfo(
          'video', {
            'mediatype': 'video',
            'genre': 'Live Stream',
            'title': f'{now_playing_title} - {info}',
            'playcount': '1',
            },
        )
        xbmc.Player().updateInfoTag(list_item)
        if req.status_code != 200:
            msg = (
              f'could not fetch {url}, HTTP status code: {req.status_code}',
            )
            logger.error(msg)
    except Exception as err:
        logger.error(err)


def init_plugin():
    """Prepare the add-on."""
    global cache_dir

    cache_dir = os.path.join(cfg_dir, cache_dirname)
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except Exception as err:
            logger.error(err)
            xbmcgui.Dialog().ok('Error', err)

    logger.debug(f'OSD info enabled: {osdinfo_enabled}')
    logger.debug(f'user_agent: {user_agent}')
    if not debug_enabled:
        try:
            if os.path.isfile(log_file):
                os.remove(log_file)
            if os.path.isfile(play_file):
                os.remove(play_file)
        except Exception as err:
            logger.error(err)
            xbmcgui.Dialog().ok('Error', err)


"""Run this add-on."""
init_plugin()
params = get_params()
url = None
now_playing_thumb = None
now_playing_title = None
now_playing_info = None

try:
    url = urllib.parse.unquote(params['url'])
except Exception:
    url = None

try:
    now_playing_title = urllib.parse.unquote_plus(params['name'])
except Exception:
    now_playing_title = str(url)

try:
    now_playing_thumb = urllib.parse.unquote_plus(params['thumb'])
except Exception:
    now_playing_thumb = default_thumb

logger.debug(f'url: {url}')
logger.debug(f'now_playing_title: "{now_playing_title}"')
logger.debug(f'now_playing_thumb: "{now_playing_thumb}"')

if url is None or len(url) < 1:
    show_root()
else:
    parse_input(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]), updateListing=True)
