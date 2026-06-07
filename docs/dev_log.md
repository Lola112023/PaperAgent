# PaperAgent 开发日志

## 项目简介

PaperAgent 是一个面向论文阅读与学术汇报的智能 Agent 原型系统。项目基于 Python、DeepSeek API、工具调用机制与 RAG 检索增强生成流程进行设计，目标是实现文档解析、语义检索、论文问答、方法分析、实验分析、学术 concern 生成和汇报材料整理等功能。
---

# Day 1：项目初始化与工程结构搭建

## 今日目标

完成 PaperAgent 项目的基础工程结构搭建，使项目具备清晰的目录划分、Git 版本管理和最小可运行入口。

## 完成内容

1. 在 VSCode 中创建 `PaperAgent` 项目。
2. 初始化 Git 仓库，并连接 GitHub 远程仓库。
3. 创建 Python 虚拟环境 `.venv`。
4. 创建 `.gitignore`，避免上传虚拟环境、`.env`、缓存文件、上传文档和输出报告。
5. 创建基础目录结构：

```text
PaperAgent/
├── main.py
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── agent/
├── tools/
├── rag/
├── data/
├── outputs/
├── logs/
└── tests/
````

6. 实现 `config.py`，统一管理项目路径、API Key、模型名称和 Agent 参数。
7. 实现 `agent/memory.py`，用于保存短期对话历史。
8. 实现 `agent/core.py` 的初始骨架。
9. 实现 `main.py` 命令行入口，支持用户输入与固定回复。
10. 完成第一次 Git commit 并推送到 GitHub。

## 关键理解

* `main.py` 是命令行入口，负责用户交互。
* `agent/core.py` 是 Agent 主逻辑入口。
* `config.py` 用于统一管理项目配置，避免在代码中写死路径和参数。
* `.env` 用于保存 API Key 等敏感信息，不能提交到 GitHub。
* `.gitignore` 用于控制哪些文件不参与版本管理。
* `ConversationMemory` 当前只是短期记忆，用 list 保存多轮对话。

## 遇到的问题与解决

1. PowerShell 中 `mkdir agent tools rag ...` 报错。
   原因是 PowerShell 的 `mkdir` 不支持像 Git Bash 一样一次性用空格创建多个目录。
   解决方式是使用逐个创建或 PowerShell 数组循环创建目录。

2. Git 提交时报 `Author identity unknown`。
   原因是 Git 没有配置用户名和邮箱。
   解决方式：

```powershell
git config --global user.name "Lola Chen"
git config --global user.email "自己的 GitHub 邮箱"
```

3. `git push` 时出现网络连接失败。
   原因是 Git 没有走代理。
   解决方式是配置 Git 代理：

```powershell
git config --global http.proxy http://127.0.0.1:22307
git config --global https.proxy http://127.0.0.1:22307
```

## 阶段成果

完成了一个可运行、可维护、可版本管理的 Python Agent 项目骨架。

---

# Day 2：接入 DeepSeek LLM 调用

## 今日目标

将 Day 1 的固定回复升级为真实调用大模型，实现基础多轮对话能力。

## 完成内容

1. 新增 `llm/` 目录：

```text
llm/
├── __init__.py
└── client.py
```

2. 安装 OpenAI Python SDK，用于兼容调用 DeepSeek API。
3. 修改 `.env`，配置：

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=自己的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
TEMPERATURE=0.3
MAX_OUTPUT_TOKENS=1200
MAX_AGENT_STEPS=5
```

4. 修改 `config.py`，增加 DeepSeek 相关配置。
5. 实现 `llm/client.py`，封装 LLM 调用逻辑。
6. 使用 OpenAI SDK 的兼容接口调用 DeepSeek。
7. 修改 `agent/core.py`，使 `PaperAgent` 能够调用真实 LLM。
8. 实现基础多轮对话。

## 关键理解

* OpenAI SDK 不一定只能调用 OpenAI，只要服务商兼容 OpenAI API 格式，就可以通过设置 `base_url` 调用其他模型服务。
* DeepSeek 需要设置：

```python
OpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_base_url,
)
```

* `messages` 是发送给大模型的对话上下文，包含：

```text
system：系统规则
user：用户输入
assistant：模型回复
```

* 当前系统仍然是 chatbot，本质流程是：

