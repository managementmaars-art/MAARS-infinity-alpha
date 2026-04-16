/**
 * Email Personalization Types
 * 
 * Types and constants for AI-powered email personalization using {{ tags }}.
 */

export interface PersonalizationContext {
  // Time context
  currentTime: Date;
  timezone: string;

  // Sender context
  senderName: string;
  senderEmail: string;
  teamName: string;
  aboutUs: string | null;

  // Model configuration
  modelId: string; // e.g., "google/gemini-3-flash"
  customInstructions: string | null; // Custom instructions from team settings

  // Recipient context (adjust based on your entity)
  creator: {
    id: string;
    name: string | null;
    email: string | null;
    // Social handles
    tiktokHandle?: string | null;
    instagramHandle?: string | null;
    youtubeHandle?: string | null;
    twitterHandle?: string | null;
    linkedinUrl?: string | null;
    // Additional context
    notes?: string | null;
    type?: string | null;
    geo?: string | null;
    followerCount?: number | null;
    medianViews?: number | null;
  };
  // Platform metrics for richer context
  platformMetrics?: Array<{
    platform: string;
    followerCount: number | null;
    medianViews: number | null;
    bio: string | null;
  }>;
}

export interface PersonalizationInput {
  subject: string;
  body: string;
  context: PersonalizationContext;
}

export type PersonalizationResult =
  | {
      success: true;
      subject: string;
      message: string;
      explanation: string;
    }
  | {
      success: false;
      error: string;
    };

/**
 * Available personalization tags that users can insert into emails.
 * Each tag is replaced by AI with contextually appropriate content.
 */
export const AVAILABLE_TAGS = [
  { 
    tag: "name", 
    label: "Recipient's Name", 
    description: "The recipient's name" 
  },
  {
    tag: "time_based_greeting",
    label: "Day-based Greeting",
    description: "Smart greeting based on day of week (e.g., 'Happy Friday!', 'Hope your week is going well!')",
  },
  {
    tag: "compliment",
    label: "Personalized Compliment",
    description: "A genuine compliment about their work/content",
  },
  {
    tag: "content_fit_pitch",
    label: "Content Fit Pitch",
    description: "Why a collaboration/partnership makes sense for them",
  },
  {
    tag: "reply_cta",
    label: "Reply CTA",
    description: "Call to action encouraging them to reply",
  },
  {
    tag: "user_name",
    label: "Your Name",
    description: "The sender's name",
  },
] as const;

export type AvailableTag = typeof AVAILABLE_TAGS[number]["tag"];
