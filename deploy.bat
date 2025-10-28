@echo off
echo ========================================
echo Mini-RAG 快速部署脚本 (Windows)
echo ========================================
echo.

:: 检查 Docker 是否已安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Docker，请先安装 Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

:: 检查 docker-compose 是否可用
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 docker-compose
    pause
    exit /b 1
)

echo [信息] Docker 环境检查通过
echo.

:: 检查环境文件
if not exist ".env" (
    if exist ".env.template" (
        echo [提示] 正在创建环境配置文件...
        copy .env.template .env
        echo [警告] 请编辑 .env 文件，配置您的 Azure AI 信息后重新运行此脚本
        echo [警告] 必须配置: AZURE_AI_ENDPOINT 和 AZURE_AI_KEY
        pause
        exit /b 1
    ) else (
        echo [错误] 找不到 .env.template 文件
        pause
        exit /b 1
    )
)

echo [信息] 环境配置文件存在
echo.

:: 创建必要的目录
if not exist "data" mkdir data
if not exist "data\uploads" mkdir data\uploads
if not exist "data\vectorstore" mkdir data\vectorstore

echo [信息] 数据目录已创建
echo.

:: 构建和启动服务
echo [信息] 正在启动 Mini-RAG 服务...
docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 🎉 Mini-RAG 部署成功！
    echo ========================================
    echo.
    echo 📱 Web 界面: http://localhost:8000
    echo 📚 API 文档: http://localhost:8000/docs
    echo 🔍 服务状态: docker-compose ps
    echo 📋 查看日志: docker-compose logs -f
    echo 🛑 停止服务: docker-compose down
    echo.
    echo [提示] 首次启动可能需要几分钟下载依赖...
    echo [提示] 请确保已正确配置 .env 文件中的 Azure AI 信息
    echo.
    
    :: 等待几秒钟让服务启动
    echo [信息] 等待服务启动...
    timeout /t 10 /nobreak > nul
    
    :: 检查服务状态
    docker-compose ps
    
    echo.
    echo [提示] 按任意键打开 Web 界面...
    pause > nul
    start http://localhost:8000
) else (
    echo.
    echo [错误] 服务启动失败，请检查错误信息
    echo [建议] 运行 'docker-compose logs' 查看详细日志
    pause
)