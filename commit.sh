#!/bin/sh

git add .
git commit -m $1
git push

echo "\033[32m push success: $1 \033[0m"
