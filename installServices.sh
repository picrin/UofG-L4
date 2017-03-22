#!/bin/sh
set -ue
cp transvis-db.service /lib/systemd/system/
systemctl enable transvis-db.service
systemctl start transvis-db.service
