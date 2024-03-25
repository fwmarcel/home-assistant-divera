#!/bin/bash

cd custom_components/divera
cp manifest.json manifest.json.tmp
jq --arg version $1 '.version=$version' manifest.json.tmp > manifest.json
rm manifest.json.tmp

zip divera.zip -r ./
