#!/bin/bash

# 循环执行 24 小时一次
while true; do
    # 查找进程中包含 "python3 quest.py" 的进程并杀掉
    pid=$(pgrep -f "quest.py")
    if [ ! -z "$pid" ]; then
        echo "结束进程quest.py, PID: $pid"
        kill -9 $pid
    else
        echo "没有找到quest.py 进程"
    fi

    # 等待 5 秒
    rm -rf *.png
    rm -rf bonus.log
    rm -rf run.log
    sleep 5

    # 运行 python3 bonus.py
    echo "运行 python3 bonus.py"
    python3 bonus.py
    python3 bonus.py

    # 启动 nohup python3 quest.py
    python3 quest.py &
    echo "等待 24 小时"
    sleep 1310m
done
