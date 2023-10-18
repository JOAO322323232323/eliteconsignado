#!/bin/bash
rm -rf elite/
git clone https://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@github.com/GabrielYudenich/elite
cd elite/
sudo docker-compose build
sudo docker-compose up -d