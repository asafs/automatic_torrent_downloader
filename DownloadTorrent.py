import threading
import utorrentUtils
import LocalFilesUtil
import time
from datetime import datetime
import subliminal
import os
from babelfish import Language


class DownloadTorrentThread(threading.Thread):
    """
    Class for managing the download, moving and subtitles for torrents.
    """
    STATE_STARTED = 0
    STATE_DOWNLOADING = 1
    STATE_FINISHED_DOWNLOADING = 2
    STATE_MOVING = 3
    STATE_FINISHED = 4

    def __init__(self, magnet_link, ovewrite_existing=False):
        super(DownloadTorrentThread, self).__init__()
        self.magnet_link = magnet_link
        self.hash = ''
        self.percent_downloaded = 0
        self.state = DownloadTorrentThread.STATE_STARTED
        self.ovewrite_existing = ovewrite_existing
        self.video_files_data = []
        self.time_since_start_downloading = 0

    @staticmethod
    def _get_new_downloaded_hash(before_list, after_list):
        for tor in after_list:
            name = tor['name']
            found = False
            for tor2 in before_list:
                if tor2['name'] == tor['name']:
                    found = True
                    continue
            if not found:
                return tor['hash'], tor
        return None, None

    def _wait_to_finish_downloading(self):
        finished = False
        start_download_time = datetime.now()
        time_since_start_downloading = datetime.now()
        torrent_name = ''
        while not finished:
            time.sleep(1)
            torrent_list = utorrentUtils.get_all_torrents()
            for tor in torrent_list:
                if tor['hash'] == self.hash:
                    torrent_name = tor['name']
                    self.percent_downloaded = tor['percent_progress']
                    break
            if self.percent_downloaded == 100:
                finished = True
            self.time_since_start_downloading = (datetime.now() - time_since_start_downloading).seconds
            # self.print_downloading_status()
        self.state = DownloadTorrentThread.STATE_FINISHED_DOWNLOADING
        return torrent_name

    def get_percent_downloaded(self):
        if self.state != DownloadTorrentThread.STATE_DOWNLOADING:
            return None
        return self.percent_downloaded

    def get_time_since_start_downloading(self):
        if self.state != DownloadTorrentThread.STATE_DOWNLOADING:
            return None
        return self.time_since_start_downloading

    def print_downloading_status(self):
        if self.state == DownloadTorrentThread.STATE_DOWNLOADING:
            s = 'after {} seconds, downloaded {} %'.format(self.get_time_since_start_downloading(), self.get_percent_downloaded())
            return s
        return None

    def _copy_files(self):

        video_files_data = self.video_files_data
        self.thread_list = []
        for data in video_files_data:
            src_file = data['full_file_path']
            dst_dir = os.path.join(LocalFilesUtil.get_series_path(data['series_name']), 'Season ' + str(data['season']))
            dst_file = os.path.join(dst_dir, os.path.split(src_file)[1])
            if not self.ovewrite_existing and os.path.exists(dst_file):
                print('file {} already exists, skipping copy'.format(dst_file))
                continue

            # print('copying file to {}, this my take a while...'.format(dst_dir))
            copy_thread = LocalFilesUtil.FileCopy(src_file, dst_file)
            copy_thread.start()
            self.thread_list.append({
                'thread': copy_thread,
                'file_name': os.path.split(src_file)[1],
                'finished': False})

        while not self._all_copy_finished():
            for threads in self.thread_list:
                if threads['thread'].is_finished:
                    threads['finished'] = True
            time.sleep(1)
            pass
        for th in self.thread_list:
            th['thread'].join()

    def _all_copy_finished(self):
        """
        return true if all copy threads are finished
        :return: boolean
        """
        if self.state != DownloadTorrentThread.STATE_MOVING:
            return None
        for th in self.thread_list:
            if not th['finished']:
                return False
        return True

    def get_percent_copy(self):
        """
        returns the average percentage of copied files
        """
        if self.state != DownloadTorrentThread.STATE_MOVING:
            return None
        sum_percentage = 0
        for th in self.thread_list:
            sum_percentage += th['thread'].get_copy_status()
        return sum_percentage / len(self.thread_list)

    def get_time_since_start_copying(self):
        if self.state != DownloadTorrentThread.STATE_MOVING:
            return None
        max_time = 0
        for th in self.thread_list:
            if max_time < th['thread'].get_time_passed():
                max_time = th['thread'].get_time_passed()
        return max_time

    def print_copying_status(self):
        if self.state == DownloadTorrentThread.STATE_MOVING:
            s = 'after {} seconds, copied {} %'.format(self.get_time_since_start_copying(), self.get_percent_copy())
            return s
        return None

    def run(self):
        """
        The main thread. this will run:
        - download torrent using utorrent
        - check utorent for status until finish downloading
        - move file to new location
        :return:
        """
        # start downloading and get hash
        self.state = DownloadTorrentThread.STATE_DOWNLOADING
        before_list = utorrentUtils.get_all_torrents()
        if not utorrentUtils.download_file(self.magnet_link):
            # TODO: run utorrent
            raise RuntimeError('Utorrent not working!')
        time.sleep(1)
        after_list = utorrentUtils.get_all_torrents()
        self.hash, torrent_data = self._get_new_downloaded_hash(before_list, after_list)

        if not self.hash:
            print 'file already existing in utorrent'
            return
        # print self.hash
        # print torrent_data

        torrent_name = self._wait_to_finish_downloading()

        # get all video files and move them to the correct location
        self.state = DownloadTorrentThread.STATE_MOVING
        files = utorrentUtils.get_torrent_files(self.hash)
        video_files_data = utorrentUtils.get_data_for_video_files(files, torrent_name=torrent_name)
        if video_files_data:
            self.video_files_data = video_files_data
            self._copy_files()

            # download subtitles
            for data in video_files_data:
                src_file = data['full_file_path']
                dst_dir = os.path.join(LocalFilesUtil.get_series_path(data['series_name']), 'Season ' + str(data['season']))
                dst_file = os.path.join(dst_dir, os.path.split(src_file)[1])
                videos = subliminal.scan_videos([dst_file])
                subtitles = subliminal.download_best_subtitles(videos, {Language('heb'), Language('eng')})
                subliminal.save_subtitles(subtitles)

        self.state = DownloadTorrentThread.STATE_FINISHED

        pass