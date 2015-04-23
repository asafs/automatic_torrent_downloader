

from os import listdir
import os.path
import re
from APIsConstants import *
import json
import shutil
import threading
import time


def get_all_series_from_local_network():
    series = []
    for dir_path in LOCAL_SERIES_FULL_PATHS:
        series += [f for f in listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]


def get_series_path(series_name):
    for dir_path in LOCAL_SERIES_FULL_PATHS:
        series_path = os.path.join(dir_path, series_name)
        if os.path.isdir(series_path):
            return series_path
    return None


def get_all_episodes_for_series(series_name):
    series_path = get_series_path(series_name)
    directories = [f for f in listdir(series_path) if os.path.isdir(os.path.join(series_path, f))]

    episode_list = {}
    for direc in directories:
        if direc == '.AppleDouble':
            continue
        episodes_path = os.path.join(series_path, direc)
        episodes = [f for f in listdir(episodes_path) if os.path.isfile(os.path.join(episodes_path, f))]
        for epi in episodes:
            if epi[-3:] == 'srt':  # subtitle
                continue
            # print epi
            season_number, episode_number = get_season_and_episode_from_filename(epi)
            if not season_number:
                # print epi
                continue
            # print season_number, episode_number
            if season_number not in episode_list:
                episode_list[season_number] = []
            episode_list[season_number].append(episode_number)
    return episode_list

    pass


def get_season_and_episode_from_filename(episode_name):
    # for now, only search sXXeXX
    # TODO: add YYxYY expression
    m = re.search('[Ss]{1,1}(\d\d)[Ee]{1,1}(\d\d)', episode_name)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def get_series_name_from_filename(episode_name):
    # for now, only search sXXeXX
    # TODO: add YYxYY expression
    m = re.search('(.*?)[Ss]{1,1}\d\d[Ee]{1,1}\d\d', episode_name)
    if m:
        return ' '.join(m.group(1).split('.'))[:-1]  # last one is space...
    return None


def get_last_episode(series_name):
    series_episode_list = get_all_episodes_for_series(series_name)
    highest_season = 0
    for season in series_episode_list:
        if season > highest_season:
            highest_season = season
    return {'season': highest_season, 'episode': max(series_episode_list[highest_season])}


def update_series_to_download():
    if os.path.isfile(SEIRES_TO_DOWNLOAD_FILE_NAME):
        with open(SEIRES_TO_DOWNLOAD_FILE_NAME, 'r') as f:
            series_to_download = json.loads(f.read())
            print series_to_download
        new_series_to_download = []
        for series in series_to_download:
            new_series_to_download.append({'name': series['name'], 'last_episode': get_last_episode(series['name'])})
        with open(SEIRES_TO_DOWNLOAD_FILE_NAME, 'w') as f:
            f.write(json.dumps(new_series_to_download))


def check_if_file_is_video(file_name):
    ext = file_name[-3:]
    return ext == 'mp4' or ext == 'mkv' or ext == 'avi'


def copy_file_to_file_server(full_file_path, series_name, season, overwrite=False):
    full_new_path = os.path.join(get_series_path(series_name), 'Season ' + str(season))
    full_new_file = os.path.join(full_new_path, os.path.split(full_file_path)[1])
    if not overwrite and os.path.exists(full_new_file):
        print('file {} already exists, aborting copy'.format(full_new_file))
        return
    print('copying file {}, this my take a while...'.format(full_file_path))
    copy_thread = FileCopy(full_file_path, full_new_file)
    copy_thread.start()
    seconds_waited = 0
    start_size = os.path.getsize(full_file_path)
    print('original file size: {} MB'.format(start_size/1000/1000))
    while not copy_thread.get_is_finished():
        time.sleep(1)
        seconds_waited += 1
        updated_size = os.path.getsize(full_new_file)
        print('After {0} seconds, current output file size: {1} MB, finished {2:.2f}%'
              .format(seconds_waited, updated_size/1000/1000, 1.0*updated_size/start_size*100))
    copy_thread.join()
    # shutil.copy2(full_file_path, full_new_file)
    print('copying file {} completed!'.format(full_file_path))


class FileCopy(threading.Thread):
    def __init__(self, src_file_path, dst_dir_path):
        threading.Thread.__init__(self)
        self.src = src_file_path
        self.dst = dst_dir_path
        self.is_finished = False

    def get_is_finished(self):
        return self.is_finished

    def run(self):
        try:
            shutil.copy(self.src, self.dst)
        except IOError, e:
            raise RuntimeError('copy failed')
        finally:
            self.is_finished = True