from keras.layers import Dense

import numpy as np
import os

import cv2

import dlib
import os.path
from keras.models import Sequential
from keras.applications.resnet50 import ResNet50

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(PACKAGE_ROOT,
                          "face_detector.dat")

resnet_model_path = os.path.join(PACKAGE_ROOT,
                                 "model-resnet.h5")


cnn_face_detector = dlib.cnn_face_detection_model_v1(model_path)

resnet = ResNet50(include_top=False, pooling='avg')
model = Sequential()
model.add(resnet)
model.add(Dense(5, activation='softmax'))
model.layers[0].trainable = False
model.load_weights(resnet_model_path)

def score_mapping(modelScore):
    if modelScore <= 3.4:
        mappingScore = 5/3 * modelScore + 5/6
    elif modelScore <= 4:
        mappingScore = 5/2 * modelScore - 2
    elif modelScore < 5:
        mappingScore = modelScore + 4

    return mappingScore


def scores(path):
    im0 = cv2.imread(os.path.join(path))

    if im0.shape[0] > 1280:
        new_shape = (1280, im0.shape[1] * 1280 / im0.shape[0])
    elif im0.shape[1] > 1280:
        new_shape = (im0.shape[0] * 1280 / im0.shape[1], 1280)
    elif im0.shape[0] < 640 or im0.shape[1] < 640:
        new_shape = (im0.shape[0] * 2, im0.shape[1] * 2)
    else:
        new_shape = im0.shape[0:2]

    im = cv2.resize(im0, (int(new_shape[1]), int(new_shape[0])))
    dets = cnn_face_detector(im, 0)

    OUT = []
    for i, d in enumerate(dets):
        face = [d.rect.left(), d.rect.top(), d.rect.right(), d.rect.bottom()]
        face[0] = max(0, face[1])
        face[1] = max(0, face[1])
        face[2] = min(im.shape[1] - 1, face[2])
        face[3] = min(im.shape[0] - 1, face[3])
        croped_im = im[face[1]:face[3], face[0]:face[2], :]
        try:
            resized_im = cv2.resize(croped_im, (224, 224))
        except:
            break
        normed_im = np.array([(resized_im - 127.5) / 127.5])

        pred = model.predict(normed_im)
        ldList = pred[0]
        out = (1 * ldList[0] + 2 * ldList[1] + 3 * ldList[2] + 4 * ldList[3]
               + 5 * ldList[4])
        OUT.append(score_mapping(out))
    return OUT
