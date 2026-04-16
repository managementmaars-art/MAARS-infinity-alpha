import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();

// Check for scheduled messages every minute
crons.interval(
  "process-scheduled-messages",
  { minutes: 1 },
  internal.telegram.processScheduledMessages
);

export default crons;
