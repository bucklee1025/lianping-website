#!/bin/bash
# ===== 联屏传媒 自动部署 v2 (API版) =====
# 使用 GitHub API (api.github.com) 代替 git pull
# 解决服务器无法连接 github.com 的问题

TOKEN="3FZrbkGOOdwolLTygx2xuZb57nL"
REPO="bucklee1025/lianping-website"
BRANCH="master"
WEBROOT="/opt/lianping-website"
RAW="https://raw.githubusercontent.com/$REPO/$BRANCH"

echo '=== 联屏传媒 自动部署 v2 (API) ==='
echo ''

# 1. 先尝试获取文件列表 (通过 API)
echo '[1/4] 获取更新文件列表...'
API_URL="https://api.github.com/repos/$REPO/git/trees/$BRANCH?recursive=1"
FILES=$(curl -s -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3+json" \
  "$API_URL" | grep -o '"path":"[^"]*"' | grep -v '^"path":"\.' | cut -d'"' -f4 | grep -v '/$')

if [ -z "$FILES" ]; then
  echo '  API获取失败，尝试直接下载已知文件...'
  FILES="index.html about.html cases.html faq.html process.html news.html
    BingSiteAuth.xml CNAME robots.txt sitemap.xml baidu_verify_codeva-16oPFOUdNy.html"
  for i in $(seq 1 34); do
    FILES="$FILES news/article$i.html"
  done
fi

echo "  待下载: $(echo $FILES | wc -w) 个文件"

# 2. 下载所有文件
echo '[2/4] 下载更新...'
mkdir -p $WEBROOT
COUNT=0
for f in $FILES; do
  DIR=$(dirname "$WEBROOT/$f")
  mkdir -p "$DIR"
  HTTP_CODE=$(curl -s -o "$WEBROOT/$f" -w "%{http_code}" "$RAW/$f" 2>/dev/null)
  if [ "$HTTP_CODE" = "200" ]; then
    COUNT=$((COUNT + 1))
  fi
done
echo "  成功下载 $COUNT 个文件"

# 确保新文章和图片被下载（兼容旧版脚本的列表限制）
echo '  [补丁] 检查缺失的新文件...'
for missing in "news/article34.html" "assets/yulin-beizhan-a3-dengxiang-case.jpg"; do
  if [ ! -f "$WEBROOT/$missing" ]; then
    HTTP_CODE=$(curl -s -o "$WEBROOT/$missing" -w "%{http_code}" "$RAW/$missing" 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
      echo "  补丁下载成功: $missing"
    fi
  fi
done

# 3. 检查 Nginx 配置
echo '[3/4] 检查 Nginx 配置...'
if command -v nginx &> /dev/null; then
  nginx -t 2>/dev/null && echo '  Nginx配置正确' || echo '  Nginx配置有误，请检查'
  systemctl reload nginx 2>/dev/null && echo '  Nginx已重载' || echo '  Nginx重载失败'
else
  echo '  Nginx未安装'
fi

# 4. 更新定时任务
echo '[4/4] 配置自动更新(crontab)...'
CRON_JOB="*/30 * * * * cd $WEBROOT && bash $WEBROOT/deploy-auto.sh 2>&1 >> /var/log/lianping-deploy.log"
(crontab -l 2>/dev/null | grep -v 'lianping-website\|deploy-auto'; echo "$CRON_JOB") | crontab -
echo '  自动更新已配置: 每30分钟检查一次'

echo ''
echo '=== 部署完成 ==='
echo "网站: https://lpmedia.cn"
echo "更新: 每30分钟自动同步(通过API)"
echo '备案: 桂ICP备20250128311号'
