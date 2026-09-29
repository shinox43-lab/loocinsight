#!/usr/bin/env bash
# loocinsight 一鍵部署：確保搜尋隱藏 CSS 已注入 → 部署到 Cloudflare Pages（project loocinsight）
# 用法：./deploy.sh
# 注意：loocinsight 係 WordPress 靜態鏡像，唔經 Claude Design；改內容＝重新 mirror .wpress 後再跑此檔。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SITE="$HERE/site"
[ -f "$SITE/index.html" ] || { echo "❌ $SITE 冇 index.html"; exit 1; }

echo "▶ 移除已確認的 WordPress 注入文章卡片（idempotent）"
python3 "$HERE/remove-injected-posts.py" "$SITE"

echo "▶ 確保搜尋隱藏 CSS 已注入（idempotent）"
python3 "$HERE/hide-search.py" "$SITE"

echo "▶ 部署 production（loocinsight）"
npx wrangler pages deploy "$SITE" --project-name=loocinsight --branch=main
echo "✅ 完成（真域名 loocinsight.com；M365 email 不受影響）"
