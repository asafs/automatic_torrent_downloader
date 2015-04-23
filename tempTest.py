
from SeriesUtils import *
from LocalFilesUtil import *
from utorrentUtils import *
import requests
from requests.auth import HTTPBasicAuth
import re

torrents = get_all_torrents()
torrents = filter_finished(torrents)
for tor in torrents:
    files = get_torrent_files(tor['hash'])
    video_files_data = get_data_for_video_files(files, torrent_name=tor['name'])
    if video_files_data:
        for data in video_files_data:
            copy_file_to_file_server(data['full_file_path'], data['series_name'], data['season'])

# print get_utorrent_settings()
# for tor in torrents:
#     print tor['name'], get_season_and_episode_from_filename(tor['name'])





#TODO: for each download create thread: create utorrent download, with for it do finish, copy file to path, remove from utorrent
#TODO: find subtitle
#TODO: Run with schedule
#TODO: GUI (Web UI?) to manage this
#TODO: add preffered quality for each searies
#TODO: add py-utorrent [https://github.com/ftao/py-utorrent] code
