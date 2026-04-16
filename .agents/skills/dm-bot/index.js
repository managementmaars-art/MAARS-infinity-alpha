require('dotenv').config();
const { Client, GatewayIntentBits, Partials } = require('discord.js');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const Bree = require('bree');
const db = require('./db');
const { MockClient, startInteractiveInput, MOCK_CHANNEL } = require('./mock');
const logger = require('./logger');

// 加载用户配置
const userConfigPath = path.join(os.homedir(), 'dm-bot', 'config.json');
let userConfig = {};
try {
  if (fs.existsSync(userConfigPath)) {
    userConfig = JSON.parse(fs.readFileSync(userConfigPath, 'utf8'));
  }
} catch (e) {
  logger.warn('读取用户配置失败，使用默认配置');
}

const config = {
  timezone: 'Asia/Shanghai',
  messagePollInterval: 2000,
  scheduleCheckInterval: 60000,
  ...userConfig,
};

// 创建Bree调度器实例
const bree = new Bree({
  root: false, // 禁用root目录检查
  logger: logger,
  jobs: [], // 初始为空，后续从数据库加载
  errorHandler: (error, workerMetadata) => {
    logger.error(`任务 ${workerMetadata.name} 执行失败`, error);
  },
  workerMessageHandler: (name, message) => {
    logger.info(`任务 ${name} 消息:`, message);
  }
});

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages
  ],
  partials: [Partials.Channel]
});

let isProcessing = false;

client.once('clientReady', async () => {
  logger.info(`机器人已上线！登录身份：${client.user.tag}`);
  
  // 清空未完成的消息
  db.clearPendingMessages();
  isProcessing = false;
  
  // 启动消息队列轮询
  startPolling();
  
  // 启动定时任务检查
  startScheduledTaskChecker();
});

client.on('messageCreate', async message => {
  // 忽略机器人消息
  if (message.author.bot) return;

  // 只处理私聊消息
  if (message.guild) return;
  
  // 将消息存入数据库队列
  try {
    const msgId = db.addMessage(message.author.id, message.channel.id, message.content);
    logger.info(`消息已存入队列 ID: ${msgId}, 来自用户: ${message.author.tag}`);
  } catch (error) {
    logger.error('存入消息失败', error);
    await message.reply('抱歉，处理消息时出错，请稍后重试。');
  }
});

// 轮询处理消息队列
function startPolling(botClient = client) {
  setInterval(async () => {
    if (isProcessing || db.hasProcessingMessage()) return;
    
    const message = db.getPendingMessage();
    if (message) {
      logger.info(`[轮询] 准备处理消息 ID: ${message.id}`);
      await processMessage(message, botClient);
    }
  }, config.messagePollInterval);
}

// 定时任务检查（使用Bree）
function startScheduledTaskChecker() {
  // 添加Bree事件监听
  bree.on('worker created', (name) => {
    logger.debug(`[Bree] Worker创建: ${name}`);
  });
  
  bree.on('worker deleted', (name) => {
    logger.debug(`[Bree] Worker删除: ${name}`);
  });
  
  // 首先从数据库加载任务到Bree
  loadTasksFromDatabaseToBree().then(() => {
    // 启动Bree调度器
    bree.start();
    logger.info('[Bree] 调度器已启动');
  }).catch(error => {
    logger.error('[Bree] 启动失败', error);
    process.exit(1);
  });
  
  // 每分钟重新同步一次数据库任务到Bree
  setInterval(() => {
    loadTasksFromDatabaseToBree();
  }, 60 * 1000);
}





