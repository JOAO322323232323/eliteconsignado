#!/bin/bash
rm -rf elite/
git clone git@github.com:JOAO322323232323/eliteconsignado.git
cd elite-main/
sudo docker-compose build
sudo docker-compose up -d
