# Confirm the cv2 module has been installed correctly
echo "cv2 version:"
sudo /usr/bin/env python3 -c "import cv2; print(cv2.__version__);"

# Confirm the face_recognition module has been installed correctly
echo "face_recognition version:"
sudo /usr/bin/env python3 -c "import face_recognition; print(face_recognition.__version__);"
