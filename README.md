# Zenith - 滑动关机

## 简介

Zenith 是一款简单易用的滑动关机工具，允许用户通过滑动鼠标来触发关机操作。该工具提供了直观的图形用户界面（GUI）和系统托盘图标，方便用户进行设置和操作。

## 功能介绍

### 滑动区域设置

- **功能**：设置屏幕顶部的区域，用户需要在这个区域内开始滑动操作。
- **操作**：在"滑动区域"部分，通过滑块调整屏幕顶部区域的百分比。

### 滑动距离设置

- **功能**：设置滑动的最小距离，滑动距离达到此值时将触发关机操作。
- **操作**：在"滑动距离"部分，通过滑块调整滑动距离的像素值。

### 开机自启

- **功能**：设置程序是否在开机时自动启动。
- **操作**：在"开机自启"部分，勾选或取消勾选复选框以启用或禁用开机自启功能。

### 托盘图标

- **功能**：程序最小化到系统托盘，通过托盘图标可以快速显示或退出程序。
- **操作**：右键点击托盘图标，选择"显示窗口"或"退出"。

## 使用教程

### 启动程序

1. 双击运行程序，程序将自动最小化到系统托盘。
2. 右键点击托盘图标，选择"显示窗口"以显示主界面。

### 调整设置

1. **滑动区域设置**：
   - 在主界面中找到"滑动区域"部分。
   - 拖动滑块调整屏幕顶部区域的百分比。

2. **滑动距离设置**：
   - 在主界面中找到"滑动距离"部分。
   - 拖动滑块调整滑动距离的像素值。

3. **开机自启设置**：
   - 在主界面中找到"开机自启"部分。
   - 勾选或取消勾选复选框以启用或禁用开机自启功能。

### 使用滑动关机

1. 确保程序已启动并处于监听状态。
2. 将鼠标移到屏幕顶部区域（由"滑动区域"设置决定）。
3. 按住鼠标右键并向下拖动。
4. 拖动距离达到"滑动距离"设置后，将调用关机操作。

### 隐藏/退出程序

- **隐藏程序**：点击窗口的关闭按钮，程序将最小化到系统托盘。
- **退出程序**：右键点击托盘图标，选择"退出"。

## 配置文件说明

程序的配置文件存储在`%APPDATA%/Zenith/config.json`中，包含以下配置项：

- **SLIDE_THRESHOLD**：屏幕顶部的滑动区域高度（像素）。
- **SLIDE_DISTANCE**：滑动的最小距离（像素）。
- **AUTO_START**：是否在开机时自动启动程序。

## 常见问题解答

### 1. 程序启动时提示未找到`icon.png`文件

- **原因**：程序无法找到`icon.png`文件。
- **解决方法**：确保`icon.png`文件与程序在同一目录下，或者重新安装程序。

### 2. 滑动关机功能无法触发

- **原因**：滑动区域或滑动距离设置不正确。
- **解决方法**：检查并调整滑动区域和滑动距离的设置，确保滑动操作符合设置要求。

### 3. 程序无法开机自启

- **原因**：开机自启功能未正确配置。
- **解决方法**：确保在程序中启用了开机自启功能，并检查注册表中的开机自启项是否正确。

## 版本历史

- **1.0.0**：初始版本，提供基本的滑动关机功能。
- **1.1.0**：添加开机自启功能和托盘图标支持。
- **1.2.0**：优化用户界面和滑动关机算法。
- **1.2.1**：优化开机自启。
