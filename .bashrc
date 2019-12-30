# this is appended to the end of .bashrc
cd ~/adsb-remote
if [ -n "$SSH_CLIENT" ]; then
  echo "Remote login detected"
else
  echo "Starting ADS-B Remote"
  ./start.sh > debug.log 2>&1
fi