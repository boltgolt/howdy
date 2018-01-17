# Howdy for Ubuntu

Windows Hello™ style authentication for Ubuntu. Use your build in IR emitters and camera in combination with face recognition to prove who you are.

### Installation

Fist we need to install pam-python, fswebcam and OpenCV from the Ubuntu repositories:

```
sudo apt install libpam-python fswebcam libopencv-dev python-opencv
```

After that, install the face_recognition python module. There's an excellent step by step guide on how to do this on [its github page](https://github.com/ageitgey/face_recognition#installation).

In the root of your cloned repo is a file called `config.ini`. The `device_id` variable in this file is important, make sure it is the IR camera and not your normal webcam.

Now it's time to let Howdy learn your face. The learn.py script will make 3 models of your face and store them as an encoded set in the `models` folder. To run the script, open a terminal, navigate to this repository and run:

```
python3 learn.py
```

The script should guide you through the process.

Finally we need to tell PAM that there's a new module installed. Open `/etc/pam.d/common-auth` as root (`sudo nano /etc/pam.d/common-auth`) and add the following line to the top of the file:

```
auth sufficient pam_python.so /path/to/pam.py
```

Replace the final argument with the full path to pam.py in this repository. The `sufficient` control tells PAM that Howdy is enough to authenticate the user, but if it fails we can fall back on more traditional methods.

If nothing went wrong we should be able to run sudo by just showing your face. Open a new terminal and run `sudo -i` to see it in action.

### Troubleshooting

Any errors in the script itself get logged directly into the console and should indicate what went wrong. If authentication still fails but no errors are printed you could take a look at the last lines in `/var/log/auth.log` to see if anything has been reported there.
