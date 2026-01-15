from __future__ import annotations

import json
import os
from typing import Any

from flask import Flask, redirect, render_template, request, send_from_directory, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, 'public', 'data', 'questions.jsonl')
PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'public')

app = Flask(__name__)
app.secret_key = 'memory-garden-local'


def load_entries() -> list[dict[str, Any]]:
  entries: list[dict[str, Any]] = []
  if not os.path.exists(DATA_PATH):
    return entries
  with open(DATA_PATH, 'r', encoding='utf-8') as file:
    for line in file:
      line = line.strip()
      if not line:
        continue
      try:
        entries.append(json.loads(line))
      except json.JSONDecodeError:
        continue
  return entries


def save_entries(entries: list[dict[str, Any]]) -> None:
  os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
  with open(DATA_PATH, 'w', encoding='utf-8') as file:
    for entry in entries:
      file.write(json.dumps(entry, ensure_ascii=False))
      file.write('\n')


def validate_entry(entry: dict[str, Any]) -> list[str]:
  errors: list[str] = []
  if not entry.get('image'):
    errors.append('图片路径不能为空。')
  questions = entry.get('questions')
  if not isinstance(questions, list) or not questions:
    errors.append('至少需要一条题目。')
    return errors
  for idx, question in enumerate(questions, start=1):
    if not isinstance(question, dict):
      errors.append(f'第 {idx} 题格式不正确。')
      continue
    if not question.get('text'):
      errors.append(f'第 {idx} 题缺少题目文本。')
    options = question.get('options')
    if not isinstance(options, list) or len(options) < 2:
      errors.append(f'第 {idx} 题选项至少 2 个。')
    answer = question.get('answer')
    if not isinstance(answer, int):
      errors.append(f'第 {idx} 题答案必须是数字索引。')
    elif isinstance(options, list) and (answer < 0 or answer >= len(options)):
      errors.append(f'第 {idx} 题答案索引超出范围。')
    difficulty = question.get('difficulty')
    if not isinstance(difficulty, (int, float)):
      errors.append(f'第 {idx} 题难度必须是数字。')
  return errors


def build_image_url(image_path: str) -> str:
  cleaned = image_path.lstrip('/')
  return url_for('public_file', filename=cleaned)


@app.route('/public/<path:filename>')
def public_file(filename: str):
  return send_from_directory(PUBLIC_DIR, filename)


@app.route('/')
def index():
  entries = load_entries()
  summaries = []
  for idx, entry in enumerate(entries):
    summaries.append({
      'index': idx,
      'image': entry.get('image', ''),
      'description': entry.get('description', ''),
      'question_count': len(entry.get('questions', [])),
      'image_url': build_image_url(entry.get('image', '')) if entry.get('image') else '',
    })
  return render_template('index.html', entries=summaries)


@app.route('/new', methods=['POST'])
def create_entry():
  entries = load_entries()
  entries.append({'image': '', 'description': '', 'questions': []})
  save_entries(entries)
  return redirect(url_for('edit_entry', index=len(entries) - 1))


@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_entry(index: int):
  entries = load_entries()
  if index < 0 or index >= len(entries):
    return redirect(url_for('index'))

  entry = entries[index]
  message = ''
  errors: list[str] = []

  if request.method == 'POST':
    image = request.form.get('image', '').strip()
    description = request.form.get('description', '').strip()
    questions_raw = request.form.get('questions', '').strip()
    try:
      questions = json.loads(questions_raw) if questions_raw else []
    except json.JSONDecodeError:
      questions = []
      errors.append('题目 JSON 解析失败，请检查格式。')

    updated = {'image': image, 'description': description, 'questions': questions}
    errors.extend(validate_entry(updated))

    if not errors:
      entries[index] = updated
      save_entries(entries)
      entry = updated
      message = '已保存并更新题库文件。'

  questions_pretty = json.dumps(entry.get('questions', []), ensure_ascii=False, indent=2)

  return render_template(
    'edit.html',
    entry=entry,
    index=index,
    image_url=build_image_url(entry.get('image', '')) if entry.get('image') else '',
    questions=questions_pretty,
    message=message,
    errors=errors,
  )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5222)
