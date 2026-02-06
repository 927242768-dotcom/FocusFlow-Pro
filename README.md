# 🍅 FocusFlow Pro (专注流)

FocusFlow Pro 是一款基于 Python 和 CustomTkinter 开发的现代化桌面番茄钟任务管理软件。它结合了任务清单、番茄工作法计时器和数据复盘功能，旨在帮助用户在快节奏的工作中保持专注。

![软件截图](https://github.com/927242768-dotcom/FocusFlow-Pro/blob/main/assets/Screenshot%202026-02-06%20140057.png?raw=true)

---

## 🚀 下载即用 (推荐)

如果你不想研究代码，只想下载软件直接使用，请点击下方链接下载最新的 **.exe** 安装包：

👉 **[点击这里下载 FocusFlow Pro 最新版 (Releases)](https://github.com/927242768-dotcom/FocusFlow-Pro/releases)**

**使用说明：**
1. 进入页面后，找到最新的版本（例如 v1.0）。
2. 在 "Assets" 下方找到 `FocusFlowPro.exe` 并点击下载。
3. 下载后直接双击即可运行，无需安装 Python。

---

## ✨ 主要功能

* **✅ 任务管理**：轻松创建、删除任务，设置预计完成时间。
* **🍅 沉浸式番茄钟**：25分钟专注倒计时，支持暂停/继续，伴随提示音。
* **🌈 动态交互界面**：
    * 空闲状态下展示动态彩虹文字：“左侧添加你的任务，开始每天的进步吧”。
    * 支持长文本自动换行，右键菜单快速修改或删除任务。
* **📊 数据归档与复盘**：
    * 任务完成后弹出评分滑块和备注框。
    * 历史记录查看器：保存最近50条完成记录，支持查看评分和复盘心得。
* **💾 数据持久化**：
    * 自动记忆数据保存位置（首次运行询问）。
    * JSON 格式本地存储，保护隐私。

---

## 🛠️ 开发者指南 (源码运行)

如果你懂 Python，想查看源码或在本地修改运行，请按照以下步骤操作：

### 1. 克隆仓库
打开终端或命令行，运行以下命令：
```bash
git clone [https://github.com/927242768-dotcom/FocusFlow-Pro.git](https://github.com/927242768-dotcom/FocusFlow-Pro.git)
cd FocusFlow-Pro

2. 安装依赖
请确保你的电脑已安装 Python 3.8 或以上版本。

Bash
pip install -r requirements.txt
3. 运行软件
Bash
python main.py
📦 如何打包成 EXE
如果你修改了代码，想自己生成 Windows 可执行文件，可以使用 PyInstaller：

Bash
pyinstaller --noconfirm --onefile --windowed --name "FocusFlowPro" --add-data "assets;assets" main.py
打包完成后，FocusFlowPro.exe 文件将位于生成的 dist 文件夹中。

🤝 贡献
欢迎提交 Issue 或 Pull Request 来改进这个项目！

📄 开源协议
本项目采用 MIT License 开源协议。
