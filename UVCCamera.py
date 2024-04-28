import ray
import time
import cv2
import socket
import time
import numpy as np
import os
import sys
import threading


@ray.remote
class SyncSignal:
    def __init__(self):
        self._value = 0
    def set_signal(self, value):
        self._value = value
    def get_signal(self):
        return self._value
    def set_pulse(self,frames_num,fps):
        period_time = 1/fps
        sleep_time = period_time / 2
        for i in range(frames_num):
            self.set_signal(0)
            time.sleep(sleep_time)
            self.set_signal(i + 1)
            time.sleep(sleep_time)
        self.set_signal(-1)
        return True
            
@ray.remote
class UVCCamera:
    def __init__(self,id,frames_num = 100,width = 1280,height=720) -> None:
        self.id = id
        self.init_flag = False
        self.frames_num = frames_num
        self.frame_count = 0
        self.width = width
        self.height = height
        self.img_list = []
        self.sync_ind_list = []
        self.time_list = []
    def init_camera(self):
        self.cam = cv2.VideoCapture(self.id)
        self.cam.set(3,self.width)
        self.cam.set(4,self.height)
        self.cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        self.cam.set(cv2.CAP_PROP_EXPOSURE, -5)
        self.init_flag, frame = self.cam.read()
        self.init_flag, frame = self.cam.read()
        self.init_flag, frame = self.cam.read()
        return self.init_flag
    def get_flag(self):
        return self.init_flag
    def capture_soft_sync(self,actor):
        sync_ind_now = 0
        while self.frame_count < self.frames_num:
            sync_ind = ray.get(actor.get_signal.remote())
            if sync_ind == -1 or self.frame_count >= self.frames_num:
                break
            if sync_ind and sync_ind > sync_ind_now:
                start_time = time.time()
                success, frame = self.cam.read()
                end_time = time.time()
                if success:
                    self.img_list.append(frame)
                    self.sync_ind_list.append(sync_ind)
                    self.time_list.append(end_time)
                    self.frame_count += 1
                    sync_ind_now = sync_ind
            else:
                time.sleep(0.01)
        return True
    def save_img(self, save_dir):
        self.save_dir = save_dir
        for ind,ts,frame in zip(self.sync_ind_list,self.time_list,self.img_list):
            save_path = os.path.join(self.save_dir, f"camera_{self.id}_frame_{ind}.jpg")
            cv2.imwrite(save_path, frame)
        return self.time_list