```text
用户输入
↓
保存到 memory
↓
调用 LLM
↓
输出回复
```

还没有自动工具调用能力。

## 遇到的问题与解决

1. 使用 DeepSeek API Key 调用 OpenAI 官方接口时出现 401 错误。
   原因是代码仍然请求 OpenAI 官方地址。
   解决方式是在 `LLMClient` 中增加 DeepSeek 的 `base_url`。

2. `responses.create(input=messages)` 出现 Pylance 类型警告。
   解决方式是改用兼容性更好的：

```python
self.client.chat.completions.create(
    model=self.model,
    messages=messages,
)
```

## 阶段成果

系统从固定回复升级为真实调用 DeepSeek 的多轮 chatbot。

---

# Day 3：工具注册机制设计

## 今日目标

建立统一的工具注册机制，为后续 Agent 自动调用工具打基础。

## 完成内容

1. 新增 `tools/base.py`，定义 `Tool` 数据结构。
2. 改造 `tools/registry.py`，建立工具注册表。
3. 注册基础工具：

   * `calculator`
   * `read_file`
4. 实现：

   * `list_tools()`
   * `get_tool()`
   * `run_tool()`
5. 在 `main.py` 中增加 `/tools` 命令，用于查看当前可用工具。

## 关键理解

* 工具注册机制的作用是统一管理工具，而不是让 Agent 直接调用具体函数。
* 理想调用方式是：

```python
run_tool("calculator", expression="1 + 2")
run_tool("read_file", file_path="data/example.md")
```

* `run_tool()` 的核心是：

```python
result = tool.function(**kwargs)
```

它可以把字典参数自动展开成函数参数。

## 遇到的问题与解决

运行时报错：

```text
ImportError: cannot import name 'Tool' from 'tools.base'
```

原因是 `tools/base.py` 中没有正确写入或保存 `Tool` 类。
解决方式是检查并补全：

```python
from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]
```

## 阶段成果

系统具备了工具注册表和统一工具调用接口，但工具仍然主要通过命令手动调用。

---

# Day 4：实现安全计算器工具

## 今日目标

将 `calculator` 从占位函数改造成真正可用的安全数学计算工具。

## 完成内容

1. 修改 `tools/calculator.py`。
2. 使用 `ast` 解析数学表达式，避免直接使用不安全的 `eval`。
3. 支持以下运算：

   * 加法 `+`
   * 减法 `-`
   * 乘法 `*`
   * 除法 `/`
   * 幂运算 `**`
   * 取余 `%`
   * 括号
   * 小数
4. 增加除零错误处理。
5. 在 `main.py` 中增加 `/calc` 命令。
6. 添加 calculator 相关测试用例。

## 关键理解

不能直接使用：

```python
eval(expression)
```

因为用户可能输入恶意代码，例如：

```python
__import__("os").system("dir")
```

使用 AST 的方式是：

```text
表达式字符串
↓
ast.parse 解析成语法树
↓
只允许数学节点
↓
递归计算
↓
返回结果
```

这样可以有效限制可执行内容。

## 阶段成果

可以通过命令行手动调用计算器：

```text
/calc 12 * (3 + 4)
```

输出：

```text
计算结果：84
```

---

# Day 5：实现安全文件读取工具

## 今日目标

实现 `read_file` 工具，使系统能够读取项目目录内的 `.txt` 和 `.md` 文件。

## 完成内容

1. 修改 `tools/file_reader.py`。
2. 支持读取：

   * `.txt`
   * `.md`
3. 限制只能读取项目目录内的文件。
4. 限制文件最大大小为 200KB。
5. 增加文件不存在、文件类型不支持、编码错误等异常处理。
6. 创建测试文件 `data/example.md`。
7. 在 `main.py` 中增加 `/read` 命令。
8. 添加文件读取测试用例。

## 关键理解

文件读取工具必须有安全边界，不能允许 Agent 任意读取系统文件。

主要限制包括：

```text
1. 只能读取项目目录内文件
2. 只支持指定类型
3. 限制文件大小
4. 处理编码错误
```

路径安全检查通过：

```python
path.relative_to(base_dir.resolve())
```

判断目标文件是否位于项目目录内。

## 阶段成果

可以通过命令行读取文档：

```text
/read data/example.md
```

系统可以输出文件内容。

---

