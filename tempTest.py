
from SeriesUtils import *
from LocalFilesUtil import *
from utorrentUtils import *
import requests
from requests.auth import HTTPBasicAuth
import re
import DownloadTorrent
import subliminal
from babelfish import Language
from datetime import timedelta
import urllib2

link = r'magnet:?xt=urn:btih:CTMX2DJCG5EMRFHBT6QGZQI7XHFTJE4D&dn=The.Big.Bang.Theory.S08E18.HDTV.x264-LOL&tr=' \
       r'udp://open.demonii.com:80&tr=udp://tracker.coppersurfer.tk:80&tr=udp://tracker.leechers-paradise.org:6969' \
       r'&tr=udp://exodus.desync.com:6969'
video_path = LOCAL_SERIES_FULL_PATHS[0] + r'/The Big Bang Theory/Season 1/big_bang_theory.1x02.the_big_bran_hypothesis.dvdrip_xvid-fov.avi'


update_series_to_download()
series_to_download = get_series_to_download()
for series in series_to_download:
    print series
    get_links_for_series(series)

# t = DownloadTorrent.DownloadTorrentThread(magnet_link=link)
# t.start()
# t.join()
# print 'finish'
# download_file(link)

# configure the cache
# subliminal.cache_region.configure('dogpile.cache.dbm', arguments={'filename': './vid/cachefile.dbm'})

# # scan for videos in the folder and their subtitles
# videos = subliminal.scan_videos([video_path])
# # subliminal.sc
# print videos
# # download best subtitles
# subtitles = subliminal.download_best_subtitles(videos, {Language('heb'), Language('eng')})
# print subtitles
# # save them to disk, next to the video
# subliminal.save_subtitles(subtitles)


# torrents = get_all_torrents()
# torrents = filter_finished(torrents)
# for tor in torrents:
#     files = get_torrent_files(tor['hash'])
#     video_files_data = get_data_for_video_files(files, torrent_name=tor['name'])
#     if video_files_data:
#         for data in video_files_data:
#             #print data
#             copy_file_to_file_server(data['full_file_path'], data['series_name'], data['season'])

# print get_utorrent_settings()
# for tor in torrents:
#     print tor['name'], get_season_and_episode_from_filename(tor['name'])





#TODO: for each download create thread: create utorrent download, with for it do finish, copy file to path, remove from utorrent
#TODO: find subtitle
#TODO: Run with schedule
#TODO: GUI (Web UI?) to manage this
#TODO: add preffered quality for each searies
#TODO: add py-utorrent [https://github.com/ftao/py-utorrent] code
