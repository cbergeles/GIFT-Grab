#!/usr/bin/env python

from threading import Thread
from time import sleep, time
from datetime import timedelta
import pygiftgrab


class ORThread(Thread):
    def __init__(self, port, frame_rate, file_path):
        self.port = port
        try:
            self.file = pygiftgrab.Factory.writer(pygiftgrab.Storage.File_H265)
        except RuntimeError as e:
            print e.message
            self.is_running = False
        else:
            self.is_running = True
            self.file_path = file_path
            self.recording_index = 0
            self.frame_rate = frame_rate
            self.is_recording = False
            self.latency = 0.0  # sec
            self.sub_frame = None
            self.device = None
        Thread.__init__(self)

    def run(self):
        # mitigate re-start risk
        if not self.is_running:
            return

        inter_frame_duration = self.__inter_frame_duration()

        try:
            self.device = pygiftgrab.Factory.connect(self.port)
        except IOError as e:
            print e.message
            return

        frame = pygiftgrab.VideoFrame_BGRA(False)
        self.resume_recording()  # i.e. start recording

        while self.is_running:
            start = time()
            if self.is_recording:
                try:
                    self.device.get_frame(frame)
                except IOError as e:
                    print e.message
                else:
                    try:
                        self.file.append(frame)
                    except RuntimeError as e:
                        # TODO - this line is quick hack because of GiftGrab#37
                        self.is_running = False
                        print e.message
            sleep_duration = inter_frame_duration - (time() - start)
            if sleep_duration > 0:
                sleep(sleep_duration)
            else:
                self.latency -= sleep_duration

    def stop(self):
        if not self.is_running:
            return

        self.pause_recording()
        self.is_running = False

        try:
            pygiftgrab.Factory.disconnect(self.port)
        except IOError as e:
            print e.message

    def pause_recording(self):
        # TODO - this line is quick hack because of GiftGrab#37
        if not self.is_running:
            return

        if not self.is_recording:
            return

        self.is_recording = False
        # sleep to allow for stop to be picked up
        sleep(2 * self.__inter_frame_duration())

        try:
            self.file.finalise()
        except RuntimeError as e:
            print e.message
        # write latency as well
        latency_file = open(self.__next_filename(increment_index=False) +
                            '.latency.txt', 'w')
        latency_file.write(str(timedelta(seconds=self.latency)) + '\n')
        self.latency = 0.00

    def resume_recording(self):
        # TODO - this line is quick hack because of GiftGrab#37
        if not self.is_running:
            return

        if self.is_recording:
            return

        if self.sub_frame:
            self.device.set_sub_frame(self.sub_frame[0], self.sub_frame[1],
                                      self.sub_frame[2], self.sub_frame[3])
        else:
            self.device.get_full_frame()
        filename = self.__next_filename()
        try:
            self.file.init(filename, self.frame_rate)
        except RuntimeError as e:
            print e.message
            self.is_recording = False
        else:
            self.is_recording = True

    def set_sub_frame(self, x, y, width, height):
        self.sub_frame = [x, y, width, height]

    def set_full_frame(self):
        self.sub_frame = None

    def __next_filename(self, increment_index=True):
        if increment_index:
            self.recording_index += 1
        return self.file_path + '-' + \
            '{0:06d}'.format(self.recording_index) + \
            '.mp4'

    def __inter_frame_duration(self):
        return 1.0 / self.frame_rate  # sec
