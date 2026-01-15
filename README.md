# 记忆小花园

一个本地运行的儿童注意力与记忆力训练小游戏。游戏流程为“观察图片 + 随机选择题”，每局共 5 轮。

## 开发与构建

```bash
bun install
bun dev
bun run build
```

## 题库与图片

- 题库文件：`public/data/questions.jsonl`
- 图片目录：`public/images/`
- 题库中的 `image` 字段填写 `/images/xxx.png` 这样的相对路径。

## 题库维护工具

本地维护工具位于 `tools/bank_manager/`：

```bash
python tools/bank_manager/app.py
```

打开 `http://127.0.0.1:5000` 即可。

功能说明：
- 自动扫描 `public/images`，没有条目的图片会自动生成空条目。
- 表单填写题目，不需要手动编辑 JSON。
- 正确答案填写选项文字，保存时自动转换为索引。
