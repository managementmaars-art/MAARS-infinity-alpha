"use node";

import { v } from "convex/values";
import { action, internalAction } from "./_generated/server";
import { internal } from "./_generated/api";

// Send a message immediately via Telegram
export const sendMessage = action({
  args: {
    message_text: v.string(),
    storage_id: v.optional(v.id("_storage")),
    file_name: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const botToken = process.env.TELEGRAM_BOT_TOKEN;
    const userId = process.env.TELEGRAM_USER_ID;

    if (!botToken || !userId) {
      throw new Error("Telegram credentials not configured");
    }

    try {
      if (args.storage_id) {
        // Get file from storage
        const fileBlob = await ctx.storage.get(args.storage_id);
        if (!fileBlob) {
          throw new Error("File not found in storage");
        }

        // Convert blob to buffer
        const arrayBuffer = await fileBlob.arrayBuffer();
        const buffer = Buffer.from(arrayBuffer);

        await sendWithFile(
          botToken,
          userId,
          args.message_text,
          buffer,
          args.file_name || "file"
        );

        // Delete file from storage after sending
        await ctx.storage.delete(args.storage_id);
      } else {
        await sendTextOnly(botToken, userId, args.message_text);
      }
      return { success: true };
    } catch (error: any) {
      throw new Error(`Failed to send message: ${error.message}`);
    }
  },
});

// Internal action to process scheduled messages (called by cron)
export const processScheduledMessages = internalAction({
  args: {},
  handler: async (ctx) => {
    // Get pending messages
    const pendingMessages = await ctx.runQuery(
      internal.messages.getPendingMessages
    );

    const botToken = process.env.TELEGRAM_BOT_TOKEN;
    const userId = process.env.TELEGRAM_USER_ID;

    if (!botToken || !userId) {
      console.error("Telegram credentials not configured");
      return { processed: 0, errors: 0 };
    }

    let processed = 0;
    let errors = 0;

    for (const message of pendingMessages) {
      try {
        // Send the message
        if (message.storage_id) {
          // Get file from storage
          const fileBlob = await ctx.storage.get(message.storage_id);
          if (!fileBlob) {
            throw new Error("File not found in storage");
          }

          // Convert blob to buffer
          const arrayBuffer = await fileBlob.arrayBuffer();
          const buffer = Buffer.from(arrayBuffer);

          await sendWithFile(
            botToken,
            userId,
            message.message_text || message.title,
            buffer,
            message.file_name || "file"
          );

          // Delete file from storage after sending
          await ctx.storage.delete(message.storage_id);
        } else {
          await sendTextOnly(
            botToken,
            userId,
            message.message_text || message.title
          );
        }

        // Mark as sent
        await ctx.runMutation(internal.messages.markAsSent, {
          messageId: message._id,
          recurring: message.recurring,
        });

        // Add to history
        await ctx.runMutation(internal.messages.addToHistory, {
          title: message.title,
          message_text: message.message_text,
          status: "sent",
          scheduled_message_id: message._id,
        });

        processed++;
      } catch (error: any) {
        // Mark as failed
        await ctx.runMutation(internal.messages.markAsFailed, {
          messageId: message._id,
          error: error.message,
        });

        // Add to history
        await ctx.runMutation(internal.messages.addToHistory, {
          title: message.title,
          message_text: message.message_text,
          status: "failed",
          error_message: error.message,
          scheduled_message_id: message._id,
        });

        errors++;
        console.error(`Failed to send message ${message._id}:`, error.message);
      }
    }

    return { processed, errors };
  },
});

// Helper: Send text-only message
async function sendTextOnly(
  botToken: string,
  userId: string,
  text: string
): Promise<void> {
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: userId,
      text: text,
      parse_mode: "Markdown",
    }),
  });

  const result = (await response.json()) as any;
  if (!result.ok) {
    throw new Error(result.description || "Failed to send message");
  }
}

// Helper: Send message with file using multipart/form-data
async function sendWithFile(
  botToken: string,
  userId: string,
  caption: string,
  fileBuffer: Buffer,
  fileName: string
): Promise<void> {
  const url = `https://api.telegram.org/bot${botToken}/sendDocument`;

  // Create multipart form data manually
  const boundary = `----FormBoundary${Date.now()}`;
  
  const parts: Buffer[] = [];

  // Add chat_id field
  parts.push(
    Buffer.from(
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="chat_id"\r\n\r\n` +
      `${userId}\r\n`
    )
  );

  // Add caption field
  parts.push(
    Buffer.from(
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="caption"\r\n\r\n` +
      `${caption}\r\n`
    )
  );

  // Add document field with file
  parts.push(
    Buffer.from(
      `--${boundary}\r\n` +
      `Content-Disposition: form-data; name="document"; filename="${fileName}"\r\n` +
      `Content-Type: application/octet-stream\r\n\r\n`
    )
  );
  parts.push(fileBuffer);
  parts.push(Buffer.from(`\r\n`));

  // Add closing boundary
  parts.push(Buffer.from(`--${boundary}--\r\n`));

  // Combine all parts
  const body = Buffer.concat(parts);

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": `multipart/form-data; boundary=${boundary}`,
      "Content-Length": body.length.toString(),
    },
    body: body,
  });

  const result = (await response.json()) as any;
  if (!result.ok) {
    throw new Error(result.description || "Failed to send document");
  }
}
