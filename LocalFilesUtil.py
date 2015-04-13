

from os import listdir
from os.path import isfile, join, isdir
import re
from APIsConstants import *
import json


def get_all_series_from_local_network():
    return [f for f in listdir(LOCAL_SERIES_FULL_PATH) if isdir(join(LOCAL_SERIES_FULL_PATH, f))]
    pass


def get_all_episodes_for_series(series_name):
    series_path = join(LOCAL_SERIES_FULL_PATH, series_name)
    directories = [f for f in listdir(series_path) if isdir(join(series_path, f))]

    episode_list = {}
    for direc in directories:
        if direc == '.AppleDouble':
            continue
        episodes_path = join(series_path, direc)
        episodes = [f for f in listdir(episodes_path) if isfile(join(episodes_path, f))]
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


def get_last_episode(series_name):
    series_episode_list = get_all_episodes_for_series(series_name)
    highest_season = 0
    for season in series_episode_list:
        if season > highest_season:
            highest_season = season
    return {'season': highest_season, 'episode': max(series_episode_list[highest_season])}


def update_series_to_download():
    if isfile(SEIRES_TO_DOWNLOAD_FILE_NAME):
        with open(SEIRES_TO_DOWNLOAD_FILE_NAME, 'r') as f:
            series_to_download = json.loads(f.read())
            print series_to_download
        new_series_to_download = []
        for series in series_to_download:
            new_series_to_download.append({'name': series['name'], 'last_episode': get_last_episode(series['name'])})
        with open(SEIRES_TO_DOWNLOAD_FILE_NAME, 'w') as f:
            f.write(json.dumps(new_series_to_download))
