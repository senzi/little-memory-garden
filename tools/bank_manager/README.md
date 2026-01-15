# 题库维护工具

本工具用于本地维护 `public/data/questions.jsonl`，帮助预览图片、编辑题目并校验数据。

## 启动方式

在项目根目录执行：

```bash
python tools/bank_manager/app.py
```

打开浏览器访问 `http://127.0.0.1:5000`。

## 题目 JSON 格式示例

```json
[
  {
    "text": "图片里有几只气球？",
    "options": ["2只", "3只", "4只"],
    "answer": 1,
    "difficulty": 2
  }
]
```

- `answer` 为选项索引，从 0 开始。
- `difficulty` 为题目难度分值（数字）。
- 图片路径需放在 `public` 目录下，例如 `/images/xxx.png`。
