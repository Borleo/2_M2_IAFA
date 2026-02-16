#!/bin/zsh

# Lance client1.py en arrière-plan
python ./client_1.py &
# Lance client2.py en arrière-plan
python ./client_2.py &

# Attend que tous les processus en arrière-plan se terminent
wait