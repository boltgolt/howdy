# TEST MODEL-FRAME COMPARE FUNCTIONS
set -o xtrace
set -e

# Make sure howdy is clean before starting
sudo howdy clear -y || true

# Learn match 1
sudo sed -i "s,device_path.*,device_path = $PWD\/tests\/video\/match1.m4v,g" /lib/security/howdy/config.ini
sudo howdy add -y

# Text compare matching with same camera input
sudo python3 /lib/security/howdy/compare.py $USER

# Change to match 2 and compare against the modal of match 1, which should fail
sudo sed -i "s,device_path.*,device_path = $PWD\/tests\/video\/match2.m4v,g" /lib/security/howdy/config.ini
! sudo python3 /lib/security/howdy/compare.py $USER

# Add match 2 as a model to compare both 1 and 2 at the same time
sudo howdy add -y
sudo python3 /lib/security/howdy/compare.py $USER

# Compare against a camera with no visible face
sudo sed -i "s,device_path.*,device_path = $PWD\/tests\/video\/noMatch.m4v,g" /lib/security/howdy/config.ini
! sudo python3 /lib/security/howdy/compare.py $USER

# Clean up
sudo howdy clear -y
sudo sed -i "s,device_path.*,device_path = none,g" /lib/security/howdy/config.ini