// 从数据库增量同步任务到Bree
async function loadTasksFromDatabaseToBree() {
  try {
    const tasks = db.getUserTasks('all');
    const dbTaskNames = new Set(tasks.map(t => `task-${t.id}`));
    
    // 1. 移除数据库中不再启用或已删除的任务
    const currentTaskJobs = (bree.config.jobs || []).filter(j => {
      const name = typeof j === 'object' ? j.name : j;
      return name.startsWith('task-');
    });

    for (const job of currentTaskJobs) {
      const jobName = typeof job === 'object' ? job.name : job;
      if (!dbTaskNames.has(jobName)) {
        logger.info(`[Bree] 移除任务: ${jobName}`);
        await bree.remove(jobName);
      }
    }

    // 2. 添加新任务或更新配置变化的任务
    for (const task of tasks) {
      const jobName = `task-${task.id}`;
      const existingJob = (bree.config.jobs || []).find(j => (typeof j === 'object' ? j.name : j) === jobName);
      
      const jobConfig = {
        name: jobName,
        path: path.join(__dirname, 'jobs', 'worker.js'),
        worker: {
          workerData: {
            taskId: task.id,
            userId: task.user_id,
            channelId: task.channel_id,
            taskContent: task.task_content,
            taskType: 'schedule'
          }
        }
      };
      
      // 设置调度方式
      if (task.cron_expression) {
        jobConfig.cron = task.cron_expression;
        jobConfig.timezone = config.timezone;
      } else if (task.next_run_time) {
        const nextRunDate = new Date(task.next_run_time);
        if (nextRunDate > new Date()) {
          jobConfig.date = nextRunDate;
        } else {
          continue; // 跳过已过期的一次性任务
        }
      } else {
        jobConfig.timeout = 0;
      }

      if (existingJob) {
        const existingConfig = typeof existingJob === 'object' ? existingJob : null;
        const isChanged = !existingConfig || 
                         existingConfig.cron !== jobConfig.cron || 
                         existingConfig.date?.toString() !== jobConfig.date?.toString() ||
                         JSON.stringify(existingConfig.worker?.workerData) !== JSON.stringify(jobConfig.worker?.workerData);
        
        if (isChanged) {
          logger.info(`[Bree] 更新任务: ${jobName}`);
          await bree.remove(jobName);
          await bree.add(jobConfig);
        }
      } else {
        logger.info(`[Bree] 添加新任务: ${jobName}`);
        await bree.add(jobConfig);
      }
    }
    
    logger.debug(`[Bree] 同步完成，当前共有 ${(bree.config.jobs || []).length} 个活跃任务`);
    
  } catch (error) {
    logger.error('[Bree] 从数据库同步任务失败', error);
  }
}

// 添加延迟任务
async function addDelayedTask(userId, channelId, delayMinutes = 15, message = '机器人已叫醒！') {
  try {
    const jobName = `delayed-wake-${Date.now()}`;
    
    const jobConfig = {
      name: jobName,
      path: path.join(__dirname, 'jobs', 'worker.js'),
      timeout: `${delayMinutes}m`,
      worker: {
        workerData: {
          userId,
          channelId,
          message,
          taskType: 'delayed'
        }
      }
    };
    
    await bree.add(jobConfig);
    await bree.start(jobName);
    logger.info(`[Bree] 已创建延迟任务: ${delayMinutes}分钟后执行`);
    
    return { success: true, jobName };
  } catch (error) {
    logger.error('[Bree] 创建延迟任务失败', error);
    return { success: false, error: error.message };
  }
}

// 处理单条消息
async function processMessage(message, botClient = client) {
  isProcessing = true;
  logger.info(`[开始处理] 消息 ID: ${message.id}, 用户: ${message.user_id}`);
  
  try {
    db.markAsProcessing(message.id);
    
    const channel = await botClient.channels.fetch(message.channel_id);
    if (!channel) throw new Error('无法找到频道');

    const userSessionId = db.getUserSession(message.user_id);

    // 执行 opencode run
    const result = await runOpencode(message.content, userSessionId, message.user_id, message.channel_id);
    
    if (result.sessionId) {
      db.setUserSession(message.user_id, result.sessionId);
    }
    
    await channel.send(result.text);
    db.markAsCompleted(message.id);
    logger.info(`[处理完成] 消息 ID: ${message.id}`);
    
  } catch (error) {
    logger.error(`[处理失败] 消息 ID: ${message.id}`, error);
    try {
      const channel = await botClient.channels.fetch(message.channel_id);
      if (channel) await channel.send(`处理消息时出错: ${error.message}`);
    } catch (e) {}
    db.markAsCompleted(message.id);
  } finally {
    isProcessing = false;
  }
}

