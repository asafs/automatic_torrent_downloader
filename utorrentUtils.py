import requests
from requests.auth import HTTPBasicAuth
import re

BASE_API_URL = 'http://192.168.2.106:8089/gui/'
API_TOKEN = 'token.html'
API_LIST_FILES = '?list=1'

STATUS_STRINGS = ['Started', 'Checking', 'Start after check', 'Checked', 'Error', 'Paused', 'Queued', 'Loaded']

auth = HTTPBasicAuth('admin', 'admin')


def get_token():
    """
    gets the private token from the API.
    currently disabled in the server.

    :return: the token
    """

    r = requests.get(BASE_API_URL + API_TOKEN, auth=auth)
    if r.status_code == 200:
        m = re.search('div.*?>(.*)</div>', r.text)
        if m:
            print('found token')
            return m.group(1)
    else:
        print 'token not available...'
        return None


def get_all_torrents():
    r = requests.get(BASE_API_URL + API_LIST_FILES, auth=auth)
    if r.status_code != 200:
        print('can\'t access list api')
        return None
    torrents = r.json()['torrents']
    # create new json data for each torrent
    json_torrents = []
    for torrent in torrents:
        json_torrents.append({
            'hash': torrent[0],
            'status': torrent[1],
            'status_strings': get_status_from_code(torrent[1]),
            'name': torrent[2],
            'size_in_bytes': torrent[3],
            'percent_progress': torrent[4]/10,
            'downloaded_in_bytes': torrent[5],
            'uploaded_in_bytes': torrent[6],
            'ratio': torrent[7],
            'upload_speed_in_Bps': torrent[8],
            'download_speed_in_Bps': torrent[9],
            'eta_in_seconds': torrent[10],
            'label': torrent[11],
            'peers': torrent[12],
            'peers_in_swarm': torrent[13],
            'seeds_connected': torrent[14],
            'seeds_in_swarm': torrent[15],
            'availability': torrent[16],
            'queue_order': torrent[17],
            'remaining_in_bytes': torrent[18]
        })
    return json_torrents
    pass


def get_status_from_code(status_code):
    statuses = []
    for i in range(0, 8):
        if status_code >> i & 1:
            statuses.append(STATUS_STRINGS[i])
    return statuses

# 	REMAINING (integer in bytes)	]

