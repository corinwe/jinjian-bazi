#!/bin/bash
# 彻底清除微信开发者工具缓存（macOS版本）
# 这是解决代码更新不生效的关键步骤

echo "⚠️ 开始彻底清除微信开发者工具缓存..."
echo "请先完全退出微信开发者工具！"

# 微信开发者工具缓存目录
CACHE_DIRS=(
    "$HOME/Library/Application Support/微信开发者工具"
    "$HOME/Library/Caches/微信开发者工具"
    "$HOME/Library/Preferences/com.tencent.wechat.devtools.plist"
)

# 备份并删除缓存
for dir in "${CACHE_DIRS[@]}"; do
    if [ -d "$dir" ] || [ -f "$dir" ]; then
        echo "🗑️  删除: $dir"
        rm -rf "$dir"
    else
        echo "ℹ️  不存在: $dir"
    fi
done

echo "\n✅ 缓存清除完成！"
echo "\n📋 下一步操作:"
echo "1. 重新启动微信开发者工具"
echo "2. 导入干净的项目文件夹"
echo "3. 点击'编译'按钮"
echo "4. 点击'预览'进行真机测试"

echo "\n⚠️ 注意：Windows用户请删除以下目录:"
echo "- %APPDATA%/微信开发者工具"
echo "- %LOCALAPPDATA%/微信开发者工具"