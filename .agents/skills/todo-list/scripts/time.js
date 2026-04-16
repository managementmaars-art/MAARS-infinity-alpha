#!/usr/bin/env node

/**
 * 时间处理脚本
 * 支持 natural language → ISO 8601 标准时间解析
 * 
 * 使用方法:
 *   node scripts/time.js now              # 获取当前时间
 *   node scripts/time.js parse "明天下午3点"  # 解析自然语言时间
 */

import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat.js';
import relativeTime from 'dayjs/plugin/relativeTime.js';
import timezone from 'dayjs/plugin/timezone.js';
import utc from 'dayjs/plugin/utc.js';

dayjs.extend(customParseFormat);
dayjs.extend(relativeTime);
dayjs.extend(timezone);
dayjs.extend(utc);

/**
 * 解析自然语言时间
 */
function parseNaturalTime(input, referenceTime = null) {
  const now = referenceTime ? dayjs(referenceTime) : dayjs();
  let text = input.trim();
  
  // 移除前缀词
  text = text
    .replace(/^(请|帮我|提醒我|记住|提醒|在|于|等|大概|大约|差不多|左右|前后)?\s*/i, '')
    .replace(/\s*(左右|前后|左右|左右)?\s*(去|来|开始|的时候)?\s*$/i, '')
    .trim();
  
  let result = now.clone();
  let foundDate = false;
  
  // 相对时间：半小时后、N分钟后、N小时后、N天后
  const halfHour = text.match(/半\s*小时\s*后/);
  const minLater = text.match(/(\d+)\s*分\s*钟?\s*后/);
  const hourLater = text.match(/(\d+)\s*小时\s*后/);
  const dayLater = text.match(/(\d+)\s*天\s*后/);
  if (halfHour) {
    result = result.add(30, 'minute');
    return result;
  }
  if (minLater) {
    result = result.add(parseInt(minLater[1], 10), 'minute');
    return result;
  }
  if (hourLater) {
    result = result.add(parseInt(hourLater[1], 10), 'hour');
    return result;
  }
  if (dayLater) {
    result = result.add(parseInt(dayLater[1], 10), 'day');
    return result;
  }
  
  // 检查周几
  const weekMatch = text.match(/周[一二三四五六日天]/);
  const isNextWeek = text.includes('下周') || text.includes('下下');
  
  if (weekMatch) {
    const dayMap = { '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 0, '天': 0 };
    const targetDay = dayMap[weekMatch[0][1]];
    let daysUntil = targetDay - now.day();
    if (isNextWeek || daysUntil <= 0) {
      daysUntil += 7;
    }
    result = result.add(daysUntil, 'day');
    foundDate = true;
  }
  
  // 检查日期偏移
  if (text.includes('今天')) {
    // 已经是 now
  } else if (text.includes('后天')) {
    result = result.add(2, 'day');
    foundDate = true;
  } else if (text.includes('明天')) {
    result = result.add(1, 'day');
    foundDate = true;
  } else if (text.includes('昨天')) {
    result = result.subtract(1, 'day');
    foundDate = true;
  }
  
  // 处理时间
  let hour = result.hour();
  let minute = 0;
  
  const timeMatch = text.match(/(\d{1,2})\s*[:点时]\s*(\d{0,2})/);
  if (timeMatch) {
    hour = parseInt(timeMatch[1]);
    minute = timeMatch[2] ? parseInt(timeMatch[2]) : 0;
    
    // 上下午处理
    if ((text.includes('下午') || text.includes('晚上')) && hour < 12) {
      hour += 12;
    } else if ((text.includes('上午') || text.includes('早上')) && hour === 12) {
      hour = 0;
    }
  }
  
  result = result.hour(hour).minute(minute).second(0);
  
  return result;
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2);
  const command = args[0] || 'now';
  
  console.log(`[TIMESTAMP] ${Date.now()}`);
  
  if (command === 'now') {
    const now = dayjs();
    console.log(`[RESULT]`);
    console.log(`iso: ${now.format()}`);
    console.log(`iso-utc: ${now.utc().format()}`);
    console.log(`timestamp: ${now.valueOf()}`);
    console.log(`unix: ${now.unix()}`);
    console.log(`formatted: ${now.format('YYYY-MM-DD HH:mm:ss')}`);
  } else if (command === 'parse') {
    const refArg = args.find(a => a.startsWith('--ref='));
    const referenceTime = refArg ? refArg.replace('--ref=', '') : null;
    const timeInput = args.slice(1).filter(a => !a.startsWith('--ref=')).join(' ').trim() || '';
    
    console.log(`[INPUT] ${timeInput}`);
    console.log(`[REFERENCE] ${referenceTime || 'now'}`);
    
    const parsed = parseNaturalTime(timeInput, referenceTime);
    
    if (parsed && parsed.isValid()) {
      console.log(`[RESULT]`);
      console.log(`iso: ${parsed.format()}`);
      console.log(`iso-utc: ${parsed.utc().format()}`);
      console.log(`timestamp: ${parsed.valueOf()}`);
      console.log(`unix: ${parsed.unix()}`);
      console.log(`formatted: ${parsed.format('YYYY-MM-DD HH:mm:ss')}`);
      console.log(`relative: ${parsed.fromNow()}`);
    } else {
      console.log(`[ERROR] 无法解析时间: ${timeInput}`);
      process.exit(1);
    }
  } else {
    console.log(`Usage:`);
    console.log(`  node scripts/time.js now`);
    console.log(`  node scripts/time.js parse "明天下午3点" [--ref=ISO时间]`);
    process.exit(1);
  }
}

main();
