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


def process_image(self, image_data):
    # reshape the image data as 1dimensional array
    image = image_data.as_1d_image()
    # make a gray image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image = cv2.medianBlur(image,5)
    # find circles in the image
    circles = cv2.HoughCircles(image, cv2.cv.CV_HOUGH_GRADIENT, 1.2, 100)
    # make a color image again to mark the circles in green
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(image, (x, y), r, (0, 255, 0), 6)

    # show the image with Qt
    #return QtGui.QImage(image.data,
    #                    image_data.mem_info.width,
    #                    image_data.mem_info.height,
    #                   QtGui.QImage.Format_RGB888)


def main():
    # we need a QApplication, that runs our QT Gui Framework
    ##app = PyuEyeQtApp()

    # a basic qt window
    #view = PyuEyeQtView()
    #view.show()
    #view.user_callback = process_image

    # camera class to simplify uEye API access
    cam = Camera(1)
    cam.init()
    cam.set_colormode(ueye.IS_CM_BGR8_PACKED)

    #ret = cam.set_exposure(30.0)
    #ret = cam.set_LUT()
    #
    width, height = cam.get_size()
    x = 0
    y = 0
    ret = cam.set_aoi(x, y, width, height)
    cam.alloc(buffer_count=100)
    ret = cam.capture_video(True)  # start to capture;

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter( '_output.avi', fourcc, 20.0, (width, height))

    # a thread that waits for new images and processes all connected views
    #thread = FrameThread(cam)
    #thread.start()
    running = True
    img_buffer = ImageBuffer()
    DATA = ImageData(cam.handle(), img_buffer)
    while (ret == 0) and running:
        #img_buffer = ImageBuffer()
        ret = ueye.is_WaitForNextImage(cam.handle(),
                                       1000,
                                       img_buffer.mem_ptr,
                                       img_buffer.mem_id)
        #print(img_buffer.mem_id)
        if ret == ueye.IS_SUCCESS:
            #DATA = ImageData(cam.handle(), img_buffer)
            DATA.getdata(img_buffer)
            #print(DATA.array.shape)
            image = DATA.as_1d_image()
            DATA.unlock()
            # make a gray image
            #imag = cv2.cvtColor(image, cv2.COLOR_BGR)
            cv2.imshow("Simple_black", image)
            out.write(image)
            if cv2.waitKey(1) == 27:
                break
            #cv2.Mat(ImageData.array)

    # cleanup
    #app.exit_connect(thread.stop)
    #app.exec_()

    #thread.stop()
    #thread.join()

    cam.stop_video()
    cam.exit()
    cv2.destroyAllWindows()
    out.release()


if __name__ == "__main__":
    main()

