#!/bin/sh

# git@github.com:studeyang/blog.git
url=$1

# 1. git clone
git clone $url

# 2. cut dir

# blog.git
dir_git=${url##*/}
# blog
dir=${dir_git%.*}

# 3. git config
cd $dir
git config --local user.name studeyang
git config --local user.email studeyang@gmail.com

echo "clone success: $url"
