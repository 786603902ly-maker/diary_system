#!/usr/bin/env bash
# 把 site/（python3 src/build.py 生成的 PWA 版本）推到 gh-pages 分支，GitHub Pages 从该分支发布。
# gh-pages 只放构建产物、每次整体覆盖，和开发分支的历史无关。
# 用法：python3 src/build.py && bash src/deploy_pages.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE="$ROOT/site"
[ -f "$SITE/index.html" ] || { echo "site/ 不存在，先跑 python3 src/build.py" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -R "$SITE"/. "$TMP"/
cd "$TMP"
git init -q -b gh-pages
git add -A
git -c user.name="$(git -C "$ROOT" config user.name || echo deploy)" \
    -c user.email="$(git -C "$ROOT" config user.email || echo deploy@localhost)" \
    commit -q -m "Deploy site from $(git -C "$ROOT" rev-parse --short HEAD)"
git push -f "$(git -C "$ROOT" remote get-url origin)" gh-pages:gh-pages
echo "pushed to gh-pages → https://786603902ly-maker.github.io/diary_system/"
