@echo off
REM 设置代码页为 UTF-8
chcp 65001 >nul
REM 启用延迟变量扩展
setlocal enabledelayedexpansion

REM 设置解压和压缩工具路径
set UNRAR_PATH="C:\Program Files\WinRAR\UnRAR.exe"
set RAR_PATH="C:\Program Files\WinRAR\Rar.exe"
set TARGET_FOLDER=10



REM 检查解压工具是否存在
if not exist %UNRAR_PATH% (
    echo 1~~~解压工具未找到，请检查路径是否正确。
    pause
    exit /b 1
)

REM 检查压缩工具是否存在
if not exist %RAR_PATH% (
    echo 1~~~压缩工具未找到，请检查路径是否正确。
    pause
    exit /b 1
)

REM 获取当前脚本执行目录
set CURRENT_DIR=%~dp0

REM 输出当前目录，用于调试
echo 1~~~%CURRENT_DIR%

REM 1. 遍历当前目录下的 .exe 文件并逐个解压
for %%f in (%CURRENT_DIR%*.exe) do (
    echo 1~~~ %%f

    REM 解压到对应文件夹中
    %UNRAR_PATH% x "%%f" "%CURRENT_DIR%\" >null

    for /d %%d in (%CURRENT_DIR%*) do (
        set TARGET_FOLDER=%%d
        REM 显示延迟扩展的变量值
    )

    echo 2~~~!TARGET_FOLDER!
    for %%I in ("!TARGET_FOLDER!") do set LAST_FOLDER=%%~nxI
    :: 遍历 TARGET_FOLDER 下的所有 .url 文件，并增加调试输出
    FOR /R "%CURRENT_DIR%" %%f IN (**.url) DO (
        echo 2~~~Found file: %%f

        :: 检查文件是否包含指定内容
        findstr /m /c:"flysheep" "%%f" >nul
        if not errorlevel 1 (
            echo Processing: %%f
            echo Deleting file: %%f
            del "%%f"
        )
    )

    REM 4. 打包处理后的文件夹
    echo 3~~~%CURRENT_DIR%

    REM 提取最后一个文件夹名称
    %RAR_PATH% a -r "%CURRENT_DIR%!LAST_FOLDER!.rar" ".\!LAST_FOLDER!"
    REM 检查打包是否成功
    if %ERRORLEVEL% neq 0 (
        echo 打包文件夹 %CURRENT_DIR% 时出现错误！错误代码：%ERRORLEVEL%
        pause
        exit /b 1
    ) else (
        echo 文件夹已成功打包为：%CURRENT_DIR%!LAST_FOLDER!.rar
    )
goto: end
)

:end
echo 所有操作完成。
pause
