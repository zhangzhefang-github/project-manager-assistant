#!/bin/bash

echo "🔄 应用项目管理助手优化修复..."
echo ""

# 停止现有进程
echo "1. 停止现有服务..."
pkill -f "uvicorn app.api.main"
pkill -f "rq worker"
pkill -f "streamlit run"

# 等待进程完全停止
sleep 2

# 创建日志目录
echo "2. 准备日志系统..."
mkdir -p logs

# 重启服务
echo "3. 启动优化后的服务..."
echo "   - 📊 日志已优化：控制台显示减少，详细日志保存到 logs/ 目录"
echo "   - 🔧 进度追踪已增强：支持实时节点状态和自动重连"
echo "   - 🌐 中文化已完善：所有输出内容现在都是中文"
echo ""

# 启动服务
./run.sh &

echo ""
echo "✅ 修复应用完成！"
echo ""
echo "📋 验证方法："
echo "1. 打开 http://localhost:8501"
echo "2. 提交一个新的项目计划"
echo "3. 观察进度条是否流畅更新（不再卡在20%）"
echo "4. 检查输出的任务名称是否为中文"
echo "5. 查看控制台日志输出是否减少"
echo ""
echo "📁 日志文件位置："
echo "- 应用日志: logs/app.log"
echo "- 错误日志: logs/error.log"
echo "- FastAPI日志: logs/fastapi.log"
echo "- Worker日志: logs/worker.log" 