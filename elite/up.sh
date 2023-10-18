#!/bin/bash
rm -rf eliteconsignado/
git clone https://github.com/JOAO322323232323/eliteconsignado.git
cd eliteconsignado/
sudo docker-compose build
sudo docker-compose up -d
