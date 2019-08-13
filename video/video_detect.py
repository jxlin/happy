# -*- encoding:utf-8 -*-
__date__ = "18/9/18"
__author__  = "jensen"
 
import os
import shutil
 
 
 
frames_path = "picture"
 
files= os.listdir(frames_path) 
 
 
results = []
 
import video_nsfw
 
safe = 0.0
median = 0.0
dangerous = 0.0
 
for file in files:   
    if not os.path.isdir(file):
        res = video_nsfw.detact("nsfw_model/deploy.prototxt", "nsfw_model/resnet_50_1by2_nsfw.caffemodel", frames_path + "/" + file)
        if res < 0.2:
            safe += 1
        elif res < 0.8:
            median += 1
        else:
            dangerous += 1
 
        results.append(res)
 
print(len(results))
print("safe count: {}, proportion: {}%".format(safe, round(safe / len(results) * 100, 3)))
print("median count: {}, proportion: {}%".format(median, round(median / len(results) * 100, 3)))
print("dangerous count: {}, proportion: {}%".format(dangerous, round(dangerous / len(results) * 100, 3)))