@echo off
REM 设置代码页为 UTF-8
chcp 65001 >nul

REM 检查是否已安装 Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker 未安装，请先安装 Docker。
    exit /b 1
)

REM 构建 Docker 镜像
docker build -t ziyuan_image .

REM 启动 Docker 容器
docker run --rm -p 5000:5000 ziyuan_image

pause