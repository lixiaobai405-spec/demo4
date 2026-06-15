# 领导力建模智能体

基于 AI 的领导力模型构建工具，通过 5 步向导式流程，帮助企业快速构建贴合实际的管理者领导力模型。

## 功能流程

| 步骤 | 名称 | 说明 |
|------|------|------|
| 1 | 信息采集 | AI 引导对话收集企业背景，支持上传参考文档解析 |
| 2 | 维度确认 | AI 生成领导力维度框架，可增删改确认 |
| 3 | 描述建立 | 为每个维度生成定位描述，含质检提示 |
| 4 | 行为锚定 | BARS 三档行为描述（优秀/达标/不达标） |
| 5 | 总览导出 | 查看完整模型，导出 Markdown |

## 技术栈

- **后端**: Python Flask + DeepSeek API (OpenAI-compatible)
- **前端**: 原生 HTML/CSS/JS，零框架，多页架构
- **AI**: DeepSeek Chat / Reasoner

## 快速启动

### 环境要求

- Python 3.10+
- DeepSeek API Key

### 1. 配置 API Key

编辑 `mykey.py` 文件（已存在），填入 DeepSeek API Key：

```python
DEEPSEEK_API_KEY = "sk-your-key-here"
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动后端

在项目根目录（`demo4/`）下运行：

```bash
python -m backend.app
```

或直接：

```bash
python backend/app.py
```

服务启动在 `http://localhost:8000`。

### 4. 打开浏览器

访问 `http://localhost:8000` 即可使用。

## API 端点

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/chat` | AI 引导对话 |
| POST | `/api/analyze-doc` | 文档分析（上传文件） |
| POST | `/api/generate-dimensions` | 生成领导力维度 |
| POST | `/api/generate-descriptions` | 生成维度描述 |
| POST | `/api/generate-anchors` | 生成行为锚定 |
| POST | `/api/regenerate` | 重新生成单条内容 |

## 项目结构

```
demo4/
├── mykey.py                  # API Key 配置（不入 git）
├── backend/
│   ├── app.py                # Flask 主入口
│   ├── config.py             # 配置读取
│   ├── ai_service.py         # DeepSeek API 封装
│   └── requirements.txt
├── frontend/
│   ├── index.html            # 首页
│   ├── step1.html            # 信息采集
│   ├── step2.html            # 维度确认
│   ├── step3.html            # 描述建立
│   ├── step4.html            # 行为锚定
│   ├── step5.html            # 总览导出
│   └── style.css             # 共享样式
└── 页面参考/                  # 原始参考页面
```

## 注意事项

- `mykey.py` 已加入 `.gitignore`，不会被提交到仓库
- 前端状态通过 `localStorage` 在步骤间传递
- 如 AI 调用失败，系统会自动降级使用模拟数据
- Markdown 导出在 step5 页面可用
