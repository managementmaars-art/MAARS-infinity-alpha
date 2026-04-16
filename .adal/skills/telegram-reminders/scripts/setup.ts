#!/usr/bin/env tsx

import { writeFileSync } from 'fs';
import { execSync } from 'child_process';
import { Config, CONFIG_PATH, BotInfo } from './types.js';
import { logError, logSuccess, logInfo, logDetail, log } from './logger.js';
import { setupProxy } from './proxy-util.js';

setupProxy();

async function setup(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 3) {
    console.error(
      'Usage: tsx setup.ts <bot_token> <user_id> <convex_deploy_key>'
    );
    console.error('');
    console.error('Steps to get credentials:');
    console.error('1. Bot Token: Message @BotFather on Telegram, create a bot');
    console.error('2. User ID: Message @userinfobot on Telegram');
    console.error(
      '3. Deploy Key: Get from Convex dashboard (Settings > Deploy Keys)'
    );
    logDetail('- Login at https://dashboard.convex.dev', '   ');
    logDetail('- Create a new project', '   ');
    logDetail('- Go to Settings > Deploy Keys', '   ');
    logDetail("- Create a 'Production' deploy key", '   ');
    process.exit(1);
  }

  const [botToken, userId, deployKey] = args;

  logInfo('🔧', 'Setting up Telegram Reminders with Convex...\n');

  // Step 1: Verify Telegram credentials (skip in sandboxed environments)
  logInfo('1️⃣', 'Verifying Telegram bot...');
  try {
    const botInfo = await verifyTelegramBot(botToken);
    logDetail(`✓ Bot verified: @${botInfo.username}`);
  } catch (error: any) {
    console.warn(
      `   ⚠ Could not verify bot (fetch may be unavailable): ${error.message}`
    );
    logDetail('→ Proceeding with setup anyway...');
  }

  // Step 2: Save configuration FIRST (so other tools can work)
  logInfo('\n2️⃣', 'Saving configuration...');
  const config: Config = {
    botToken,
    userId,
    deployKey,
    setupDate: new Date().toISOString(),
  };

  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  logDetail(`✓ Config saved to ${CONFIG_PATH}`);

  // Step 3: Install dependencies
  logInfo('\n3️⃣', 'Installing dependencies...');
  try {
    execSync('npm install', { stdio: 'inherit' });
    logDetail('✓ Dependencies installed');
  } catch (error) {
    logDetail('✗ Failed to install dependencies');
    process.exit(1);
  }

  // Step 4: Deploy to Convex
  logInfo('\n4️⃣', 'Deploying to Convex...');
  try {
    // Set deploy key as environment variable
    process.env.CONVEX_DEPLOY_KEY = deployKey;

    // Create .env.local for local development
    writeFileSync('.env.local', `CONVEX_DEPLOY_KEY=${deployKey}\n`);

    // Deploy
    execSync('npx convex deploy', { stdio: 'inherit' });
    logDetail('✓ Deployed to Convex');

    // Set environment variables in Convex
    logInfo('\n5️⃣', 'Setting Telegram credentials in Convex...');
    execSync(`npx convex env set TELEGRAM_BOT_TOKEN "${botToken}"`, {
      stdio: 'inherit',
    });
    execSync(`npx convex env set TELEGRAM_USER_ID "${userId}"`, {
      stdio: 'inherit',
    });
    logDetail('✓ Environment variables set');
  } catch (error) {
    logDetail('✗ Deployment failed');
    logDetail('→ Make sure your deploy key is valid');
    logDetail('→ Check https://dashboard.convex.dev for errors');
    process.exit(1);
  }

  // Step 6: Test sending a message via Convex
  logInfo('\n6️⃣', 'Testing message send...');
  try {
    await sendTestMessageViaConvex(deployKey);
    logDetail('✓ Test message sent successfully!');
    logDetail('→ Check your Telegram for the test message');
    logDetail(
      "→ If you don't see it, make sure you've started a chat with your bot"
    );
  } catch (error: any) {
    console.warn(`   ⚠ Could not send test message: ${error.message}`);
    logDetail(
      '→ You can test manually with: npx convex run telegram:sendMessage \'{"message_text":"Test"}\''
    );
  }

  logSuccess('\nSetup complete!');
  log('\nYour Telegram reminder system is now running 24/7 in Convex Cloud!');
  log("\n⚠️  IMPORTANT: Make sure you've started a chat with your bot!");
  logDetail('→ Search for your bot on Telegram');
  logDetail("→ Press 'Start' to enable messages");
  log(
    '\nTo send messages (use Convex CLI instead of npm scripts in sandboxed environments):'
  );
  log(
    '  • Send: npx convex run telegram:sendMessage \'{"message_text":"Your message"}\''
  );
  log(
    '  • Schedule: npx convex run messages:schedule \'{"scheduled_time":1234567890,"title":"Title","message":"Text"}\''
  );
  log('\nMonitor your deployment:');
  log('  → https://dashboard.convex.dev');
}

interface TelegramResponse<T = unknown> {
  ok: boolean;
  description?: string;
  result?: T;
}

async function verifyTelegramBot(botToken: string): Promise<BotInfo> {
  const url = `https://api.telegram.org/bot${botToken}/getMe`;
  const response = await fetch(url);
  const result = (await response.json()) as TelegramResponse<BotInfo>;

  if (!result.ok) {
    throw new Error(result.description || 'Invalid bot token');
  }

  return result.result!;
}

async function sendTestMessage(
  botToken: string,
  userId: string
): Promise<void> {
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: userId,
      text: '✅ Telegram Reminders setup successful! Your bot is ready to send messages.',
    }),
  });

  const result = (await response.json()) as TelegramResponse;
  if (!result.ok) {
    throw new Error(result.description || 'Failed to send test message');
  }
}

async function sendTestMessageViaConvex(deployKey: string): Promise<void> {
  try {
    execSync(
      `npx convex run telegram:sendMessage '{"message_text":"✅ Telegram Reminders setup successful! Your bot is ready to send messages."}'`,
      { stdio: 'inherit' }
    );
  } catch (error: any) {
    throw new Error('Convex test message failed');
  }
}

setup().catch((error: Error) => {
  logError(`\nSetup failed: ${error.message}`);
  process.exit(1);
});
