#!/usr/bin/env bash

echo ">> Update app"
ssh -vvv -o "StrictHostKeyChecking no" -tt -i rocketleaguekey.pem ubuntu@34.245.214.229 "cd rocket-league-replay && git pull"

echo ">> Update db"
ssh -vvv -o "StrictHostKeyChecking no" -tt -i rocketleaguekey.pem ubuntu@34.245.214.229 "cd rocket-league-replay/rocketleaguereplay && python3 manage.py makemigrations && python3 manage.py migrate"

echo ">> Restart"
ssh -vvv -o "StrictHostKeyChecking no" -tt -i rocketleaguekey.pem ubuntu@34.245.214.229 "sudo supervisorctl reread && sudo supervisorctl update && sudo supervisorctl restart rlreplay-gunicorn && sudo supervisorctl status"
