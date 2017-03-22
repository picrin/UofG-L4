#!/bin/sh
set -ue
cp transvis-db.service /lib/systemd/system/
cp transvis-backend.service /lib/systemd/system/
systemctl enable transvis-db.service
systemctl start transvis-db.service
systemctl enable transvis-backend.service
systemctl start transvis-backend.service
