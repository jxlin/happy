#!/usr/bin/env python


from pyueye_example_camera import Camera
from pyueye_example_utils import FrameThread, ImageBuffer, ImageData
#from pyueye_example_gui import PyuEyeQtApp, PyuEyeQtView
#from PyQt4 import QtGui

from pyueye import ueye
import sys

cvpath = "/usr/local/lib/python2.7/dist-packages"
if cvpath not in sys.path:
    sys.path.insert(0, cvpath)

import cv2
import numpy as np

class idscamera(object):
    def __init__(self, camhand=1, AOIwidth = 1280, AOIheight = 1024, buffer_count=100 ):
        self.camhandle = camhand
        self.cam = Camera(self.camhandle)
        self.cam.init()
        self.cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
        # ret = self.cam.set_exposure(30.0)
        #ret = cam.set_LUT()
        # ret = self.cam.set_aoi(0, 0, AOIwidth, AOIheight)
        self.cam.alloc(buffer_count)
        ret = self.cam.capture_video(True)  # start to capture;
        self.img_buffer = ImageBuffer()
        self.DATA = ImageData(self.camhandle, self.img_buffer)



    def extract(self):

        ret = ueye.is_GetActSeqBuf(self.camhandle,
                                   self.img_buffer.mem_id,
                                   self.img_buffer.mem_ptr,
                                   self.img_buffer.mem_ptrlast)


        # ret = ueye.is_WaitForNextImage(self.camhandle,
        #                                100,
        #                                self.img_buffer.mem_ptr,
        #                                self.img_buffer.mem_id)
        # print(self.img_buffer.mem_id)
        if ret == ueye.IS_SUCCESS:
            #DATA = ImageData(cam.handle(), img_buffer)
            self.DATA.lock()
            self.DATA.getdata(self.img_buffer)
            image = self.DATA.as_1d_image()
            #print(DATA.array.shape)            
            self.DATA.unlock()
            
            return image
        else:
            return None

    def get_size(self):
        return self.cam.get_size()

    def stop(self):
        self.cam.stop_video()
        self.cam.exit()



