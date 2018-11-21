# TEST THE PAM INTEGRATION
set -o xtrace
set -e

# Make sure howdy is clean before starting
sudo howdy clear -y || true

# Change active camera to match video 1
sudo sed -i "s,device_path.*,device_path = $PWD\/tests\/video\/match1.m4v,g" /lib/security/howdy/config.ini

# Let howdy add the match face
sudo howdy add -y

# Test the PAM auth
timeout 10 pamtester login $USER authenticate

# Clear the face models and change the camera to video 2
sudo howdy clear -y
sudo sed -i "s,device_path.*,device_path = $PWD\/tests\/video\/match2.m4v,g" /lib/security/howdy/config.ini

# Let howdy add the match face
sudo howdy add -y

# Try to open a elevated session through PAM
timeout 10 pamtester login $USER open_session

# Verify we can close sessions, even though howdy does not use this PAM function
timeout 10 pamtester login $USER close_session

# Clean up
sudo howdy clear -y
sudo sed -i "s,device_path.*,device_path = none,g" /lib/security/howdy/config.ini
