import { v } from "convex/values";
import { mutation, query, internalMutation, internalQuery } from "./_generated/server";

// Upload a file to Convex Storage
export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx) => {
    // Generate a short-lived upload URL
    return await ctx.storage.generateUploadUrl();
  },
});

// Schedule a new message
export const scheduleMessage = mutation({
  args: {
    title: v.string(),
    message_text: v.optional(v.string()),
    storage_id: v.optional(v.id("_storage")), // Convex Storage ID
    file_name: v.optional(v.string()), // Original filename
    scheduled_time: v.number(),
    recurring: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const messageId = await ctx.db.insert("scheduled_messages", {
      title: args.title,
      message_text: args.message_text,
      storage_id: args.storage_id,
      file_name: args.file_name,
      scheduled_time: args.scheduled_time,
      recurring: args.recurring,
      status: "pending",
      created_at: Date.now(),
    });
    return messageId;
  },
});

// List all scheduled messages
export const listScheduled = query({
  args: {},
  handler: async (ctx) => {
    const messages = await ctx.db
      .query("scheduled_messages")
      .filter((q) => q.neq(q.field("status"), "cancelled"))
      .order("desc")
      .collect();
    return messages;
  },
});

// Get pending messages that are due (internal only - called by cron)
export const getPendingMessages = internalQuery({
  args: {},
  handler: async (ctx) => {
    const now = Date.now();
    const messages = await ctx.db
      .query("scheduled_messages")
      .withIndex("by_status_and_time", (q) => 
        q.eq("status", "pending")
      )
      .filter((q) => q.lte(q.field("scheduled_time"), now))
      .collect();
    return messages;
  },
});

// Cancel a scheduled message
export const cancelMessage = mutation({
  args: {
    messageId: v.id("scheduled_messages"),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.messageId, {
      status: "cancelled",
    });
    return { success: true };
  },
});

// Mark message as sent (internal only)
export const markAsSent = internalMutation({
  args: {
    messageId: v.id("scheduled_messages"),
    recurring: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const message = await ctx.db.get(args.messageId);
    if (!message) return;

    // If recurring, schedule next occurrence
    if (args.recurring) {
      const nextTime = calculateNextOccurrence(
        message.scheduled_time,
        args.recurring
      );
      
      await ctx.db.patch(args.messageId, {
        scheduled_time: nextTime,
        last_sent_at: Date.now(),
      });
    } else {
      // Mark as sent
      await ctx.db.patch(args.messageId, {
        status: "sent",
        last_sent_at: Date.now(),
      });
    }
  },
});

// Mark message as failed (internal only)
export const markAsFailed = internalMutation({
  args: {
    messageId: v.id("scheduled_messages"),
    error: v.string(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.messageId, {
      status: "failed",
      error_message: args.error,
    });
  },
});

// Add to message history (internal only)
export const addToHistory = internalMutation({
  args: {
    title: v.string(),
    message_text: v.optional(v.string()),
    status: v.string(),
    error_message: v.optional(v.string()),
    scheduled_message_id: v.optional(v.id("scheduled_messages")),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("message_history", {
      title: args.title,
      message_text: args.message_text,
      sent_at: Date.now(),
      status: args.status,
      error_message: args.error_message,
      scheduled_message_id: args.scheduled_message_id,
    });
  },
});

// View message history
export const viewHistory = query({
  args: {
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit || 50;
    const history = await ctx.db
      .query("message_history")
      .order("desc")
      .take(limit);
    return history;
  },
});

// Helper function to calculate next occurrence for recurring messages
function calculateNextOccurrence(lastTime: number, recurring: string): number {
  const intervals: { [key: string]: number } = {
    "every minute": 60 * 1000,
    "every 5 minutes": 5 * 60 * 1000,
    "every 30 minutes": 30 * 60 * 1000,
    "every hour": 60 * 60 * 1000,
    "every 2 hours": 2 * 60 * 60 * 1000,
    "every day": 24 * 60 * 60 * 1000,
    "daily": 24 * 60 * 60 * 1000,
    "every week": 7 * 24 * 60 * 60 * 1000,
    "weekly": 7 * 24 * 60 * 60 * 1000,
  };

  // Check for simple intervals
  const interval = intervals[recurring.toLowerCase()];
  if (interval) {
    return lastTime + interval;
  }

  // For more complex recurring (handled by chrono-node in client)
  // Just add 24 hours as fallback
  return lastTime + 24 * 60 * 60 * 1000;
}
