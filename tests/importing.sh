# TEST INSTALLATION OF DEPENDENCIES
set -o xtrace
set -e

# Confirm the cv2 module has been installed correctly
sudo /usr/bin/env python3 -c "import cv2; print(cv2.__version__);"

# Confirm the dlib module has been installed correctly
sudo /usr/bin/env python3 -c "import dlib; print(dlib.__version__);"
