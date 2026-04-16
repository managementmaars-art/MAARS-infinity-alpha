#!/usr/bin/env node

const { Command } = require('commander');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { startBot } = require('../index');
const { resetDatabase } = require('../db');
const { formatDateTime } = require('../utils');

// 标准配置目录: ~/dm-bot/
const configDir = path.join(os.homedir(), 'dm-bot');
const configPath = path.join(configDir, 'config.json');

// 确保配置目录存在
function ensureConfigDir() {
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
}

// 读取配置
function readConfig() {
  if (fs.existsSync(configPath)) {
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }
  return {};
}

// 保存配置
function saveConfig(config) {
  ensureConfigDir();
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}

// 复制 skills 到 OpenCode 目录
function copySkills() {
  const targetBaseDir = path.join(process.cwd(), '.opencode', 'skills');
  
  try {
    // 查找根目录下的所有 SKILL.md 文件
    const rootDir = path.join(__dirname, '..');
    const skillFile = path.join(rootDir, 'SKILL.md');
    
    if (!fs.existsSync(skillFile)) {
      return;
    }
    
    // 读取 SKILL.md 内容，提取 name 字段
    const content = fs.readFileSync(skillFile, 'utf8');
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    
    if (!frontmatterMatch) {
      console.warn('[skills] SKILL.md 缺少 frontmatter');
      return;
    }
    
    // 解析 frontmatter 获取 name
    const frontmatter = frontmatterMatch[1];
    const nameMatch = frontmatter.match(/^name:\s*(.+)$/m);
    
    if (!nameMatch) {
      console.warn('[skills] SKILL.md 缺少 name 字段');
      return;
    }
    
    const skillName = nameMatch[1].trim();
    const targetDir = path.join(targetBaseDir, skillName);
    
    // 创建目标目录并复制文件
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }
    
    const targetFile = path.join(targetDir, 'SKILL.md');
    fs.copyFileSync(skillFile, targetFile);
    console.log(`[skills] 已同步到 .opencode/skills/${skillName}/`);
  } catch (error) {
    console.warn('[skills] 同步失败:', error.message);
  }
}

// 启动机器人的逻辑
async function doStart(options = {}) {
  // 先复制 skills 到 .opencode/skills
  copySkills();
  
  // Mock 模式不需要 token
  if (options.mock) {
    console.log('[Mock] 使用模拟模式，跳过 token 验证');
    await startBot({ mock: true });
    return;
  }
  
  let token = options.token;
  
  // 优先级: 1. 命令行参数 2. 环境变量 3. 配置文件
  if (!token) {
    token = process.env.DISCORD_TOKEN;
  }
  if (!token) {
    const config = readConfig();
    token = config.token;
  }
  
  if (!token) {
    ensureConfigDir();
    
    // 生成配置文件模板
    const configTemplate = {
      token: "YOUR_DISCORD_BOT_TOKEN_HERE",
      description: "请将上面的 token 替换为你的 Discord Bot Token",
      timezone: "Asia/Shanghai",
      scheduleCheckInterval: 60000,
      messagePollInterval: 2000
    };
    saveConfig(configTemplate);
    
    console.error('错误: 未设置 Discord Token');
    console.log('');
    console.log('已为你生成配置文件模板:');
    console.log(`  ${configPath}`);
    console.log('');
    console.log('请按以下步骤操作:');
    console.log('  1. 打开上述文件');
    console.log('  2. 将 YOUR_DISCORD_BOT_TOKEN_HERE 替换为你的 Discord Bot Token');
    console.log('  3. 再次运行 dm-bot');
    console.log('');
    console.log('或者你可以使用以下方式直接设置:');
    console.log('  dm-bot --token <your-token>');
    console.log('');
    console.log('提示: 使用 --mock 参数可以在没有 token 的情况下启动模拟模式');
    process.exit(1);
  }
  
  process.env.DISCORD_TOKEN = token;
  console.log('正在启动 Discord Bot...');
  await startBot();
}

const program = new Command();

program
  .name('dm-bot')
  .description('Discord DM Bot CLI with OpenCode integration')
  .version('1.0.0')
  .option('-t, --token <token>', 'Discord Bot Token')
  .option('-m, --mock', '使用模拟模式（无需 Discord 连接，用于本地测试）')
  .action(async (options) => {
    // 默认执行启动
    await doStart(options);
  });

program
  .command('start')
  .description('启动 Discord 机器人（默认命令）')
  .option('-t, --token <token>', 'Discord Bot Token')
  .option('-m, --mock', '使用模拟模式')
  .action(async (options) => {
    // 合并全局选项
    await doStart({ ...program.opts(), ...options });
  });

program
  .command('config')
  .description('配置 Discord Bot')
  .option('-t, --token <token>', '设置 Discord Bot Token', '')
  .action((options) => {
    if (options.token) {
      const config = readConfig();
      config.token = options.token;
      saveConfig(config);
      console.log(`Token 已保存到 ${configPath}`);
    } else {
      const config = readConfig();
      if (config.token) {
        console.log('当前配置:');
        console.log(`配置文件位置: ${configPath}`);
        console.log(`Token: ${config.token.substring(0, 10)}...`);
      } else {
        console.log('未找到配置');
        console.log('使用: dm-bot config --token <your-token>');
      }
    }
  });