// 调用 opencode run
function runOpencode(prompt, sessionId = null, userId = null, channelId = null) {
  return new Promise((resolve, reject) => {
    let finished = false;

    const args = ['run', '--format', 'json', prompt];
    if (sessionId) args.push('--session', sessionId);

    const isWin = process.platform === 'win32';
    const spawnOptions = {
      cwd: process.cwd(),
      env: {
        ...process.env,
        SKILL_PATH: path.join(process.cwd(), '.opencode', 'tools'),
        DISCORD_USER_ID: userId || '',
        DISCORD_CHANNEL_ID: channelId || ''
      },
      stdio: ['ignore', 'pipe', 'pipe']
    };

    // 日志目录
    const logsDir = path.join(os.homedir(), 'dm-bot', 'opencode-logs');
    const fs = require('fs');
    if (!fs.existsSync(logsDir)) {
      fs.mkdirSync(logsDir, { recursive: true });
    }

    // 生成日志文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').slice(0, 19);
    const logFile = path.join(logsDir, `${timestamp}.log`);

    let childProcess;
    if (isWin) {
      childProcess = spawn('cmd.exe', ['/c', 'opencode', ...args], spawnOptions);
    } else {
      childProcess = spawn('opencode', args, spawnOptions);
    }

    let stdout = '';
    let stderr = '';
    let newSessionId = sessionId;

    // 实时记录输出到日志
    childProcess.stdout.on('data', (data) => {
      const str = data.toString();
      stdout += str;
      fs.appendFileSync(logFile, `[stdout] ${str}`);
    });
    childProcess.stderr.on('data', (data) => {
      const str = data.toString();
      stderr += str;
      fs.appendFileSync(logFile, `[stderr] ${str}`);
    });

    childProcess.on('close', (code) => {
      if (finished) return;
      finished = true;

      // 记录命令信息
      const cmdLine = `opencode ${args.join(' ')}`;
      const logHeader = `[${new Date().toISOString()}] [INFO] Executing: ${cmdLine}\n`;
      fs.appendFileSync(logFile, logHeader);

      if (code === 0) {
        let text = '';
        const jsonLines = stdout.trim().split('\n');

        for (const line of jsonLines) {
          try {
            const trimmedLine = line.trim();
            if (!trimmedLine) continue;

            const json = JSON.parse(trimmedLine);
            if (!newSessionId && json.sessionID) newSessionId = json.sessionID;

            if (json.type === 'text' && json.part?.text) {
              text += json.part.text;
            }
          } catch (e) {
            if (line.includes('你好') || line.includes('Hello')) {
              text = line.trim();
            }
          }
        }
        fs.appendFileSync(logFile, `[${new Date().toISOString()}] [INFO] Completed successfully\n`);
        resolve({ text: text || '处理完成', sessionId: newSessionId });
      } else {
        fs.appendFileSync(logFile, `[${new Date().toISOString()}] [ERROR] Exit code: ${code}\n`);
        reject(new Error(stderr.trim() || `进程退出码: ${code}`));
      }
    });

    childProcess.on('error', (error) => {
      if (!finished) {
        finished = true;
        fs.appendFileSync(logFile, `[${new Date().toISOString()}] [ERROR] ${error.message}\n`);
        reject(new Error(`执行opencode失败: ${error.message}`));
      }
    });
  });
}

client.on('error', error => logger.error('机器人发生错误', error));

const TOKEN = config.token || process.env.DISCORD_TOKEN;
let isMockMode = false;

function startBot(options = {}) {
  const mockValue = options.mock;
  isMockMode = mockValue === true ? true : (mockValue === 'non-interactive' ? 'non-interactive' : false);
  
  if (isMockMode) {
    logger.info('[Mock] 使用模拟模式启动...');
    return startMockBot();
  }
  
  return client.login(TOKEN)
    .then(() => {
      logger.info('正在登录 Discord...');
      return client;
    })
    .catch(error => {
      logger.error('登录失败', error);
      throw error;
    });
}

async function startMockBot() {
  const mockClient = new MockClient();
  logger.info(`[Mock] 机器人已上线！登录身份：MockBot`);
  db.clearPendingMessages();
  isProcessing = false;
  startPolling(mockClient);
  startScheduledTaskChecker();
  
  startInteractiveInput(async (message) => {
    if (message.author.bot || message.guild) return;
    try {
      const msgId = db.addMessage(message.author.id, MOCK_CHANNEL.id, message.content);
      logger.info(`[Mock] 消息已存入队列 ID: ${msgId}`);
    } catch (error) {
      logger.error('[Mock] 存入消息失败', error);
    }
  }, isMockMode !== 'non-interactive');
  
  return mockClient;
}

module.exports = { startBot };

if (require.main === module) {
  startBot();
}
