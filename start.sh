#!/bin/bash
# OfferRadar 一键启动
cd "$(dirname "$0")"

echo "==============================="
echo "  OfferRadar"
echo "==============================="
echo ""

# 检查 Python
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then
    echo "[ERROR] 未找到 Python，请先安装 Python 3.9+"
    exit 1
fi
echo "[OK] Python 已就绪"

# 安装依赖
$PY -c "import openpyxl, yaml" 2>/dev/null || {
    echo "[INFO] 首次运行，正在安装依赖..."
    $PY -m pip install openpyxl pyyaml -q
}

# 直接启动
echo ""
echo "  浏览器即将打开: http://127.0.0.1:8686"
echo "  所有配置可在网页上直接修改"
echo "  按 Ctrl+C 停止"
echo ""
$PY -W ignore launcher.py dashboard
