const fs = require('fs');
const path = require('path');
const os = require('os');

// 读取版本号
const pkgPath = path.join(__dirname, 'package.json');
let version = 'unknown';
try {
  version = JSON.parse(fs.readFileSync(pkgPath, 'utf8')).version || 'unknown';
} catch (e) {}

const logDir = path.join(os.homedir(), 'dm-bot', 'logs');
const logFile = path.join(logDir, 'bot.log');

// 确保日志目录存在
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// 第一行日志输出版本
const versionLine = `[${new Date().toISOString()}] [INFO] dm-bot v${version} starting...`;
try {
  fs.appendFileSync(logFile, versionLine + '\n');
} catch (err) {}
console.log(versionLine);

function formatMessage(level, message, data = null) {
  const timestamp = new Date().toISOString();
  let logLine = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  if (data) {
    if (data instanceof Error) {
      logLine += `\nError: ${data.message}\nStack: ${data.stack}`;
    } else {
      logLine += ` ${JSON.stringify(data)}`;
    }
  }
  return logLine;
}

function writeLog(level, message, data) {
  const line = formatMessage(level, message, data);
  // 输出到控制台
  if (level === 'error') {
    console.error(line);
  } else if (level === 'warn') {
    console.warn(line);
  } else {
    console.log(line);
  }
  // 写入文件
  try {
    fs.appendFileSync(logFile, line + '\n');
  } catch (err) {
    console.error('无法写入日志文件:', err);
  }
}

const logger = {
  info: (msg, data) => writeLog('info', msg, data),
  error: (msg, data) => writeLog('error', msg, data),
  warn: (msg, data) => writeLog('warn', msg, data),
  debug: (msg, data) => writeLog('debug', msg, data),
  getLogPath: () => logFile
};

module.exports = logger;
