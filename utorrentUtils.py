import requests
from requests.auth import HTTPBasicAuth
import re
import LocalFilesUtil
import os.path
import webbrowser

# BASE_API_URL = 'http://192.168.2.106:8089/gui/'
BASE_API_URL = 'http://localhost:8089/gui/'
API_TOKEN = 'token.html'
API_LIST_FILES = '?list=1'
API_GET_SETTINGS = '?action=getsettings'
API_GET_FILES = '?action=getfiles&hash='
API_STOP_TORRENT = '?action=stop&hash='
API_ADD_TORRENT = '?action=add-url&s='
API_REMOVE_TORRENT = '?action=remove&hash='

DOWNLOAD_PATH = 'C:/Users/Asaf/Downloads'

STATUS_STRINGS = ['Started', 'Checking', 'Start after check', 'Checked', 'Error', 'Paused', 'Queued', 'Loaded']
FILE_PRIORITY_STRINGS = ['Don''t Download', 'Low Priority', 'Normal Priority', 'High Priority']

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


def filter_finished(torrents):
    finished = []
    for tor in torrents:
        if tor['percent_progress'] == 100:
            finished.append(tor)
    return finished


def get_status_from_code(status_code):
    statuses = []
    for i in range(0, 8):
        if status_code >> i & 1:
            statuses.append(STATUS_STRINGS[i])
    return statuses


def get_utorrent_settings():
    r = requests.get(BASE_API_URL + API_GET_SETTINGS, auth=auth)
    if r.status_code == 200:
        return r.text
    pass


def stop_torrent(torrent_hash):
    r = requests.get(BASE_API_URL + API_STOP_TORRENT + torrent_hash, auth=auth)
    print r.text
    if r.status_code != 200:
        return False
    return True


def remove_torrent(torrent_hash):
    r = requests.get(BASE_API_URL + API_REMOVE_TORRENT + torrent_hash, auth=auth)
    print r.text
    if r.status_code != 200:
        return False
    return True


def get_torrent_files(torrent_hash):
    r = requests.get(BASE_API_URL + API_GET_FILES + torrent_hash, auth=auth)
    if r.status_code != 200:
        return None
    j = r.json()
    if not j:
        return None
    files = []
    for file_data in j['files'][1]:
        data = {'file_name': file_data[0],
                'file_size_in_bytes': file_data[1],
                'downloaded_in_bytes': file_data[2],
                'priority': file_data[3],
                'priority_string': FILE_PRIORITY_STRINGS[int(file_data[3])],
                'first_piece': file_data[4],
                'num_pieces': file_data[5]
                }
        # print part
        files.append(data)
    return files


def get_data_for_video_files(files_in_torrent, torrent_name):
    if not files_in_torrent:
        return None
    files_data = []
    for f in files_in_torrent:
        if not LocalFilesUtil.check_if_file_is_video(f['file_name']):
            continue
        # check if series and get season
        season, episode = LocalFilesUtil.get_season_and_episode_from_filename(f['file_name'])
        if not season:
            # for now, don't handle movies
            print('{} is not series file'.format(f['file_name']))
            return None
        # get series name
        series_name = LocalFilesUtil.get_series_name_from_filename(f['file_name'])
        if not series_name:
            print('{} is a bad file name'.format(f['file_name']))
            return None
        # get full file path
        full_path = os.path.join(DOWNLOAD_PATH, torrent_name)
        if os.path.isdir(full_path):
            full_path = os.path.join(full_path, f['file_name'])
        files_data.append({
            'season': season,
            'episode': episode,
            'file_name': f['file_name'],
            'series_name': series_name,
            'full_file_path': full_path
        })
    return files_data


def download_magnet_link(magnet_link):
    webbrowser.open_new(magnet_link)


def download_file(file_link):
    r = requests.get(BASE_API_URL + API_ADD_TORRENT + file_link, auth=auth)
    if r.status_code != 200:
        return False
    return True


def get_series_data_from_file_name():
    pass
