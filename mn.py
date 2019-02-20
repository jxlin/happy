#!/usr/bin/python
# -*- coding: utf-8 -*-
from sets import Set
import numpy as np
import urllib
import json
import cv2
import os
import time
from face_detection import FaceDetection
from face_recognition import FaceRecogniton
from face_alignment import FaceAlignment
import argparse
import glob
import shutil

face_det = None
face_recon = None
face_align = None
gpu_id = 0

def compare(root, f1, f2):
    global face_det
    global face_recon
    global face_align
    if not face_det:
        face_det = FaceDetection(gpu_id)
    if not face_recon:
        face_recon = FaceRecogniton(gpu_id)
    if not face_align:
        face_align = FaceAlignment(gpu_id)
    time_start = time.time()
    img_a = cv2.imread(root + '/' + f1)
    img_b = cv2.imread(root + '/' + f2)

    bbox_list1, a_point = face_det.get_max_bounding_box_by_image(img_a)
    bbox_list2, b_point = face_det.get_max_bounding_box_by_image(img_b)
    similarity = 0
    if bbox_list1 and bbox_list2:
        a_aligned_faces = face_align.affine_face(img_a, a_point)
        b_aligned_faces = face_align.affine_face(img_b, b_point)
        similarity = face_recon.face_compare(a_aligned_faces, b_aligned_faces)
        #print similarity
        time_end = time.time()
        time_use = int(1000 * (time_end - time_start))
        #print 'time_used:' + str(time_use)
    return similarity, time_use

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="test on a single directory")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image_dir', type=str, default=None)
    parser.add_argument('--confidence', type=int, default=70)
    args = parser.parse_args()
    default_confidence = 0.7
    if args.confidence is not None:
	print args.confidence
	if args.confidence > 0 and args.confidence <= 100:
	    default_confidence = args.confidence/float(100)
    files = []
    if os.path.exists(args.image_dir):
        for root, dirs, filenames in os.walk(args.image_dir):
            for file in filenames:
                img=cv2.imread(args.image_dir + '/' + file)
                if img is not None and img.shape is not None:
                    height, width, channels = img.shape
                    if height < 128 or width < 128: continue
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2Fray)
                    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
                    if fm > 50:
                        files.append(file)

    length = len(files)
    print ('{} files to be examined with confidence level {}.'.format(length, default_confidence))
    total_time = 0
    goodsets = Set()
    output = dict()
    reverse = dict()
    value = 0
    failed = 0
    for i in range(0, length-2):
        for j in range(i+1, length-1):
            try:
                similarity, time_use = compare(args.image_dir, files[i], files[j])
                if similarity >= default_confidence:
                    print files[i], files[j], similarity
                    if output.get(files[i]) is None and output.get(files[j]) is None:
                        output.update({files[i]: value, files[j]: value})
                        values = None
                        if reverse.get(value) is None:
                            values = Set()
                        else:
                            values = reverse.get(value)
                        values.add(files[i])
                        values.add(files[j])
                        print ('{}->{}'.format(files[i], value))
                        print ('{}->{}'.format(files[j], value))
                        reverse.update({value:values})
                        value = value + 1
                    elif output.get(files[j]) is None:
                        value1 = output.get(files[i])
                        output.update({files[j]: value1})
                        print ('{}->{}'.format(files[j], value1))
                        values = reverse.get(value1)
                        values.add(files[j])
                        reverse.update({value1:values})
                    elif output.get(files[i]) is None:
                        value1 = output.get(files[j])
                        output.update({files[i]: value1})
                        print ('{}->{}'.format(files[i], value1))
                        values = reverse.get(value1)
                        values.add(files[i])
                        reverse.update({value1:values})
                    elif output.get(files[i]) is not None and output.get(files[j]) is not None:
                        value1 = output.get(files[i])
                        value2 = output.get(files[j])
                        if value1 != value2:
                            values = reverse.get(value2)
                            for v in values:
                                output.update({v: value1})
                                print ('{}->{}'.format(v, value1))
                            reverse.pop(value2)
                    goodsets.add(files[i])
                    goodsets.add(files[j])
                total_time = total_time + time_use
            except:
                #print '********error comparing two faces*********** ' + files[i] + ',' + files[j]
                failed = failed + 1
    print 'total time used:' + str(total_time)
    #print 'good ones:'
    #print goodsets

    print ('there are {} unique sets found in the images'.format(len(reverse)))
    targetdir = '/home/cmti/workspace/faces/' + args.image_dir
    command = 'mkdir ' + targetdir
    os.system(command)
    index = 1
    for key in reverse.keys():
        values = reverse.get(key)
        print len(values)
        print values
        d2 = targetdir + '/cluster-' + str(index)
        command = 'mkdir ' + d2
        os.system(command)
        index = index + 1
    if len(value) < 10: shutil.rmtree(d2, ignore_errors = True)
    else:
	    for v in values:
	        command = 'cp ' +  args.image_dir + '/' + v + ' ' + d2
	        os.system(command)
#        if len(values) >= 15:
#	   for v in values:
#		command = 'cp ' +  args.image_dir + '/' + v + ' ' + targetdir
#		os.system(command)
    print 'total time used to process this folder:' + args.image_dir + ' is ' + str(total_time) + ' milliseconds'