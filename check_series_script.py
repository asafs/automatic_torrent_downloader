"""
This script checks for new episodes, and downloads them with Download torrent

"""

import LocalFilesUtil
import SeriesUtils
import DownloadTorrent
import time
import sys

thread_list = []


def all_finished():
    for th in thread_list:
        if not th['finished']:
            return False
    return True

if __name__ == '__main__':
    LocalFilesUtil.update_series_to_download()
    series_to_download = SeriesUtils.get_series_to_download()

    for series in series_to_download:
        # print series
        links = SeriesUtils.get_links_for_series(series)
        # for each
        for link in links:
            # print link['link']['magnet_link']['url']
            t = DownloadTorrent.DownloadTorrentThread(magnet_link=link['link']['magnet_link']['url'])
            t.start()
            thread_list.append({
                'thread': t,
                'link': link,
                'name': series['name'],
                'finished': False
            })

    while not all_finished():
        time.sleep(2)
        for th in thread_list:
            s = 'status for file Series {0} Se {1} Ep {2}: '.format(
                th['name'],
                th['link']['season'],
                th['link']['episode'])
            t = th['thread']
            if t.state == DownloadTorrent.DownloadTorrentThread.STATE_DOWNLOADING:
                s += t.print_downloading_status()
            elif t.state == DownloadTorrent.DownloadTorrentThread.STATE_MOVING:
                s += t.print_copying_status()
            elif t.state == DownloadTorrent.DownloadTorrentThread.STATE_FINISHED:
                th['finished'] = True
                s += 'Finished!'
            print s
        pass

    for th in thread_list:
        th['thread'].join()

        # while not t.state == DownloadTorrent.DownloadTorrentThread.STATE_FINISHED:
        #     print('for series {0}:'.format(series['name']))
        #     if t.state == DownloadTorrent.DownloadTorrentThread.STATE_DOWNLOADING:
        #         t.print_downloading_status()
        #     elif t.state == DownloadTorrent.DownloadTorrentThread.STATE_MOVING:
        #         t.print_copying_status()
        #     time.sleep(1)
        # t.join()

            # pass
            # t.start()
            # t.join()
        pass