@echo off
REM ============================================================================
REM NetBackup Policy 本地處理腳本 (Windows)
REM
REM 用途: 將本地的 policies.json 和 slp.json 轉換為知識庫 CSV
REM
REM 前置條件:
REM   1. policies.json 和 slp.json 已從 NBU Server 複製到本目錄
REM   2. retention_level.json 存在於本目錄
REM   3. Python 3.x 已安裝並加入 PATH
REM
REM 使用方式:
REM   雙擊執行或在命令提示字元中執行: process_local_json.bat
REM
REM ============================================================================

setlocal enabledelayedexpansion

REM 設定變數
set SCRIPT_DIR=%~dp0
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_DIR=%SCRIPT_DIR%backups

REM 檔案名稱
set POLICIES_JSON=policies.json
set SLP_JSON=slp.json
set RETENTION_JSON=retention_level.json
set OUTPUT_CSV=policies_llm_final.csv

echo ================================================================
echo   NetBackup Policy 本地處理工具 (Windows) v1.0
echo ================================================================
echo.

REM ============================================================================
REM 環境檢查
REM ============================================================================
echo [步驟 0/4] 環境檢查...

python --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python
    echo.
    echo 請安裝 Python 3: https://www.python.org/downloads/
    echo 安裝時請勾選 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [資訊] %PYTHON_VERSION%
echo.

REM ============================================================================
REM 步驟 1: 檢查必要檔案
REM ============================================================================
echo [步驟 1/4] 檢查必要檔案...

set MISSING_FILES=0

if not exist "%SCRIPT_DIR%%POLICIES_JSON%" (
    echo [錯誤] 找不到 %POLICIES_JSON%
    set MISSING_FILES=1
) else (
    for %%A in ("%SCRIPT_DIR%%POLICIES_JSON%") do (
        set SIZE=%%~zA
        set /a SIZE_MB=!SIZE! / 1048576
        echo [成功] %POLICIES_JSON% 存在 ^(!SIZE_MB! MB^)
    )
)

if not exist "%SCRIPT_DIR%%SLP_JSON%" (
    echo [錯誤] 找不到 %SLP_JSON%
    set MISSING_FILES=1
) else (
    for %%A in ("%SCRIPT_DIR%%SLP_JSON%") do (
        set SIZE=%%~zA
        set /a SIZE_KB=!SIZE! / 1024
        echo [成功] %SLP_JSON% 存在 ^(!SIZE_KB! KB^)
    )
)

if not exist "%SCRIPT_DIR%%RETENTION_JSON%" (
    echo [錯誤] 找不到 %RETENTION_JSON%
    set MISSING_FILES=1
) else (
    echo [成功] %RETENTION_JSON% 存在
)

if %MISSING_FILES%==1 (
    echo.
    echo [錯誤] 缺少必要檔案，請先完成以下步驟：
    echo.
    echo   在 NBU Server 上執行:
    echo     bppllist -allpolicies -json ^> policies.json
    echo     nbstlutil list -slp -json ^> slp.json
    echo.
    echo   傳輸到本機:
    echo     使用 WinSCP 或 FileZilla 下載兩個 JSON 檔案
    echo     或使用 pscp (PuTTY):
    echo       pscp root@nbu-server:/path/to/policies.json .
    echo       pscp root@nbu-server:/path/to/slp.json .
    echo.
    pause
    exit /b 1
)
echo.

REM ============================================================================
REM 步驟 2: 備份舊檔案
REM ============================================================================
echo [步驟 2/4] 備份舊檔案...

if not exist "%BACKUP_DIR%" (
    mkdir "%BACKUP_DIR%"
)

if exist "%SCRIPT_DIR%%OUTPUT_CSV%" (
    copy "%SCRIPT_DIR%%OUTPUT_CSV%" "%BACKUP_DIR%\%OUTPUT_CSV%_%TIMESTAMP%" >nul
    echo [資訊] 已備份: %OUTPUT_CSV%
) else (
    echo [資訊] 無舊檔案需要備份
)

echo [成功] 備份完成: %BACKUP_DIR%
echo.

REM ============================================================================
REM 步驟 3: 生成知識庫 CSV
REM ============================================================================
echo [步驟 3/4] 生成知識庫 CSV...

if not exist "%SCRIPT_DIR%generate_final_csv_complete.py" (
    echo [錯誤] 找不到生成腳本: generate_final_csv_complete.py
    pause
    exit /b 1
)

echo [資訊] 執行 Python 腳本...
cd /d "%SCRIPT_DIR%"
python generate_final_csv_complete.py

if errorlevel 1 (
    echo [錯誤] CSV 生成失敗
    pause
    exit /b 1
)

if exist "%SCRIPT_DIR%%OUTPUT_CSV%" (
    for /f %%A in ('find /c /v "" ^< "%SCRIPT_DIR%%OUTPUT_CSV%"') do set LINES=%%A
    set /a RECORDS=!LINES! - 1
    for %%A in ("%SCRIPT_DIR%%OUTPUT_CSV%") do (
        set SIZE=%%~zA
        set /a SIZE_KB=!SIZE! / 1024
        echo [成功] CSV 生成完成: !RECORDS! 筆記錄 ^(!SIZE_KB! KB^)
    )
) else (
    echo [錯誤] CSV 生成失敗
    pause
    exit /b 1
)
echo.

REM ============================================================================
REM 步驟 4: 驗證輸出
REM ============================================================================
echo [步驟 4/4] 驗證輸出...

echo [資訊] 檢查 CSV 格式...

REM 檢查欄位數量
for /f "usebackq delims=" %%A in ("%SCRIPT_DIR%%OUTPUT_CSV%") do (
    set HEADER=%%A
    goto :count_fields
)
:count_fields
set FIELD_COUNT=0
set TEMP_HEADER=%HEADER%
:loop
for /f "tokens=1* delims=," %%A in ("%TEMP_HEADER%") do (
    set /a FIELD_COUNT+=1
    set TEMP_HEADER=%%B
    if not "%%B"=="" goto :loop
)

if %FIELD_COUNT%==30 (
    echo [成功] 欄位數量正確: %FIELD_COUNT% 個
) else (
    echo [警告] 欄位數量異常: %FIELD_COUNT% 個 ^(預期 30 個^)
)

REM 檢查 retention_source 分佈
echo [資訊] 檢查 retention_source 分佈...
python -c "import csv; data=list(csv.DictReader(open('policies_llm_final.csv', encoding='utf-8'))); sources={}; [sources.update({row.get('retention_source', 'Unknown'): sources.get(row.get('retention_source', 'Unknown'), 0)+1}) for row in data]; [print(f'     {src}: {count} ({count/len(data)*100:.1f}%%)') for src, count in sorted(sources.items())]"

echo.

REM ============================================================================
REM 完成
REM ============================================================================
echo ================================================================
echo   處理完成！
echo ================================================================
echo.
echo 輸出檔案:
echo   %SCRIPT_DIR%%OUTPUT_CSV%
echo.
echo 備份位置:
echo   %BACKUP_DIR%
echo.
echo 下一步:
echo   1. 檢查輸出檔案
echo   2. 上傳到公司知識庫
echo   3. 測試查詢功能
echo.
echo 記錄:
echo   生成時間: %TIMESTAMP%
echo.

pause
