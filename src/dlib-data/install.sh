#!/bin/bash

# Download the archives
wget https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2
wget https://github.com/davisking/dlib-models/raw/master/mmod_human_face_detector.dat.bz2
wget https://github.com/davisking/dlib-models/raw/master/shape_predictor_5_face_landmarks.dat.bz2

# Uncompress the data files and delete the original archive
echo "Unpacking..."
bzip2 -d *.bz2
