#!/bin/sh
# Push portfolio site to GitHub. Run from project root: /Users/zhoutonya
# First time: create repo at https://github.com/new (e.g. name: portfolio)
# Then run: sh push-to-github.sh

set -e
GIT_DIR=/tmp/portfolio-site.git
WORK_TREE=/Users/zhoutonya

export GIT_DIR
export GIT_WORK_TREE

cd "$WORK_TREE"
git push -u origin main
echo "Done. Site pushed to origin/main."
