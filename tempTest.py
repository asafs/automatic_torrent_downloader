
from SeriesUtils import *
from LocalFilesUtil import *
from utorrentUtils import *
import requests
from requests.auth import HTTPBasicAuth
import re

torrents = get_all_torrents()
tor = torrents[0]
for tor in torrents:
    get_season_and_episode_from_filename(tor['name'])









#TODO: Add move of file to NAS after finish download
#TODO: find subtitle
#TODO: Run with schedule
#TODO: GUI (Web UI?) to manage this
#TODO: add preffered quality for each searies
