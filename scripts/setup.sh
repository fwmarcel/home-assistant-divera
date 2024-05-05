#!/usr/bin/env bash

apt-get update
apt-get install ffmpeg -y

set -e

cd "$(dirname "$0")/.."

rm -rf .venv
pip3 install uv==0.1.24
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
