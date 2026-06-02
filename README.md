# PaperAgent

PaperAgent 是一个面向论文阅读与学术汇报的智能分析 Agent。

## 项目目标

本项目计划实现一个可以处理 PDF / Markdown / TXT 文档的智能体系统，支持：

1. 文档解析
2. 文档检索
3. 论文总结
4. 方法分析
5. 实验分析
6. Concern 生成
7. PPT 大纲生成
8. Markdown 报告导出

## 技术栈

- Python
- VSCode
- Git / GitHub
- Streamlit
- PyMuPDF
- Chroma / FAISS
- LLM API
- RAG
- Agent Loop

## 当前进度

见docs\dev_log.md

## 运行方式

```bash
python main.py
```
## RAG Demo 使用流程

### 1. 启动项目

```bash
python main.py
```

### 2. 查看帮助

```text
/help
```

### 3. 建立文档索引

```text
/index data/example.md
```

或者对 PDF 建立索引：

```text
/index data/uploaded/test.pdf
```

### 4. 查看索引状态

```text
/index_status
```

### 5. 手动检索

```text
/search PaperAgent 支持哪些功能？
```

### 6. 使用 Agent 自然问答

```text
/ask PaperAgent 当前实现了哪些模块？
```

或者直接输入：

```text
这篇论文的主要方法是什么？
```

系统会尝试自动调用检索工具，并基于检索结果生成回答。

### 当前限制

- 当前本地向量库默认只保存一份索引；
- 如果重新执行 `/index`，会覆盖之前的索引；
- 当前 RAG 问答依赖本地 embedding 模型；
- 若未先建立索引，文档问答无法正常进行。

