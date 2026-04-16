#!/usr/bin/env node

/**
 * Todo List 管理脚本
 * 支持增删改查、进度更新、数据持久化到 Markdown
 * 
 * 使用方法:
 *   node scripts/todo.js add "2026-02-21T14:00:00Z" "事项内容" [进度]
 *   node scripts/todo.js list
 *   node scripts/todo.js update "001" "已完成"
 *   node scripts/todo.js delete "001"
 *   node scripts/todo.js done "关键词"
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'temp');
const TODO_FILE = path.join(DATA_DIR, 'todo-list.md');

/** 表格列内存储时把 | 换成全角 ｜，避免破坏列解析 */
function escapePipe(s) {
  return String(s ?? '').replace(/\|/g, '｜');
}
function unescapePipe(s) {
  return String(s ?? '').replace(/｜/g, '|');
}

/**
 * 生成唯一 ID
 */
function generateId(existingItems) {
  if (existingItems.length === 0) return '001';
  const maxId = existingItems.reduce((max, item) => {
    const num = parseInt(item.id, 10);
    return num > max ? num : max;
  }, 0);
  return String(maxId + 1).padStart(3, '0');
}

/**
 * 读取待办事项
 */
function readTodos() {
  if (!fs.existsSync(TODO_FILE)) {
    return [];
  }
  
  const content = fs.readFileSync(TODO_FILE, 'utf-8');
  const items = [];
  
  // 解析 Markdown 表格
  const lines = content.split('\n');
  let isInTable = false;
  
  for (const line of lines) {
    if (line.startsWith('| ID |')) {
      isInTable = true;
      continue;
    }
    
    if (isInTable && line.startsWith('|')) {
      const parts = line.split('|').slice(1, -1).map(p => p.trim());
      // Skip header separator and empty/invalid rows
      if (parts.length >= 4 && parts[0] && parts[0] !== '----' && !parts[1].includes('ISO')) {
        items.push({
          id: parts[0],
          standardTime: parts[1],
          content: unescapePipe(parts[2]),
          progress: unescapePipe(parts[3]),
          timestamp: parts[4] || '',
        });
      }
    }
  }
  
  return items;
}

/**
 * 保存待办事项
 */
function saveTodos(items) {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
  let md = '## Todo List\n\n';
  md += '| ID | 标准时间 (ISO 8601) | 事项内容 | 进度 | 创建/更新时间戳 |\n';
  md += '|----|---------------------|----------|------|----------------|\n';
  
  for (const item of items) {
    md += `| ${item.id} | ${item.standardTime} | ${escapePipe(item.content)} | ${escapePipe(item.progress)} | ${item.timestamp} |\n`;
  }
  
  fs.writeFileSync(TODO_FILE, md, 'utf-8');
  console.log(`[SAVED] ${TODO_FILE}`);
}

/**
 * 查找待办事项
 */
