#!/bin/zsh
# Shop Gọn — cài ROBOT HÀNG CHỜ TRUYỀN THÔNG lên Mac mini (chạy 1 lần; chạy lại = cập nhật).
# Dùng:  zsh cai-mac-mini.sh <HC_URL> <HC_KEY>
# Robot chạy nền mỗi 2 phút (launchd), không mở cửa sổ, không chiếm màn hình. Nhật ký: ~/shopgon-robot/robot.log
set -e
DIR="$HOME/shopgon-robot"; ENVF="$HOME/.shopgon-robot.env"; PL="$HOME/Library/LaunchAgents/vn.shopgon.hangcho.plist"
mkdir -p "$DIR"; cd "$DIR"
if [ -n "$1" ] && [ -n "$2" ]; then printf 'HC_URL=%s\nHC_KEY=%s\n' "$1" "$2" > "$ENVF"; chmod 600 "$ENVF"; fi
[ -f "$ENVF" ] || { echo "Thiếu HC_URL / HC_KEY: zsh cai-mac-mini.sh <HC_URL> <HC_KEY>"; exit 1; }
NODE="$(command -v node || true)"; [ -n "$NODE" ] || { echo "Mac mini chưa có Node.js"; exit 1; }
curl -fsSL "https://shopgon.vn/robot/hang-cho.mjs?v=$(date +%s)" -o hang-cho.mjs
[ -f package.json ] || echo '{"name":"shopgon-robot","private":true,"type":"module"}' > package.json
[ -d node_modules/playwright ] || npm i playwright@1.48.2 --silent
npx playwright install chromium >/dev/null
cat > "$PL" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
 <key>Label</key><string>vn.shopgon.hangcho</string>
 <key>ProgramArguments</key><array><string>$NODE</string><string>$DIR/hang-cho.mjs</string></array>
 <key>WorkingDirectory</key><string>$DIR</string>
 <key>StartInterval</key><integer>120</integer>
 <key>RunAtLoad</key><true/>
 <key>LowPriorityIO</key><true/>
 <key>Nice</key><integer>10</integer>
 <key>StandardOutPath</key><string>$DIR/robot.log</string>
 <key>StandardErrorPath</key><string>$DIR/robot.log</string>
</dict></plist>
EOF
launchctl bootout gui/$(id -u) "$PL" 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$PL"
echo "✅ Robot hàng chờ đã chạy nền (mỗi 2 phút). Nhật ký: $DIR/robot.log"
