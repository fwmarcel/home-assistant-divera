#!/usr/bin/env bash

apt-get update
apt-get install ffmpeg -y

set -e

cd "$(dirname "$0")/.."

python3 -m pip install --requirement requirements.txt
