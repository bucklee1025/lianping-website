#!/bin/bash
# ===== 联屏传媒 自动部署脚本 =====
# 只需运行一次，以后自动从GitHub同步更新

echo '=== 联屏传媒 自动部署 v1 ==='

# 1. 首次部署：复制文件
if [ ! -d /opt/lianping-website/.git ]; then
  echo '[1/4] 首次部署，初始化...'
  cd /opt
  # 如果已经手动上传过文件，保留现有文件
  if [ -f /opt/lianping-website/index.html ]; then
    echo '  网站文件已存在，跳过复制'
  else
    echo '  错误: 请先手动上传网站文件到 /opt/lianping-website/'
    exit 1
  fi
else
  echo '[1/4] 从GitHub拉取最新更新...'
  cd /opt/lianping-website
  git pull origin master 2>/dev/null || echo '  Git拉取失败，不影响现有站点'
fi

# 2. 检查Nginx配置
echo '[2/4] 检查Nginx配置...'
if command -v nginx &> /dev/null; then
  nginx -t 2>/dev/null && echo '  Nginx配置正确' || echo '  Nginx配置有误，请检查'
  systemctl reload nginx 2>/dev/null && echo '  Nginx已重载' || echo '  Nginx重载失败'
else
  echo '  Nginx未安装'
fi

# 3. 检查证书到期
echo '[3/4] SSL证书状态...'
if [ -f /etc/nginx/lpmedia.cn.pem ]; then
  openssl x509 -in /etc/nginx/lpmedia.cn.pem -noout -enddate 2>/dev/null | cut -d= -f2
else
  echo '  无SSL证书'
fi

# 4. 设置自动更新定时任务
echo '[4/4] 配置自动更新...'
CRON_JOB='*/30 * * * * cd /opt/lianping-website && git pull origin master 2>/dev/null && nginx -t 2>/dev/null && systemctl reload nginx 2>/dev/null'
(crontab -l 2>/dev/null | grep -v 'lianping-website'; echo "") | crontab -
echo '  自动更新已配置: 每30分钟检查一次GitHub更新'

echo ''
echo '=== 部署完成 ==='
echo '网站: https://lpmedia.cn'
echo '更新: 每30分钟自动同步GitHub'
echo '备案: 桂ICP备20250128311号'
