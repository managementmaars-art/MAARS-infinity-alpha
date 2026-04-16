#!/usr/bin/env tsx

import { ConvexHttpClient } from 'convex/browser';
import { readFileSync, existsSync } from 'fs';
import { api } from '../convex/_generated/api.js';
import { Config, CONFIG_PATH, getConvexUrl } from './types.js';
import { setupProxy } from './proxy-util.js';
import {
  logError,
  logSuccess,
  logInfo,
  logDetail,
  logUsage,
  logNotConfigured,
} from './logger.js';

setupProxy();

async function sendMessage(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 1) {
    logUsage('Usage: tsx send_message.ts <message_text> [file_path]', [
      'tsx send_message.ts "Hello from Claude!"',
      'tsx send_message.ts "Meeting notes" /home/claude/notes.md',
      'tsx send_message.ts "Report" /home/claude/report.pdf',
    ]);
    process.exit(1);
  }

  const [messageText, filePath] = args;

  // Load config
  if (!existsSync(CONFIG_PATH)) {
    logNotConfigured();
  }

  const config: Config = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));

  // Get Convex URL from deployment
  logInfo('📡', 'Connecting to Convex...');
  const deploymentUrl = getConvexUrl(config.deployKey);

  const client = new ConvexHttpClient(deploymentUrl);

  // Verify file exists if provided
  if (filePath && !existsSync(filePath)) {
    logError(`File not found: ${filePath}`);
    process.exit(1);
  }

  logInfo('📤', 'Sending message...');

  try {
    // Build args
    const sendArgs: any = {
      message_text: messageText,
    };

    if (filePath) {
      logInfo('📁', 'Uploading file to Convex Storage...');

      // Get upload URL from Convex
      const uploadUrl = await client.mutation(api.messages.generateUploadUrl);

      // Read file
      const fileBuffer = readFileSync(filePath);
      const fileName = filePath.split('/').pop() || 'file';

      // Convert buffer to Blob for fetch compatibility
      const fileBlob = new Blob([fileBuffer], {
        type: 'application/octet-stream',
      });

      // Upload file to Convex Storage (proxy is set globally via setGlobalDispatcher)
      const uploadResponse = await fetch(uploadUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/octet-stream' },
        body: fileBlob,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`);
      }

      const { storageId } = (await uploadResponse.json()) as {
        storageId: string;
      };

      sendArgs.storage_id = storageId;
      sendArgs.file_name = fileName;

      logDetail(`✓ File uploaded: ${fileName}`);
    }

    await client.action(api.telegram.sendMessage, sendArgs);

    logSuccess('Message sent successfully!');
    if (filePath) {
      logDetail(`→ Text: ${messageText}`);
      logDetail(`→ File: ${filePath.split('/').pop()}`);
      logDetail(
        `→ File will be automatically deleted from storage after sending`
      );
    }
  } catch (error: any) {
    logError(`Failed to send: ${error.message}`);
    process.exit(1);
  }
}

sendMessage().catch((error: Error) => {
  logError(error.message);
  process.exit(1);
});
