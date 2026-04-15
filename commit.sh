#!/bin/sh

git add .
git commit -m $1$2$3
git push

echo -e "\033[7;32m push success: $1$2$3 \033[0m"
