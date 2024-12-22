@echo off
REM 设置代码页为 UTF-8
chcp 65001 >nul
REM 启用延迟变量扩展
setlocal enabledelayedexpansion

REM 设置解压和压缩工具路径
set "UNRAR_PATH=C:\Program Files\WinRAR\UnRAR.exe"
set "RAR_PATH=C:\Program Files\WinRAR\Rar.exe"
set "TARGET_FOLDER=10"

REM 检查解压工具是否存在
if not exist "%UNRAR_PATH%" (
    echo 1~~~解压工具未找到，请检查路径是否正确。
    pause
    exit /b 1
)

REM 检查压缩工具是否存在
if not exist "%RAR_PATH%" (
    echo 1~~~压缩工具未找到，请检查路径是否正确。
    pause
    exit /b 1
)

REM 获取当前脚本执行目录
set "CURRENT_DIR=%~dp0"

REM 输出当前目录，用于调试
echo 1~~~"%CURRENT_DIR%"

REM 1. 遍历当前目录下的 .exe 文件并逐个解压
for %%f in ("%CURRENT_DIR%*.exe") do (
    echo 1~~~ "%%f"

    REM 解压到对应文件夹中
    "%UNRAR_PATH%" x "%%f" "%CURRENT_DIR%" >nul

    for /d %%d in ("%CURRENT_DIR%*") do (
        set "TARGET_FOLDER=%%d"
    )

    echo 2~~~"!TARGET_FOLDER!"
    for %%I in ("!TARGET_FOLDER!") do set "LAST_FOLDER=%%~nxI"
    
    REM 遍历并删除 .url 文件
    FOR /R "%CURRENT_DIR%" %%f IN (*.url) DO (
        echo 2~~~Found file: "%%f"
        findstr /m /c:"flysheep" "%%f" >nul
        if not errorlevel 1 (
            echo Processing: "%%f"
            echo Deleting file: "%%f"
            del "%%f"
        )
    )

    REM 4. 打包处理后的文件夹
    echo 3~~~"%CURRENT_DIR%"
    
    REM 使用引号包裹路径和文件名
    "%RAR_PATH%" a -r "%CURRENT_DIR%!LAST_FOLDER!.rar" ".\!LAST_FOLDER!"
    
    if !ERRORLEVEL! neq 0 (
        echo 打包文件夹 "!TARGET_FOLDER!" 时出现错误！错误代码：!ERRORLEVEL!
        pause
        exit /b 1
    ) else (
        echo 文件夹已成功打包为："%CURRENT_DIR%!LAST_FOLDER!.rar"
    )
)

echo 所有操作完成。
pause
