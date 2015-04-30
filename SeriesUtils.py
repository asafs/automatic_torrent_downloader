
from APIsConstants import *
import requests
import os.path
import json
import utorrentUtils


def get_series_list():
    # check from file first
    if os.path.isfile(SERIES_LIST_FILE_NAME):
        with open(SERIES_LIST_FILE_NAME, 'r') as f:
            return json.loads(f.read())
        # if not exist, check API and update file
    have_more = True
    current_series_group = 1
    series_list = []
    while have_more:
        r = requests.get(API_ALL_SHOWS_URL + str(current_series_group))
        if len(r.text) == 0:
            have_more = False
        else:
            for ser in r.json():
                series_list.append({'imdb_id': ser['imdb_id'], 'name': ser['title']})
            current_series_group += 1
    with open(SERIES_LIST_FILE_NAME, 'w') as f:
            f.write(json.dumps(series_list))
    return series_list


def get_series_id(series_name):
    for ser in get_series_list():
        if ser['name'].lower() == series_name.lower():
            return ser['imdb_id']
    return None


def get_series_data(series_name):
    imdb_id = get_series_id(series_name)
    r = requests.get(API_SINGLE_SHOW_URL + imdb_id)
    if r.status_code != 200 or len(r.text) == 0:
        return None
    return r.json()


def get_episodes_not_downloaded(series):
    data = get_series_data(series['name'])
    serie_last_season = series['last_episode']['season']
    serie_last_episode = series['last_episode']['episode']
    new_episode_list = []
    for epi in data['episodes']:
        if epi['season'] > serie_last_season:
            new_episode_list.append(epi)
        elif epi['season'] == serie_last_season and epi['episode'] > serie_last_episode:
            new_episode_list.append(epi)
    return new_episode_list


def get_episode_download_link(episode, res=None):
    torrents = episode['torrents']
    if len(torrents) == 0:
        # no torrents
        return None
    # check res, 480p, or existing
    if res:
        if res in torrents:
            return {'res': res, 'magnet_link': torrents[res]}
        else:
            return None
    elif '720p' in torrents:
        return {'res': '720p', 'magnet_link': torrents['720p']}
    elif '480p' in torrents:
        return {'res': '480p', 'magnet_link': torrents['480p']}
    else:
        for v in torrents:
            return {'res': v, 'magnet_link': torrents[v]}


def get_links_for_series(series, res=None, to_download=False):
    if not res:
        res = series['res']
    # print 'checking series: {}'.format(series['name'])
    episodes = get_episodes_not_downloaded(series)
    # print 'got {} new episodes'.format(len(episodes))
    links = []
    for epi in episodes:
        link = get_episode_download_link(epi, res)
        if link:
            epi['link'] = link
            links.append(epi)
            # print 'Got link for episode season {0} episode {1} in resolution {2}'.\
            #     format(epi['season'], epi['episode'], link['res'])
        # else:
        #     print 'No link for episode season {0} episode {1} in res {2}'.format(epi['season'], epi['episode'], res)
    return links


def get_series_to_download():
    if os.path.isfile(SEIRES_TO_DOWNLOAD_FILE_NAME):
        with open(SEIRES_TO_DOWNLOAD_FILE_NAME, 'r') as f:
            return json.loads(f.read())

