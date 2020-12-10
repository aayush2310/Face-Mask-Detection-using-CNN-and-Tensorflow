from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tqdm import tqdm
from glob import glob

import tensorflow as tf
import numpy as np
import argparse
import time
import cv2
import os

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input-dir', 
                    help="Directory of input image")
parser.add_argument('-o', '--output-dir', default='data/64x64_dataset', 
                    help="Where to write the extracted data")
parser.add_argument('-s', '--size', default=64, type=int, 
                    help="Size of output face image")
parser.add_argument('-c', '--confidence', default=0.5, type=float, 
                    help='Confidence threadhold to detect face')

def extract_face(filename, output_dir, net, size, confidence_threshold):
    image = cv2.imread(filename)
    filename_out = filename.split('/')[-1].split('.')[0]
    (h, w) = image.shape[:2]

    blob = cv2.dnn.blobFromImage(image, scalefactor=1.0, mean=(104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            color = (0, 255, 0)
            cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)

            try:
                frame = image[startY:endY, startX:endX]
                frame = cv2.resize(frame, (size, size), interpolation=cv2.INTER_AREA)
                if i > 0:
                    image_out = os.path.join(output_dir, '%s_%s.jpg' % (filename_out, i))
                else:
                    image_out = os.path.join(output_dir, '%s.jpg' % filename_out)
                cv2.imwrite(image_out, frame)
            except Exception as e:
                 print(e)
    
    # show the output image
    cv2.imshow("Output", image)
    cv2.waitKey(0)

def app():
    args = parser.parse_args()

    assert os.path.isdir(args.input_dir), "Couldn't find the dataset at {}".format(args.input_dir)
    os.makedirs(args.output_dir, exist_ok=True)

    prototxt_path = os.path.join('face_detector', 'deploy.prototxt')
    weights_ath = os.path.join('face_detector', 'res10_300x300_ssd_iter_140000.caffemodel')
    net = cv2.dnn.readNet(prototxt_path, weights_ath)

    input_imgs = []
    for t in ('jpeg', 'png', 'jpg'):
        input_imgs.extend(glob(args.input_dir + '/*.' + t))

    for filename in tqdm(sorted(input_imgs)):
        extract_face(filename, args.output_dir, net, args.size, args.confidence)
        # time.sleep(1)
    print("Done!")

if __name__ == '__main__':
    app()

