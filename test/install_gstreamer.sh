#!/bin/bash

# 添加必要的仓库
sudo add-apt-repository universe -y
sudo add-apt-repository multiverse -y

# 更新包列表
sudo apt-get update

# 安装GStreamer工具和插件
sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-alsa \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav

# 安装GStreamer开发库
sudo apt-get install -y libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-good1.0-dev \
    libgstreamer-plugins-bad1.0-dev

echo "GStreamer installation completed."
