# SCP部署命令参考

本文档提供从远程服务器拷贝小程序安装包到本地的完整SCP命令和流程。

## 服务器信息

- **公网IP**: `43.162.90.39`
- **用户名**: `root`
- **SSH端口**: `22` (默认)
- **文件路径**: `/root/.openclaw/workspace/offerpath/`

## 可用安装包文件

服务器上已打包好的文件：

1. **完整安装包** (推荐)
   - 文件名: `offerpath-full-v2.1.97-20260418.tar.gz`
   - 大小: 约3.8M
   - 内容: 小程序代码 + API服务器 + 部署脚本

2. **仅小程序安装包**
   - 文件名: `offerpath-miniprogram-v2.1.97-20260418.tar.gz`
   - 大小: 约3.7M
   - 内容: 仅小程序代码

3. **部署文档**
   - `DEPLOYMENT-README.md` - 详细部署说明
   - `SCP-COMMANDS.md` - 本命令参考

## SCP拷贝命令

### 基本命令格式
```bash
scp [选项] 用户名@服务器IP:源文件路径 本地目标路径
```

### 1. 拷贝完整安装包（推荐）
```bash
# 拷贝到当前目录
scp root@43.162.90.39:/root/.openclaw/workspace/offerpath/offerpath-full-v2.1.97-20260418.tar.gz .

# 拷贝到指定目录
scp root@43.162.90.39:/root/.openclaw/workspace/offerpath/offerpath-full-v2.1.97-20260418.tar.gz ~/Downloads/
```

### 2. 拷贝所有相关文件
```bash
# 使用通配符拷贝所有安装包和文档
scp root@43.162.90.39:/root/.openclaw/workspace/offerpath/offerpath-*.tar.gz .
scp root@43.162.90.39:/root/.openclaw/workspace/offerpath/*.md .
```

### 3. 带进度显示和压缩传输
```bash
# 显示进度和压缩传输（大文件时有用）
scp -C -v root@43.162.90.39:/root/.openclaw/workspace/offerpath/offerpath-full-v2.1.97-20260418.tar.gz .
```

## 连接测试命令

在拷贝前，可先测试连接和文件是否存在：

```bash
# 测试SSH连接是否通畅
ssh root@43.162.90.39 "echo '连接成功'"

# 查看服务器上文件列表
ssh root@43.162.90.39 "ls -lh /root/.openclaw/workspace/offerpath/offerpath-*.tar.gz"

# 查看文件详细信息
ssh root@43.162.90.39 "stat /root/.openclaw/workspace/offerpath/offerpath-full-v2.1.97-20260418.tar.gz"
```

## 本地解压和部署

### 解压命令
```bash
# 解压到当前目录
 tar -xzf offerpath-full-v2.1.97-20260418.tar.gz

# 解压到指定目录
 tar -xzf offerpath-full-v2.1.97-20260418.tar.gz -C ~/Projects/
```

### 解压后目录结构
```
offerpath/
├── miniprogram/          # 小程序源代码
│   ├── pages/           # 页面文件
│   ├── utils/           # 工具函数
│   └── app.js           # 小程序入口
├── api-server.js        # API服务器
├── start-api.sh         # 启动脚本
├── DEPLOYMENT-README.md # 部署说明
└── SCP-COMMANDS.md      # 本文件
```

## 常见问题解决

### 1. 连接被拒绝
```bash
# 错误：ssh: connect to host 43.162.90.39 port 22: Connection refused
```
**解决**:
- 确认服务器IP正确
- 确认服务器SSH服务正在运行 `service ssh status`
- 确认本地防火墙未阻止22端口
- 确认云服务商安全组已开放22端口

### 2. 认证失败
```bash
# 错误：Permission denied (publickey,password).
```
**解决**:
- 确认使用正确的用户名 `root`
- 确认SSH密钥正确或密码正确
- 尝试添加 `-v` 参数查看详细错误信息

### 3. 文件不存在
```bash
# 错误：No such file or directory
```
**解决**:
- 先用SSH命令查看文件是否存在
- 检查文件路径是否正确
- 文件名可能因版本更新而变化，使用通配符 `offerpath-*.tar.gz`

### 4. 传输速度慢
**解决**:
- 添加 `-C` 参数启用压缩传输
- 确保网络连接稳定
- 可考虑先下载到跳板机再传输

## 自动化脚本

创建本地部署脚本 `deploy-local.sh`：

```bash
#!/bin/bash

SERVER_IP="43.162.90.39"
REMOTE_PATH="/root/.openclaw/workspace/offerpath"
LOCAL_DIR="./offerpath-deploy"

echo "1. 创建本地目录..."
mkdir -p $LOCAL_DIR
cd $LOCAL_DIR

echo "2. 从服务器拷贝文件..."
scp root@$SERVER_IP:$REMOTE_PATH/offerpath-full-*.tar.gz .
scp root@$SERVER_IP:$REMOTE_PATH/DEPLOYMENT-README.md .

echo "3. 解压安装包..."
tar -xzf offerpath-full-*.tar.gz

echo "4. 查看部署说明..."
cat DEPLOYMENT-README.md | head -20

echo "\n部署文件已准备就绪在: $(pwd)"
ls -la
```

## 安全建议

1. **使用SSH密钥认证** 而非密码
2. **限制IP访问** 在云安全组中设置
3. **定期更新** 安装包版本
4. **验证文件完整性** 下载后检查MD5
   ```bash
   ssh root@43.162.90.39 "md5sum /root/.openclaw/workspace/offerpath/offerpath-full-*.tar.gz"
   md5sum offerpath-full-*.tar.gz
   ```