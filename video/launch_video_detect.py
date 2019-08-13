# -*- encoding:utf-8 -*-
__date__ = "18/9/18"
__author__  = "jensen"
 
 
import os
import shutil
from argparse import ArgumentParser
 
 
 
def video_to_frames(video_path, frames_path, step_size = 20):
    if not os.path.exists(frames_path):
        os.makedirs(frames_path)
    else:
        shutil.rmtree(frames_path)
        os.makedirs(frames_path)
    
    output_file = frames_path + "/out%05d.jpg"
    print("ffmpeg -i {} -f image2 {}".format(video_path, output_file))
    #extract an image every 20 seconds
    # you can also set every 10 seconds, just set fps = fps = 1/10
    os.system("ffmpeg -i {} -f image2 -vf fps=fps=1/{} {}".format(video_path, step_size, output_file))
 
 
if __name__ == '__main__':
 
    parser = ArgumentParser()
 
    parser.add_argument('--content',
            dest='content', help='content image',
            metavar='CONTENT', required=True)
    parser.add_argument('--step', type=int, default = 20,
            dest='step', help='the video step you want use',
            metavar='STEP')
 
    options = parser.parse_args()
 
    video_name = options.content # the video name you want to detect
 
    step_size = options.step # the video step you want to use
 
    #video_name = "1994.mp4" # the video name you want to detect
 
    video_path = "./"  # the video path, i put the video at current folder
    frames_path = "picture"
    
    video_to_frames(video_path + video_name, frames_path, step_size)
 
    # start the docker and set the workspace as "/home/jingxian/open_nsfw"
    # set as your own path
    #launch the docker
    os.system("docker run -ti --volume={}:/workspace caffe:cpu bash -c \"python video_detect.py\"".format("/home/jingxian/open_nsfw/"))