#!/bin/bash
# 创建绝对干净的小程序打包文件
# 避免旧文件污染新环境

# 配置
VERSION="v2.1.86"
PROJECT_NAME="miniprogram"
SOURCE_DIR="/path/to/miniprogram/project"  # 修改为实际项目路径
TEMP_DIR="/tmp/${PROJECT_NAME}-clean"
OUTPUT_FILE="${PROJECT_NAME}-${VERSION}.tar.gz"

# 创建临时目录
mkdir -p "${TEMP_DIR}"

# 复制必需的小程序文件（根据实际项目结构调整）
cp -r "${SOURCE_DIR}/app.js" "${TEMP_DIR}/"
cp -r "${SOURCE_DIR}/app.json" "${TEMP_DIR}/"
cp -r "${SOURCE_DIR}/app.wxss" "${TEMP_DIR}/"
cp -r "${SOURCE_DIR}/pages" "${TEMP_DIR}/"
cp -r "${SOURCE_DIR}/components" "${TEMP_DIR}/"
cp -r "${SOURCE_DIR}/utils" "${TEMP_DIR}/"
cp -r "${SOURCE_DIR}/images" "${TEMP_DIR}/"

# 确保不包含任何旧文件
cd "${TEMP_DIR}"

# 删除可能存在的旧打包文件
find . -name "*.tar.gz" -delete
find . -name "*.md" -delete
find . -name "*.sh" -delete
find . -name ".DS_Store" -delete

# 创建压缩包
cd "$(dirname "${TEMP_DIR}")"
tar -czf "${OUTPUT_FILE}" "$(basename "${TEMP_DIR}")"

# 验证打包内容
echo "✅ 打包完成: ${OUTPUT_FILE}"
echo "📦 打包内容:"
tar -tzf "${OUTPUT_FILE}" | head -20

echo "\n📋 文件统计:"
tar -tzf "${OUTPUT_FILE}" | wc -l

echo "\n⚠️ 重要提醒:"
echo "1. 导入时选择解压后的文件夹，不是压缩包本身"
echo "2. 必须先彻底清除微信开发者工具缓存"
echo "3. 完全退出微信开发者工具后再重新导入"

# 清理临时目录
rm -rf "${TEMP_DIR}"