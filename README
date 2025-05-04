# Sword-Shield 项目 README

## 概述

Sword-Shield 是一个全面的 Web 安全分析工具，通过两种互补的检测方法帮助识别潜在的恶意网站：

*   **Sword**：一个关键字检测系统，使用 trie 数据结构识别网页内容中潜在的敏感或恶意词语。 
*   **Shield**：一个基于 BERT 的机器学习模型，根据网页的 HTML 标签结构将其分类为“恶意”或“正常”。

该系统使用 **Spider** 组件爬取网页进行分析，并将结果输出为 Excel 格式。

## 安装

### 先决条件

*   Python 3.9+
*   pip (Python 包管理器)

### 依赖项

```bash
# 安装所需包
pip install torch transformers sklearn beautifulsoup4 pyppeteer xlwt flask asyncio tqdm
```

### 所需文件

1.  下载预训练的 BERT 模型并将其放置在 `bert_model/` 目录中。该模型应包含三个文件：
    *   `vocab.txt`
    *   `pytorch_model.bin`
    *   `config.json`
2.  安装 Chrome 浏览器（Spider 组件需要）：
    *   对于 Windows，将 Chrome 放置在 `./bin/chrome-win32/chrome.exe`
    *   对于 Linux，请在 `spider/spider.py` 中调整路径以使用 `./bin/chrome-linux/chrome`
3.  为 Sword 组件准备关键字列表，或使用 `data/` 目录中现有的关键字数据。

## 项目结构

```
Sword-Shield/
├── .git/                  # Git 仓库元数据 (通常隐藏)
├── .gitignore             # Git 忽略文件配置
├── .venv/                 # Python 虚拟环境 (通常不提交)
├── 1746346711.xls         # 示例输出文件
├── api.py                 # 使用 Sword-Shield 功能的 API
├── best_bert_model.pth    # 训练好的 Shield 模型权重
├── commander.py           # 运行分析的命令行工具
├── Dockerfile             # Docker 配置文件
├── README                 # 本文档
├── requirements.txt       # Python 依赖列表
├── toTable.py             # 将结果转换为 Excel 格式
├── train.ipynb            # 用于训练 Shield 模型的 Jupyter Notebook
├── url_list.txt           # 待分析的 URL 列表
├── 输出记录               # (可能是输出目录)
├── __pycache__/           # Python 编译缓存 (通常不提交)
├── bert_model/            # 预训练 BERT 模型文件
│   ├── config.json
│   ├── pytorch_model.bin
│   └── vocab.txt
├── config/                # 配置设置
│   ├── __init__.py
│   ├── config.py
│   └── __pycache__/
├── Data/                  # 训练数据和关键字
│   ├── keyword_tree.pickle # 序列化的关键字树
│   ├── keyword.txt         # 原始关键字列表
│   ├── tags_data.txt       # 标签数据 (可能用于训练)
│   └── test_data.txt       # 测试/训练数据
├── shield/                # 基于 BERT 的网页分类模块
│   ├── shield.py
│   └── __pycache__/
├── spider/                # 用于获取页面的网络爬虫模块
│   ├── spider.py
│   └── __pycache__/
├── sword/                 # 关键字检测系统模块
│   ├── sword.py
│   └── __pycache__/
└── test_server/           # 包含示例页面的测试服务器
    ├── web.py
    └── templates/
        ├── 0.html         # 示例恶意页面
        └── 1.html         # 示例正常页面
```

## 使用方法

### 基本用法

1.  创建一个文本文件 (`url_list.txt`)，其中包含您要分析的 URL，每行一个：
2.  运行 commander 脚本：

    ```bash
    python commander.py
    # 或者使用自定义 URL 列表：
    python commander.py path/to/your/url_list.txt
    ```
3.  该脚本将：
    *   爬取指定的网站 
    *   使用 Sword 和 Shield 进行分析 
    *   将结果保存到 Excel 文件 

### 使用单个组件

#### Sword 组件

Sword 组件检测文本中的敏感关键字：

```python
from api import sword

# 分析一段文本以查找敏感关键字
results = sword("<要分析的文本>")
print(results)  # 检测到的关键字列表
```

#### Shield 组件

Shield 组件对网页进行分类：

```python
from api import shield

# 对 HTML 内容进行分类
result = shield("<HTML 内容>")
print(result)  # "恶意网页" 或 "正常网页"
```

#### Spider 组件

```python
from spider.spider import spider

# 爬取 URL 列表
urls = ["https://example.com", "https://example.org"]
responses = spider(urls)

# responses 将是一个字典，其中 URL 为键，HTML 内容为值
```

### 训练 Shield 模型

要使用您自己的数据训练或重新训练 Shield 模型：

1.  在 `data/test_data.txt` 中准备训练数据集，格式如下： `train.ipynb:67-88`

    ```
    <html 标签> 	 <标签>
    ```

    其中 `<标签>` 对于恶意网站为 0，对于正常网站为 1。

2.  打开并运行 `train.ipynb` notebook：

    ```bash
    jupyter notebook train.ipynb
    ```

3.  训练好的模型将保存为 `best_bert_model.pth` `train.ipynb:199-201`

### 创建自定义关键字列表

要为 Sword 组件创建自定义关键字列表：

1.  创建一个文本文件，每行包含一个关键字。
2.  使用 `create_sword_by` 函数：

    ```python
    from sword.sword import create_sword_by

    # 从文件创建关键字树
    create_sword_by("path/to/keywords.txt")
    ```

## 测试

包含一个测试服务器以验证系统功能：

1.  运行测试服务器：

    ```bash
    cd test_server
    python web.py
    ```

2.  服务器在以下地址提供测试页面：
    *   `http://localhost:5000/0` (示例恶意页面)
    *   `http://localhost:5000/1` (示例正常页面)
3.  通过将这些 URL 添加到您的 `url_list.txt` 并运行 commander 脚本来测试 Sword-Shield 系统。

## 输出格式

结果以 Excel 格式保存，包含以下列：

*   目标 URL
*   是否包含恶意代码 (Shield 结果)
*   敏感关键字检测结果 (Sword 结果)

## 注意事项

*   Shield 组件使用 BERT 进行分类，这需要足够的计算资源。
*   确保正确安装 Chrome 浏览器，以便 Spider 组件正常运行。
*   关键字检测的性能取决于关键字列表的质量。
*   默认模型将页面分为两类：恶意网页和正常网页。