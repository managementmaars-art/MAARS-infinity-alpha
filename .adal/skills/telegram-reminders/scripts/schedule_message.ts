#!/usr/bin/env tsx

import { ConvexHttpClient } from 'convex/browser';
import { readFileSync, existsSync } from 'fs';
import { api } from '../convex/_generated/api.js';
import * as chrono from 'chrono-node';
import { Config, CONFIG_PATH, ParsedTime, getConvexUrl } from './types.js';
import { setupProxy } from './proxy-util.js';
import {
  logError,
  logSuccess,
  logInfo,
  logDetail,
  logUsage,
  logNotConfigured,
} from './logger.js';

// Blob is available globally in Node.js 18+
declare const Blob: typeof globalThis extends { Blob: infer B } ? B : any;

setupProxy();

async function scheduleMessage(): Promise<void> {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    logUsage(
      'Usage: tsx schedule_message.ts <time_expression> <title> [message_text] [file_path]',
      [
        'tsx schedule_message.ts "tomorrow 10am" "Meeting" "Team standup"',
        'tsx schedule_message.ts "in 5 minutes" "Quick reminder" "Check email"',
        'tsx schedule_message.ts "next Monday 9am" "Report" "Weekly report" /path/to/file.pdf',
        'tsx schedule_message.ts "every day at 9am" "Daily" "Good morning!"',
        'tsx schedule_message.ts "every 2 hours" "Hydration" "Drink water!"',
      ]
    );
    process.exit(1);
  }

  const [timeExpression, title, messageText, filePath] = args;

  // Load config
  if (!existsSync(CONFIG_PATH)) {
    logNotConfigured();
  }

  const config: Config = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));

  // Parse time
  const { scheduledTime, recurring } = parseTime(timeExpression);

  logInfo('📅', 'Scheduling message...');
  logDetail(`Title: ${title}`);
  logDetail(`Time: ${new Date(scheduledTime).toLocaleString()}`);
  if (recurring) {
    logDetail(`Recurring: ${recurring}`);
  }

  // Get Convex URL
  const deploymentUrl = getConvexUrl(config.deployKey);
  const client = new ConvexHttpClient(deploymentUrl);

  // Verify file exists if provided
  if (filePath && !existsSync(filePath)) {
    logError(`File not found: ${filePath}`);
    process.exit(1);
  }

  try {
    // Build args, only including optional fields if they have values
    const scheduleArgs: any = {
      title,
      message_text: messageText,
      scheduled_time: scheduledTime,
    };

    // Only add recurring if it exists
    if (recurring) {
      scheduleArgs.recurring = recurring;
    }

    // Handle file upload if provided
    if (filePath) {
      logInfo('📁', 'Uploading file to Convex Storage...');

      // Get upload URL from Convex
      const uploadUrl = await client.mutation(api.messages.generateUploadUrl);

      // Read file
      const fileBuffer = readFileSync(filePath);
      const fileName = filePath.split('/').pop() || 'file';

      // Convert buffer to Blob for fetch compatibility
      const fileBlob = new Blob([fileBuffer], { type: 'application/octet-stream' });

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

      scheduleArgs.storage_id = storageId;
      scheduleArgs.file_name = fileName;

      logDetail(`✓ File uploaded: ${fileName}`);
    }

    const messageId = await client.mutation(
      api.messages.scheduleMessage,
      scheduleArgs
    );

    logSuccess('Message scheduled successfully!');
    logDetail(`ID: ${messageId}`);
    if (filePath) {
      logDetail(
        `→ File will be sent and deleted from storage when message is delivered`
      );
    }
  } catch (error: any) {
    logError(`Failed to schedule: ${error.message}`);
    process.exit(1);
  }
}

function parseTime(expression: string): ParsedTime {
  const lowerExpr = expression.toLowerCase();

  // Check for recurring patterns
  const recurringPatterns = [
    { pattern: /every (\d+) minutes?/, type: 'interval' as const },
    { pattern: /every (\d+) hours?/, type: 'interval' as const },
    {
      pattern: /every day at (\d+(?::\d+)?(?:am|pm)?)/i,
      type: 'daily' as const,
    },
    {
      pattern:
        /every (monday|tuesday|wednesday|thursday|friday|saturday|sunday) at (\d+(?::\d+)?(?:am|pm)?)/i,
      type: 'weekly' as const,
    },
    {
      pattern: /every (weekday|weekend) at (\d+(?::\d+)?(?:am|pm)?)/i,
      type: 'weekday' as const,
    },
  ];

  for (const { pattern, type } of recurringPatterns) {
    const match = lowerExpr.match(pattern);
    if (match) {
      return parseRecurring(expression, type, match);
    }
  }

  // Parse one-time scheduled time
  const parsedDate = chrono.parseDate(expression, new Date(), {
    forwardDate: true,
  });

  if (!parsedDate) {
    throw new Error(`Could not parse time expression: ${expression}`);
  }

  return {
    scheduledTime: parsedDate.getTime(),
    recurring: undefined,
  };
}

function parseRecurring(
  expression: string,
  type: 'interval' | 'daily' | 'weekly' | 'weekday',
  match: RegExpMatchArray
): ParsedTime {
  const now = Date.now();

  if (type === 'interval') {
    const amount = parseInt(match[1]);
    const unit = expression.includes('hour') ? 'hours' : 'minutes';
    const ms = unit === 'hours' ? amount * 60 * 60 * 1000 : amount * 60 * 1000;

    return {
      scheduledTime: now + ms,
      recurring: `every ${amount} ${unit}`,
    };
  }

  // For daily, weekly, weekday patterns - use chrono to parse the time part
  const timeStr = match[match.length - 1];
  const parsedDate = chrono.parseDate(timeStr, new Date(), {
    forwardDate: true,
  });

  if (!parsedDate) {
    throw new Error(`Could not parse time: ${timeStr}`);
  }

  return {
    scheduledTime: parsedDate.getTime(),
    recurring: expression,
  };
}

scheduleMessage().catch((error: Error) => {
  logError(error.message);
  process.exit(1);
});