# Day 6：实现最小 Agent Loop

## 今日目标

将系统从“Chatbot + 手动工具调用”升级为“可以自动选择工具的最小 Agent”。

## 完成内容

1. 修改 `agent/prompts.py`，要求模型输出固定 JSON 格式。
2. 定义两类模型输出：

   * `tool_call`
   * `final_answer`
3. 新增 `agent/parser.py`，用于解析 LLM 返回的 JSON。
4. 修改 `agent/core.py`，实现最小 Agent Loop。
5. Agent 可以自动判断是否需要调用：

   * `calculator`
   * `read_file`
6. 引入 `max_agent_steps`，防止工具调用死循环。
7. 增加 `scratchpad`，保存一次任务内部的工具调用过程。

## 关键理解

现在系统开始具备 Agent 特征。

新的流程是：

```text
用户输入
↓
LLM 判断是否需要工具
↓
如果需要，输出 tool_call JSON
↓
系统调用工具
↓
将工具结果返回给 LLM
↓
LLM 输出 final_answer
```

`while True` 是外层用户交互循环，表示用户可以不断提问。
`max_agent_steps` 是内层 Agent 执行步数限制，表示每一次用户请求中 Agent 最多可以思考和调用工具多少轮。

## 阶段成果

用户可以直接输入：

```text
请帮我计算 12 * (3 + 4)
```

Agent 自动调用 calculator，并返回最终答案。

---

# Day 7：补全命令、历史记录与日志

## 今日目标

增强命令行交互能力，并加入日志记录，使项目更可维护。

## 完成内容

1. 在 `main.py` 中增加：

   * `/help`
   * `/tools`
   * `/history`
   * `/clear`
   * `/calc`
   * `/read`
2. 在 `PaperAgent` 中增加：

   * `clear_memory()`
   * `get_history()`
3. 新建 `utils/logger.py`。
4. 实现按日期保存日志文件。
5. 在 Agent 运行过程中记录：

   * 用户输入
   * 工具调用
   * 工具结果
   * 最终回答

## 关键理解

* `main.py` 负责命令行交互，不应该堆积过多核心业务逻辑。
* `PaperAgent` 负责对话、记忆和工具调用。
* 日志可以帮助调试 Agent 行为，尤其是后续工具调用和 RAG 检索过程。

## 阶段成果

系统具备较完整的 CLI 交互体验，并可以查看历史、清空记忆和记录运行日志。

---

# Day 8：实现文档加载器

## 今日目标

实现 PDF / TXT / Markdown 文档加载功能，为 RAG 做准备。

## 完成内容

1. 安装 `PyMuPDF`。
2. 修改 `rag/loader.py`。
3. 定义 `DocumentChunk` 数据结构，保存：

   * 文本内容
   * 来源文件
   * 页码
4. 支持加载：

   * `.pdf`
   * `.txt`
   * `.md`
5. PDF 按页读取文本。
6. TXT / Markdown 作为整体读取。
7. 新增 `tools/document_loader.py`。
8. 在工具注册表中增加 `load_document`。
9. 在 `main.py` 中增加 `/load` 命令。

## 关键理解

文档加载是 RAG 的第一步：

```text
PDF / TXT / Markdown
↓
提取文本
↓
保留来源和页码
↓
后续用于切分和检索
```

PDF 页码从用户角度应从 1 开始，而 PyMuPDF 内部索引从 0 开始，因此保存时使用：

```python
page=page_index + 1
```

## 遇到的问题与解决

Pylance 对：

```python
for page_index, page in enumerate(pdf, start=1):
```

报类型警告，认为 `fitz.Document` 不可迭代。
解决方式是改为：

```python
for page_index in range(pdf.page_count):
    page = pdf.load_page(page_index)
```

## 阶段成果

系统可以加载并预览 PDF / Markdown / TXT 文档。

---

# Day 9：实现文本切分 Chunker

## 今日目标

将加载后的长文档切分成适合检索和输入大模型的小文本块。

## 完成内容

1. 修改 `rag/chunker.py`。
2. 定义 `TextChunk` 数据结构，保存：

   * chunk 文本
   * 来源文件
   * 页码
   * chunk_id
3. 实现 `split_text()`，用于切分单段文本。
4. 实现 `split_documents()`，用于切分多个 `DocumentChunk`。
5. 支持设置：

   * `chunk_size`
   * `overlap`
