#!/bin/bash

echo "========================================"
echo "Mini-RAG 快速部署脚本 (Linux/Mac)"
echo "========================================"
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查 Docker 是否已安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[错误]${NC} 未检测到 Docker，请先安装 Docker"
    echo "安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 docker-compose 是否可用
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[错误]${NC} 未检测到 docker-compose"
    echo "安装指南: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}[信息]${NC} Docker 环境检查通过"
echo

# 检查环境文件
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo -e "${BLUE}[提示]${NC} 正在创建环境配置文件..."
        cp .env.template .env
        echo -e "${YELLOW}[警告]${NC} 请编辑 .env 文件，配置您的 Azure AI 信息后重新运行此脚本"
        echo -e "${YELLOW}[警告]${NC} 必须配置: AZURE_AI_ENDPOINT 和 AZURE_AI_KEY"
        echo
        echo "编辑命令: nano .env 或 vim .env"
        exit 1
    else
        echo -e "${RED}[错误]${NC} 找不到 .env.template 文件"
        exit 1
    fi
fi

echo -e "${GREEN}[信息]${NC} 环境配置文件存在"
echo

# 创建必要的目录
mkdir -p data/uploads data/vectorstore

echo -e "${GREEN}[信息]${NC} 数据目录已创建"
echo

# 构建和启动服务
echo -e "${BLUE}[信息]${NC} 正在启动 Mini-RAG 服务..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo
    echo "========================================"
    echo -e "🎉 ${GREEN}Mini-RAG 部署成功！${NC}"
    echo "========================================"
    echo
    echo -e "📱 Web 界面: ${BLUE}http://localhost:8000${NC}"
    echo -e "📚 API 文档: ${BLUE}http://localhost:8000/docs${NC}"
    echo -e "🔍 服务状态: ${YELLOW}docker-compose ps${NC}"
    echo -e "📋 查看日志: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "🛑 停止服务: ${YELLOW}docker-compose down${NC}"
    echo
    echo -e "${YELLOW}[提示]${NC} 首次启动可能需要几分钟下载依赖..."
    echo -e "${YELLOW}[提示]${NC} 请确保已正确配置 .env 文件中的 Azure AI 信息"
    echo
    
    # 等待几秒钟让服务启动
    echo -e "${BLUE}[信息]${NC} 等待服务启动..."
    sleep 10
    
    # 检查服务状态
    docker-compose ps
    
    echo
    echo -e "${GREEN}[成功]${NC} 服务已启动，可以访问 http://localhost:8000"
    
    # 在 macOS 上自动打开浏览器
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${BLUE}[信息]${NC} 正在打开浏览器..."
        open http://localhost:8000
    elif command -v xdg-open &> /dev/null; then
        echo -e "${BLUE}[信息]${NC} 正在打开浏览器..."
        xdg-open http://localhost:8000
    fi
    
else
    echo
    echo -e "${RED}[错误]${NC} 服务启动失败，请检查错误信息"
    echo -e "${YELLOW}[建议]${NC} 运行 'docker-compose logs' 查看详细日志"
    exit 1
fi