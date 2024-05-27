#!/bin/bash

VERSION=$1

cd custom_components/divera
sed -i "s/0.0.0/${VERSION}/g" manifest.json
zip divera.zip -r ./
