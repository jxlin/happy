# -*- encoding:utf-8 -*-
__date__ = "18/9/18"
__author__  = "jensen"
 
 
import os
import shutil
 
 
 
import numpy as np
import os
import sys
import argparse
import glob
import time
from PIL import Image
from StringIO import StringIO
import caffe
 
 
 
def resize_image(data, sz=(256, 256)):
    """
    Resize image. Please use this resize logic for best results instead of the 
    caffe, since it was used to generate training dataset 
    """
    img_data = str(data)
    im = Image.open(StringIO(img_data))
    if im.mode != "RGB":
        im = im.convert('RGB')
    imr = im.resize(sz, resample=Image.BILINEAR)
    fh_im = StringIO()
    imr.save(fh_im, format='JPEG')
    fh_im.seek(0)
    return bytearray(fh_im.read())
 
def caffe_preprocess_and_compute(pimg, caffe_transformer=None, caffe_net=None,
    output_layers=None):
    """
    Run a Caffe network on an input image after preprocessing it to prepare
    it for Caffe.
    """
    if caffe_net is not None:
 
        # Grab the default output names if none were requested specifically.
        if output_layers is None:
            output_layers = caffe_net.outputs
 
        img_data_rs = resize_image(pimg, sz=(256, 256))
        image = caffe.io.load_image(StringIO(img_data_rs))
 
        H, W, _ = image.shape
        _, _, h, w = caffe_net.blobs['data'].data.shape
        h_off = max((H - h) / 2, 0)
        w_off = max((W - w) / 2, 0)
        crop = image[h_off:h_off + h, w_off:w_off + w, :]
        transformed_image = caffe_transformer.preprocess('data', crop)
        transformed_image.shape = (1,) + transformed_image.shape
 
        input_name = caffe_net.inputs[0]
        all_outputs = caffe_net.forward_all(blobs=output_layers,
                    **{input_name: transformed_image})
 
        outputs = all_outputs[output_layers[0]][0].astype(float)
        return outputs
    else:
        return []
 
 
def detact(model_def, pretrained_model, input_file):
    
    pycaffe_dir = os.path.dirname(__file__)
 
    #args = parser.parse_args()
    image_data = open(input_file).read()
 
    # Pre-load caffe model.
    nsfw_net = caffe.Net(model_def,  # pylint: disable=invalid-name
        pretrained_model, caffe.TEST)
 
    # Load transformer
    # Note that the parameters are hard-coded for best results
    caffe_transformer = caffe.io.Transformer({'data': nsfw_net.blobs['data'].data.shape})
    caffe_transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost
    caffe_transformer.set_mean('data', np.array([104, 117, 123]))  # subtract the dataset-mean value in each channel
    caffe_transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
    caffe_transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR
 
    # Classify.
    scores = caffe_preprocess_and_compute(image_data, caffe_transformer=caffe_transformer, caffe_net=nsfw_net, output_layers=['prob'])
 
    # Scores is the array containing SFW / NSFW image probabilities
    # scores[1] indicates the NSFW probability
    print("NSFW score:  " , scores[1])
 
    return scores[1]