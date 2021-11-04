#!/bin/sh

git add .
git commit -m 'commit by shell'
git push

echo "\033[32m push success. \033[0m"
