"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Sparkles } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useUpdateTeam } from "@/hooks/use-teams";

/**
 * Team Personalization Section Component
 * 
 * Team settings for configuring AI email personalization.
 * - About Us description for AI context
 * - AI model selection
 * - Custom instructions
 * - Preview mode toggle
 */

interface TeamPersonalizationSectionProps {
  team: {
    id: string;
    personalizationAboutUs: string | null;
    personalizationModelId: string | null;
    personalizationInstructions: string | null;
    personalizationPreviewEnabled: boolean;
  };
}

const AI_MODELS = [
  { value: "google/gemini-3-flash", label: "Google Gemini 3 Flash (Recommended)" },
  { value: "anthropic/claude-sonnet-4.5", label: "Anthropic Claude Sonnet 4.5" },
  { value: "anthropic/claude-opus-4.5", label: "Anthropic Claude Opus 4.5" },
] as const;

const formSchema = z.object({
  personalizationAboutUs: z.string().max(2000, "Maximum 2000 characters").optional(),
  personalizationModelId: z.enum([
    "google/gemini-3-flash",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-opus-4.5"
  ]).optional(),
  personalizationInstructions: z.string().max(2000, "Maximum 2000 characters").optional(),
  personalizationPreviewEnabled: z.boolean().optional(),
});

type FormValues = z.infer<typeof formSchema>;

export function TeamPersonalizationSection({ team }: TeamPersonalizationSectionProps) {
  const updateTeam = useUpdateTeam(team.id);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      personalizationAboutUs: team.personalizationAboutUs || "",
      personalizationModelId: (team.personalizationModelId as FormValues["personalizationModelId"]) || "google/gemini-3-flash",
      personalizationInstructions: team.personalizationInstructions || "",
      personalizationPreviewEnabled: team.personalizationPreviewEnabled,
    },
  });

  async function onSubmit(data: FormValues) {
    try {
      await updateTeam.mutateAsync({
        personalizationAboutUs: data.personalizationAboutUs || null,
        personalizationModelId: data.personalizationModelId || null,
        personalizationInstructions: data.personalizationInstructions || null,
        personalizationPreviewEnabled: data.personalizationPreviewEnabled,
      });
      // Reset form state to mark current values as "saved"
      form.reset(data);
      toast.success("Personalization settings updated");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to update settings"
      );
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          AI Personalization
        </CardTitle>
        <CardDescription>
          Configure AI-powered email personalization with {"{{ }}"} tags
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="personalizationAboutUs"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>About Your Team</FormLabel>
                  <FormDescription>
                    Help AI understand your team and what you do. This context improves personalization quality.
                  </FormDescription>
                  <FormControl>
                    <Textarea
                      placeholder="We are a marketing agency that helps brands connect with creators..."
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="personalizationModelId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>AI Model</FormLabel>
                  <FormDescription>
                    Select the AI model for generating personalized content
                  </FormDescription>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a model" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {AI_MODELS.map((model) => (
                        <SelectItem key={model.value} value={model.value}>
                          {model.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="personalizationInstructions"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Custom Instructions (Optional)</FormLabel>
                  <FormDescription>
                    Additional instructions for the AI when personalizing emails
                  </FormDescription>
                  <FormControl>
                    <Textarea
                      placeholder="Keep the tone professional but friendly. Avoid using exclamation marks..."
                      className="min-h-[80px]"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="personalizationPreviewEnabled"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Preview Mode</FormLabel>
                    <FormDescription>
                      Show a preview modal to review AI-personalized emails before sending
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <Button
              type="submit"
              disabled={updateTeam.isPending || !form.formState.isDirty}
            >
              {updateTeam.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
