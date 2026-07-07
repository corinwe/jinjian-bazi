# Hermes bash wrapper 无限递归修复

## 问题现象
执行 `hermes` 命令时，进程不断 fork 自身，CPU 飙升。

## 原因分析
安装脚本生成的 bash wrapper `/usr/local/bin/hermes` 内容为：
```bash
#!/bin/bash
exec hermes "$@"
```
这导致 `hermes` 命令调用自身，形成无限递归。

## 解决方案

### 方法一：创建符号链接（推荐）
```bash
# 删除有问题的 bash wrapper
rm /usr/local/bin/hermes

# 创建指向 venv 中 Python 可执行文件的符号链接
ln -sf /usr/local/lib/hermes-agent/venv/bin/hermes /usr/local/bin/hermes
```

### 方法二：直接调用 Python 模块
```bash
# 绕过 bash wrapper，直接启动 gateway 模块
/usr/local/lib/hermes-agent/venv/bin/python -m hermes.gateway.run
```

## 验证修复
```bash
# 检查符号链接是否正确
ls -la /usr/local/bin/hermes
# 应显示：/usr/local/bin/hermes -> /usr/local/lib/hermes-agent/venv/bin/hermes

# 测试命令是否正常
hermes --help
```