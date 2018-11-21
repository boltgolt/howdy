# TEST INSTALLATION OF DEPENDENCIES
set -o xtrace
set -e

# Confirm the cv2 module has been installed correctly
sudo /usr/bin/env python3 -c "import cv2; print(cv2.__version__);"

# Confirm the face_recognition module has been installed correctly
sudo /usr/bin/env python3 -c "import face_recognition; print(face_recognition.__version__);"
