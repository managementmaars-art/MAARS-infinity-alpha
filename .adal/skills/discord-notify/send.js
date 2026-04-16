#!/usr/bin/env node

const fetch = require('node-fetch');
const HttpsProxyAgent = require('https-proxy-agent');

const BOT_TOKEN = process.env.DISCORD_BOT_TOKEN;
const USER_ID = process.env.DISCORD_USER_ID;
const MESSAGE = process.argv[2];

if (!BOT_TOKEN) {
  console.error('错误: 未设置 DISCORD_BOT_TOKEN 环境变量');
  process.exit(1);
}

if (!USER_ID) {
  console.error('错误: 未设置 DISCORD_USER_ID 环境变量');
  process.exit(1);
}

if (!MESSAGE) {
  console.error('用法: node send.js "消息内容"');
  process.exit(1);
}

async function sendDM() {
  const headers = {
    'Authorization': `Bot ${BOT_TOKEN}`,
    'Content-Type': 'application/json'
  };

  // 1. 创建 DM 频道
  let dmChannel;
  try {
    const dmRes = await fetch('https://discord.com/api/v10/users/@me/channels', {
      method: 'POST',
      headers,
      body: JSON.stringify({ recipient_id: USER_ID })
    });
    if (!dmRes.ok) throw new Error(`${dmRes.status} ${await dmRes.text()}`);
    dmChannel = await dmRes.json();
  } catch (err) {
    // 直连失败，尝试代理
    const agent = new HttpsProxyAgent('http://127.0.0.1:10808');
    const dmRes = await fetch('https://discord.com/api/v10/users/@me/channels', {
      method: 'POST',
      headers,
      body: JSON.stringify({ recipient_id: USER_ID }),
      agent
    });
    if (!dmRes.ok) throw new Error(`创建 DM 频道失败: ${dmRes.status} ${await dmRes.text()}`);
    dmChannel = await dmRes.json();
  }

  // 2. 发送消息
  try {
    const msgRes = await fetch(`https://discord.com/api/v10/channels/${dmChannel.id}/messages`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content: MESSAGE })
    });
    if (!msgRes.ok) throw new Error(`${msgRes.status} ${await msgRes.text()}`);
  } catch (err) {
    // 直连失败，尝试代理
    const agent = new HttpsProxyAgent('http://127.0.0.1:10808');
    const msgRes = await fetch(`https://discord.com/api/v10/channels/${dmChannel.id}/messages`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ content: MESSAGE }),
      agent
    });
    if (!msgRes.ok) throw new Error(`发送消息失败: ${msgRes.status} ${await msgRes.text()}`);
  }

  console.log(JSON.stringify({ success: true, message: '消息发送成功' }));
}

sendDM().catch(err => {
  console.error(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
