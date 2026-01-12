@echo off
chcp 65001
echo ==========================================
echo      XiaoMusic Windows 本地启动脚本
echo ==========================================

echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到 Python。请先安装 Python 3.10+ 并勾选 "Add Python to PATH"。
    pause
    exit /b
)

echo [2/4] 检查 FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未检测到 FFmpeg。这可能会导致无法播放或转换音频。
    echo 请下载 FFmpeg 并将其 bin 目录添加到系统环境变量 PATH 中。
    echo 下载地址: https://ffmpeg.org/download.html
    echo.
    echo 按任意键继续尝试运行（如果不涉及转码可能也能运行）...
    pause
)

echo [3/4] 安装/更新依赖...
echo 正在安装 PDM...
pip install -U pdm
echo 正在安装项目依赖...
pdm install

echo [4/4] 启动 XiaoMusic...
echo 请确保您已在环境变量或配置文件中设置了小米账号信息。
echo 或者，您可以编辑此脚本，在下方添加参数，例如:
echo pdm run xiaomusic --account 13800000000 --password yourpassword --did ""

:: 在此处修改启动参数，例如添加 --account 和 --password
pdm run xiaomusic

pause
