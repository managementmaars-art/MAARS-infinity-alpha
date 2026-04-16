import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Scheduled messages table
  scheduled_messages: defineTable({
    title: v.string(),
    message_text: v.optional(v.string()),
    storage_id: v.optional(v.id("_storage")), // Convex Storage ID for file
    file_name: v.optional(v.string()), // Original filename
    scheduled_time: v.number(), // Unix timestamp in milliseconds
    recurring: v.optional(v.string()), // e.g., "daily", "weekly", "every 2 hours"
    status: v.string(), // "pending", "sent", "failed", "cancelled"
    created_at: v.number(),
    last_sent_at: v.optional(v.number()),
    error_message: v.optional(v.string()),
  })
    .index("by_status", ["status"])
    .index("by_scheduled_time", ["scheduled_time"])
    .index("by_status_and_time", ["status", "scheduled_time"]),

  // Message history table
  message_history: defineTable({
    title: v.string(),
    message_text: v.optional(v.string()),
    sent_at: v.number(),
    status: v.string(), // "sent", "failed"
    error_message: v.optional(v.string()),
    scheduled_message_id: v.optional(v.id("scheduled_messages")),
  })
    .index("by_sent_at", ["sent_at"])
    .index("by_status", ["status"]),
});
