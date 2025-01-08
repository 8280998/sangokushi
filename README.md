# sangokushi三国志自动模拟脚本介绍

读取user.txt的用户和密码后，自动登录网站根据以下模块处理不同任务

user.txt：登录用户配置文件，用户名和密码使用｜隔开

quest.py:自动讨伐据点

bonus.py:自动领取每日奖励

yellow.py：自动打黄巾活动

claim.py：自动领取黄巾活动奖励

point.py：查询每个帐号的BP积分

auto.sh: 自动处理每天的bonus领取奖励和quest讨伐循环脚本

autoyellow.sh:黄巾活动循环脚本。
______________________________________________________________
感谢openai，各个功能模块是在chatgpt的帮助下完成。
因为是陆续完成的，所以各个模块没合并到一个程序中。
______________________________________________________________

使用说明：

1.运行系统为ubuntu22.04

安装环境命令

sudo apt update

sudo apt install -y libnss3 libatk-bridge2.0-0 libcups2 libxcomposite1 libxrandr2 libxdamage1 libgbm-dev libxshmfence-dev fonts-liberation

sudo apt-get install python3-pip

pip install playwright

playwright install

playwright install-deps

2.运行各个模块

在运行前，需要先把用户名密码复制到user.txt中，一行一个用户。
用户名和密码使用｜隔开。
______________________________________________________________
nohup ./auto.sh > auto.log 2>&1 &

在后台运行bonus.py和quest.py。在运行时会先停止正在运行的quest.py.
为确保每个帐号都不错过每日奖励，bonus会运行二次。然后重新运行quest.py
50个登录帐号每天循环一次bonus.py，大约为1310分钟。
不同数量的登录帐号，需要自定义循环时间。因为bonus每天只领取一次。

使用tail -f run.log查看quest运行时日志

使用tail -f bonus.log查看bonus运行时日志

______________________________________________________________
nohup ./autoyellow.sh > autoyellow.log 2>&1 &

在后台运行yellow.py，所有用户处理完成后，等待10分钟再次循环打活动。
sleep 10m可以自定义循环时间

______________________________________________________________
领取黄巾活动奖励
python3 claim.py

帐号积分查询
python3 point.py

单独运行黄巾活动
python3 yellow.py

单独运行quest讨伐模块
python3 quest.py

单独运行bonus每日奖励领取模块
python3 bonus.py
______________________________________________________________
待优化