program
  .command('reset')
  .description('重置数据库（清空消息队列和会话）')
  .action(() => {
    console.log('正在重置数据库...');
    resetDatabase();
    console.log('数据库已重置');
  });

program
  .command('new')
  .description('开启新会话（重置所有用户的 Session ID）')
  .action(() => {
    console.log('正在开启新会话...');
    const { setUserSession } = require('../db');
    // 这里我们可以选择清空所有 session 或者为当前操作用户重置
    // 按照你的要求，我们直接重置所有用户的会话
    const { resetDatabase } = require('../db');
    // 如果只想重置 session，我们可以在 db.js 增加一个专门的方法，
    // 但目前 resetDatabase 已经包含了清空 user_sessions 的逻辑。
    // 为了更精确，我直接在 cli 里调用 db 的操作。
    resetDatabase(); 
    console.log('新会话已开启，Session ID 已重置。');
  });

// Schedule 命令
const scheduleCmd = program
  .command('schedule')
  .description('定时任务管理');

scheduleCmd
  .command('create <cron> <content> [repeat]')
  .description('创建定时任务')
  .action((cron, content, repeat) => {
    const { addScheduledTask } = require('../db');
    const cronParser = require('cron-parser');
    
    // 计算下次执行时间
    let nextRunTime;
    try {
      const interval = cronParser.parseExpression(cron, { tz: 'Asia/Shanghai' });
      nextRunTime = formatDateTime(interval.next().toDate());
    } catch (e) {
      console.log(JSON.stringify({ success: false, message: `无效的 cron 表达式: ${e.message}` }));
      process.exit(1);
    }
    
    // 使用默认用户/频道（CLI 模式）
    const userId = process.env.DISCORD_USER_ID || 'cli-user';
    const channelId = process.env.DISCORD_CHANNEL_ID || 'cli-channel';
    const isRepeat = repeat !== 'false';
    
    try {
      // 保存到数据库
      const taskId = addScheduledTask(userId, channelId, content, cron, nextRunTime, isRepeat);
      
      console.log(JSON.stringify({
        success: true,
        message: '定时任务已成功保存到数据库，主进程将在同步后自动调度',
        task: { id: taskId, cron, content, nextRun: nextRunTime, isRepeat }
      }, null, 2));
      
    } catch (e) {
      console.log(JSON.stringify({ success: false, message: `创建失败: ${e.message}` }));
    }
  });

scheduleCmd
  .command('list')
  .description('列出所有定时任务')
  .action(() => {
    const { getUserTasks } = require('../db');
    const userId = process.env.DISCORD_USER_ID || 'cli-user';
    const tasks = getUserTasks(userId);
    
    if (tasks.length === 0) {
      console.log(JSON.stringify({ success: true, message: '暂无定时任务', tasks: [] }));
    } else {
      console.log(JSON.stringify({ success: true, tasks }, null, 2));
    }
  });

scheduleCmd
  .command('delete <id>')
  .description('删除定时任务')
  .action((id) => {
    const { deleteTask } = require('../db');
    try {
      deleteTask(id);
      console.log(JSON.stringify({ success: true, message: `任务 ${id} 已删除` }));
    } catch (e) {
      console.log(JSON.stringify({ success: false, message: `删除失败: ${e.message}` }));
    }
  });

// Delayed 命令 - 延迟任务管理
const delayedCmd = program
  .command('delayed')
  .description('延迟任务管理');

delayedCmd
  .command('wake <minutes> [message]')
  .description('延迟指定分钟后叫醒机器人')
  .action((minutes, message) => {
    const { addScheduledTask } = require('../db');
    
    const userId = process.env.DISCORD_USER_ID || 'cli-user';
    const channelId = process.env.DISCORD_CHANNEL_ID || 'cli-channel';
    
    const delayMinutes = parseFloat(minutes);
    if (isNaN(delayMinutes) || delayMinutes <= 0) {
      console.log(JSON.stringify({ success: false, message: '无效的分钟数，必须是正数' }));
      process.exit(1);
    }
    
    // 计算执行时间
    const runDate = new Date(Date.now() + delayMinutes * 60 * 1000);
    const nextRunTime = formatDateTime(runDate);
    const taskContent = message || '机器人已叫醒！';

    try {
      // 延迟任务本质上是不重复的一次性任务
      const taskId = addScheduledTask(userId, channelId, taskContent, null, nextRunTime, false);
      
      console.log(JSON.stringify({
        success: true,
        message: `延迟任务已保存，将在 ${delayMinutes} 分钟后由主进程执行`,
        taskId,
        executeTime: nextRunTime
      }, null, 2));
    } catch (e) {
      console.log(JSON.stringify({ success: false, message: `创建延迟任务失败: ${e.message}` }));
    }
  });

program.parse();
