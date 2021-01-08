#!/bin/bash

echo "Downloading 3 required data files..."

# Check if wget is installed
if hash wget;then
	# Check if wget supports the option to only show the progress bar
	wget --help | grep -q "\--show-progress" && \
		_PROGRESS_OPT="-q --show-progress" || _PROGRESS_OPT=""

	# Download the archives
	wget $_PROGRESS_OPT --tries 5 https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2
	wget $_PROGRESS_OPT --tries 5 https://github.com/davisking/dlib-models/raw/master/mmod_human_face_detector.dat.bz2
	wget $_PROGRESS_OPT --tries 5 https://github.com/davisking/dlib-models/raw/master/shape_predictor_5_face_landmarks.dat.bz2

# Otherwise fall back on curl
else
	curl --location --retry 5 --output dlib_face_recognition_resnet_model_v1.dat.bz2 https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2
	curl --location --retry 5 --output mmod_human_face_detector.dat.bz2 https://github.com/davisking/dlib-models/raw/master/mmod_human_face_detector.dat.bz2
	curl --location --retry 5 --output shape_predictor_5_face_landmarks.dat.bz2 https://github.com/davisking/dlib-models/raw/master/shape_predictor_5_face_landmarks.dat.bz2
fi

# Uncompress the data files and delete the original archive
echo " "
echo "Unpacking..."
bzip2 -d -f *.bz2