6. 新增 `tools/chunk_tool.py`。
7. 注册 `chunk_document` 工具。
8. 在 `main.py` 中增加 `/chunk` 命令。
9. 添加文本切分测试用例。

## 关键理解

长文档不能直接全部输入给大模型，因此需要 chunk 切分。

切分方式：

```text
chunk 1: 0   - 800
chunk 2: 700 - 1500
chunk 3: 1400 - 2000
```

其中 overlap 的作用是保留上下文连续性，避免关键句子在切分边界处断裂。

## 阶段成果

系统可以将文档切分为多个带有来源和页码信息的 chunk。

---

# Day 10：实现 Embedding 模块

## 今日目标

将文本 chunk 转换为向量，为语义检索做准备。

## 完成内容

1. 安装：

   * `sentence-transformers`
   * `numpy`
2. 修改 `.env`，增加：

```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

3. 修改 `config.py`，增加 embedding 模型配置。
4. 修改 `rag/embedder.py`。
5. 实现：

   * `get_embedding_model()`
   * `embed_texts()`
   * `embed_query()`
6. 使用 `lru_cache` 避免重复加载 embedding 模型。
7. 使用 `normalize_embeddings=True` 对向量归一化。
8. 新增 `tools/embedding_tool.py`。
9. 注册 `embedding_preview` 工具。
10. 在 `main.py` 中增加 `/embed` 命令。

## 关键理解

Embedding 的作用是将文本转换为向量，使计算机能够通过向量相似度衡量语义相关性。

语义检索的基础流程是：

```text
文本 chunk
↓
embedding 向量
↓
用户 query 也转成向量
↓
计算相似度
↓
返回最相关 chunk
```

选择本地 `sentence-transformers` 的原因：

```text
1. 不依赖额外 embedding API
2. 支持中英文
3. 适合原型系统
4. 与 DeepSeek Chat 模型解耦
```

## 阶段成果

系统可以为文档 chunk 生成 embedding 矩阵。

---

# Day 11：实现本地向量库与语义检索

## 今日目标

实现本地向量存储和语义检索，使系统能够根据用户问题找到相关文档片段。

## 完成内容

1. 修改 `config.py`，增加：

```python
storage_dir
vector_store_dir
```

2. 修改 `.gitignore`，忽略本地向量库生成文件。
3. 新建 `rag/vector_store.py`。
4. 实现 `VectorStore`：

   * 保存 `chunks.json`
   * 保存 `embeddings.npy`
   * 加载 chunks 和 embeddings
   * 判断向量库是否存在
5. 修改 `rag/retriever.py`。
6. 定义 `RetrievedChunk` 数据结构。
7. 实现 `retrieve()`，根据 query 检索最相关 chunk。
8. 使用向量点积计算相似度。
9. 新建 `tools/index_tool.py`，实现 `build_index()`。
10. 新建 `tools/search_tool.py`，实现 `search_index()`。
11. 注册：

* `build_index`
* `search_index`

12. 在 `main.py` 中增加：

* `/index`
* `/search`

13. 添加索引构建和检索测试用例。

## 关键理解

Day 11 完成了 RAG 的底层闭环：

```text
文档
↓
加载
↓
切分
↓
向量化
↓
保存到本地向量库
↓
用户 query 向量化
↓
相似度计算
↓
返回相关 chunk
```

本地向量库由两个文件组成：

```text
storage/vector_store/
├── chunks.json
└── embeddings.npy
```

其中：

* `chunks.json` 保存文本和元数据；
* `embeddings.npy` 保存对应向量矩阵。

由于 embedding 已经归一化，因此可以使用：

```python
scores = embeddings @ query_embedding
```

计算相似度。

## 阶段成果

系统可以通过：

```text
/index data/example.md
```

建立索引，并通过：

```text
/search PaperAgent 支持什么功能？
```

检索相关文本片段。

---

# Day 1—Day 11 阶段总结

## 已完成功能

截至 Day 11，PaperAgent 已完成以下能力：

1. 项目工程结构搭建
2. Git / GitHub 版本管理
3. `.env` 配置管理
4. DeepSeek API 接入
5. LLM 调用封装
6. 多轮对话短期记忆
7. 工具注册机制
8. 统一工具调用接口
9. 安全计算器工具
10. 安全文件读取工具
11. 最小 Agent Loop
12. 自动工具调用
13. CLI 命令系统
14. 对话历史查看与清空
15. 日志记录
16. PDF / TXT / Markdown 文档加载
17. 文本 chunk 切分
18. 本地 embedding 生成
19. 本地向量库保存与加载
20. 基于向量相似度的语义检索

## 当前系统架构

```text
User
 ↓