function findTodos(items, query) {
  // 先按标准时间匹配
  if (query.match(/^\d{4}-\d{2}-\d{2}T/)) {
    const exact = items.filter(i => i.standardTime === query);
    if (exact.length > 0) return exact;
  }
  
  // 按 ID 匹配
  const byId = items.filter(i => i.id === query);
  if (byId.length > 0) return byId;
  
  // 按关键词模糊匹配
  const lowerQuery = query.toLowerCase();
  const byKeyword = items.filter(i => 
    i.content.toLowerCase().includes(lowerQuery) ||
    i.progress.toLowerCase().includes(lowerQuery)
  );
  
  return byKeyword;
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const useJson = args.includes('--json');
  const command = (args[0] === '--json' ? 'list' : (args[0] || 'list'));
  
  console.log(`[TIMESTAMP] ${Date.now()}`);
  console.log(`[COMMAND] ${command}${useJson ? ' --json' : ''}`);
  
  const items = readTodos();
  
  if (command === 'list') {
    if (useJson) {
      console.log(`[RESULT]`);
      console.log(JSON.stringify({ count: items.length, items }));
    } else {
      console.log(`[RESULT]`);
      console.log(`count: ${items.length}`);
      console.log(`items:`);
      if (items.length === 0) {
        console.log(`  (空)`);
      } else {
        for (const item of items) {
          console.log(`  - ${item.id}: ${item.content} [${item.progress}] @ ${item.standardTime}`);
        }
      }
    }
  } else if (command === 'add') {
    // 添加待办
    const time = args[1];
    const content = args[2] || '';
    const progress = args[3] || '待办';
    
    if (!time || !content) {
      console.log(`[ERROR] 用法: node scripts/todo.js add "ISO时间" "事项内容" [进度]`);
      process.exit(1);
    }
    
    // 验证时间格式
    const timeRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$/;
    if (!timeRegex.test(time)) {
      console.log(`[ERROR] 时间格式必须是 ISO 8601: ${time}`);
      process.exit(1);
    }
    
    const newItem = {
      id: generateId(items),
      standardTime: time,
      content,
      progress,
      timestamp: String(Date.now()),
    };
    
    items.push(newItem);
    saveTodos(items);
    
    console.log(`[RESULT]`);
    console.log(`added: ${newItem.id}`);
    console.log(`item: ${newItem.content}`);
  } else if (command === 'update') {
    // 更新进度
    const query = args[1];
    const newProgress = args.slice(2).join(' ');
    
    if (!query || !newProgress) {
      console.log(`[ERROR] 用法: node scripts/todo.js update "ID或关键词" "新进度"`);
      process.exit(1);
    }
    
    const matched = findTodos(items, query);
    
    if (matched.length === 0) {
      console.log(`[ERROR] 未找到匹配的待办事项: ${query}`);
      process.exit(1);
    }
    
    if (matched.length > 1) {
      console.log(`[ERROR] 匹配到多个待办事项，请提供更精确的 ID 或关键词:`);
      for (const m of matched) {
        console.log(`  - ${m.id}: ${m.content} [${m.progress}]`);
      }
      process.exit(1);
    }
    
    const item = matched[0];
    item.progress = newProgress;
    item.timestamp = String(Date.now());
    saveTodos(items);
    
    console.log(`[RESULT]`);
    console.log(`updated: ${item.id}`);
    console.log(`new_progress: ${item.progress}`);
  } else if (command === 'done' || command === 'complete') {
    // 标记为完成
    const query = args[1];
    
    if (!query) {
      console.log(`[ERROR] 用法: node scripts/todo.js done "ID或关键词"`);
      process.exit(1);
    }
    
    const matched = findTodos(items, query);
    
    if (matched.length === 0) {
      console.log(`[ERROR] 未找到匹配的待办事项: ${query}`);
      process.exit(1);
    }
    
    const item = matched[0];
    item.progress = '已完成';
    item.timestamp = String(Date.now());
    saveTodos(items);
    
    console.log(`[RESULT]`);
    console.log(`completed: ${item.id}`);
    console.log(`item: ${item.content}`);
  } else if (command === 'delete' || command === 'remove') {
    // 删除待办
    const query = args[1];
    
    if (!query) {
      console.log(`[ERROR] 用法: node scripts/todo.js delete "ID或关键词"`);
      process.exit(1);
    }
    
    const matched = findTodos(items, query);
    
    if (matched.length === 0) {
      console.log(`[ERROR] 未找到匹配的待办事项: ${query}`);
      process.exit(1);
    }
    
    const index = items.findIndex(i => i.id === matched[0].id);
    const deleted = items.splice(index, 1)[0];
    saveTodos(items);
    
    console.log(`[RESULT]`);
    console.log(`deleted: ${deleted.id}`);
    console.log(`item: ${deleted.content}`);
  } else {
    console.log(`Usage:`);
    console.log(`  node scripts/todo.js list [--json]             # 列出待办，--json 输出 JSON`);
    console.log(`  node scripts/todo.js add "ISO时间" "内容"      # 添加待办`);
    console.log(`  node scripts/todo.js update "ID" "进度"        # 更新进度`);
    console.log(`  node scripts/todo.js done "ID或关键词"         # 标记完成`);
    console.log(`  node scripts/todo.js delete "ID或关键词"       # 删除待办`);
    process.exit(1);
  }
}

main();
