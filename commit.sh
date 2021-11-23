#!/bin/sh

git add .
git commit -m '$0'
git push

echo "\033[32m push success: $0 \033[0m"