main.py
 ↓
PaperAgent
 ↓
LLMClient
 ↓
DeepSeek

PaperAgent
 ↓
Tool Registry
 ↓
calculator / read_file / load_document / chunk_document / build_index / search_index

RAG Pipeline:
Document Loader
 ↓
Chunker
 ↓
Embedder
 ↓
VectorStore
 ↓
Retriever
```

## 当前系统状态

目前 PaperAgent 已经从最初的 chatbot 发展为一个具备基础工具调用和 RAG 底层能力的 Agent 原型。

当前仍然存在的问题是：

1. RAG 检索还主要通过 `/index` 和 `/search` 手动触发。
2. Agent 尚未完全自动完成“检索文档—阅读证据—生成答案”的 RAG 问答流程。
3. 论文总结、方法分析、实验分析和 concern 生成等高层任务模块还没有完全实现。
4. 目前向量库只支持单一索引文件，后续需要支持多文档管理。
5. 还没有 Streamlit 前端和报告导出功能。

## 后续计划

下一阶段计划推进：

1. 将 `search_index` 接入 Agent Loop，使 Agent 能自动检索文档。
2. 实现基于检索结果的 RAG 问答。
3. 实现论文总结模块。
4. 实现方法分析模块。
5. 实现实验分析模块。
6. 实现学术 concern 生成模块。
7. 实现 Markdown 报告导出。
8. 后续开发 Streamlit 前端，提升交互体验。
# Day 12：将 RAG 检索工具接入 Agent Loop

## 今日目标

使 Agent 能够在用户提出文档相关问题时自动调用 `search_index` 工具，而不是只能通过 `/search` 手动检索。

## 完成内容

1. 修改 `SYSTEM_PROMPT`，新增 `search_index` 工具说明。
2. 明确要求当用户问题涉及“当前文档、这篇论文、方法、实验、数据集、baseline”等内容时优先调用检索工具。
3. 优化 `search_index` 返回格式，使其包含来源、页码、chunk_id、相似度和内容。
4. 修改工具结果反馈 prompt，使 Agent 能基于工具结果继续判断或输出最终答案。

## 阶段成果

Agent 可以在自然语言提问中自动调用本地向量检索工具，初步具备 RAG Agent 能力。

---

# Day 13：优化 RAG 问答格式

## 今日目标

使 Agent 基于检索结果生成更规范的回答，避免只复述检索片段。

## 完成内容

1. 增加 RAG 回答格式要求。
2. 要求回答包含“结论、依据、补充说明”。
3. 要求基于页码、chunk_id 和来源说明证据。
4. 增加 `/ask` 命令，显式通过 Agent 提问。
5. 在 Agent 中记录工具调用轨迹，便于调试。

## 阶段成果

系统可以基于检索结果生成结构化回答，并能说明信息来源和不确定性。

---

# Day 14：完善 RAG Demo 与索引状态检查

## 今日目标

完善 RAG 使用流程，使系统更适合作为阶段性 demo 展示。

## 完成内容

1. 新增 `index_status()` 工具。
2. 在工具注册表中注册 `index_status`。
3. 在 CLI 中增加 `/index_status` 命令。
4. 优化未建立索引时的错误提示。
5. 在 README 中补充 RAG Demo 使用流程。
6. 说明当前系统限制：单索引覆盖、多文档管理尚未实现等。

## 阶段成果

系统具备较完整的 RAG Demo 流程：建立索引、查看索引状态、手动检索、Agent 自动问答。

# Day 15：优化了chunk的部分逻辑

原先的切分逻辑在面对有checklist的文章的时候会导致检索质量下降。所以我

1. 虽然依旧是按照字数来切分，但是切分的时候标注了metadata，也就是章节名，页码等。实现尽可能丰富的上下文信息保存。
2. 后面优化的时候，按照章节优先，字数次优先的逻辑进行chunk。准确率有所提升。

继续努力。



