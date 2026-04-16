/**
 * Mock 客户端 - 用于本地测试，无需真实 Discord 连接
 */

const readline = require('readline');
const db = require('./db');

// 模拟用户信息
const MOCK_USER = {
  id: 'mock-user-001',
  tag: 'TestUser#0001',
  username: 'TestUser'
};

const MOCK_CHANNEL = {
  id: 'mock-channel-001'
};

class MockClient {
  constructor() {
    this.user = { tag: 'MockBot#0000' };
    this.isReady = false;
    this.channels = {
      fetch: async (channelId) => {
        if (channelId === MOCK_CHANNEL.id) {
          return new MockChannel();
        }
        return null;
      }
    };
  }

  async login() {
    console.log('[Mock] 模拟登录成功');
    this.isReady = true;
    return Promise.resolve();
  }

  on(event, callback) {
    if (event === 'clientReady') {
      // 延迟触发 ready 事件
      setTimeout(() => callback(), 100);
    }
    // 忽略其他事件
  }
}

class MockChannel {
  constructor() {
    this.id = MOCK_CHANNEL.id;
  }

  async send(content) {
    // 模拟发送消息 - 打印到控制台
    console.log('\n' + '='.repeat(50));
    console.log('[Bot 回复]');
    console.log('-'.repeat(50));
    console.log(content);
    console.log('='.repeat(50) + '\n');
    return Promise.resolve({ content });
  }
}

/**
 * 创建 readline 接口用于命令行输入
 */
function createReadlineInterface() {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

/**
 * 启动交互式输入循环
 */
function startInteractiveInput(onMessage, interactive = true) {
  // 非交互模式：不启动 readline
  if (!interactive) {
    console.log('[Mock] 非交互模式，等待消息队列处理...');
    return null;
  }
  
  const rl = createReadlineInterface();
  
  console.log('\n' + '='.repeat(50));
  console.log('Mock 模式已启动');
  console.log('-'.repeat(50));
  console.log('直接输入消息模拟用户发送，按 Ctrl+C 退出');
  console.log('='.repeat(50) + '\n');

  const prompt = () => {
    rl.question('[用户输入] > ', async (input) => {
      const message = input.trim();
      if (message) {
        // 模拟用户发送消息
        console.log(`[Mock] 收到消息: ${message}`);
        await onMessage({
          author: { ...MOCK_USER, bot: false },
          guild: null, // 私聊
          channel: new MockChannel(),
          content: message
        });
      }
      prompt();
    });
  };

  prompt();

  rl.on('close', () => {
    console.log('\n[Mock] 退出模拟模式');
    process.exit(0);
  });

  return rl;
}

module.exports = {
  MockClient,
  MockChannel,
  MOCK_USER,
  MOCK_CHANNEL,
  startInteractiveInput
};
