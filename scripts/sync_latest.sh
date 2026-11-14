#!/usr/bin/env bash
# 把某個 claude/* 分支上「最新一天」的資料同步進目前所在的分支（main）。
# 用法：scripts/sync_latest.sh <來源分支名>
# daily-insights 是用 build.py 把 data/YYYY-MM-DD.json + data/threads.json
# 組成單一 index.html，所以要搬：最新的 data/YYYY-MM-DD.json、data/threads.json、
# 以及 build.py 跑出來的 index.html。不搬 build.py 本身（程式要走正常 review）。
# 來源日期比 main 舊就略過。
set -euo pipefail
BRANCH="${1:?usage: sync_latest.sh <source-branch>}"
SRC="origin/${BRANCH}"

newest() { git ls-tree -r --name-only "$1" | grep -E '^data/[0-9]{4}-[0-9]{2}-[0-9]{2}\.json$' | sed 's#^data/##;s#\.json$##' | sort | tail -1 || true; }

src_latest="$(newest "$SRC")"
main_latest="$(newest HEAD)"
if [ -z "$src_latest" ]; then echo "來源分支沒有日期資料，略過"; exit 0; fi
if [ -n "$main_latest" ] && [[ "$src_latest" < "$main_latest" ]]; then
  echo "來源最新 $src_latest 比 main 的 $main_latest 舊，略過"; exit 0
fi

paths=("data/${src_latest}.json")
for p in data/threads.json index.html; do
  if git cat-file -e "${SRC}:${p}" 2>/dev/null; then paths+=("$p"); fi
done

git checkout "$SRC" -- "${paths[@]}"
git add -- "${paths[@]}"
if git diff --cached --quiet; then echo "沒有變更"; exit 0; fi
git -c user.name="github-actions[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
  commit -q -m "Sync ${src_latest} from ${BRANCH}"
echo "synced ${src_latest}"
