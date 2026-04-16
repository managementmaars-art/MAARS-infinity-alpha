import { formatDate } from "./utils.js";
import { PromptBuilder, getPhrase, getLanguageDisplayName } from "./prompts.js";

export function getReviewWorkspaceRoot(config, backend, targetInfo) {
  return (backend.kind === "git" ? targetInfo.repoRootPath : targetInfo.workingCopyPath) || config.baseDir;
}

export function buildPrompt(config, backend, targetInfo, details, reviewDiffPayload) {
  const builder = new PromptBuilder(config, backend, targetInfo, details);
  return builder.build(reviewDiffPayload);
}

export function formatTokenUsage(tokenUsage) {
  const sourceLabel = tokenUsage.source === "reviewer" ? "reviewer reported" : "estimated (~4 chars/token)";
  return [
    `- Input Tokens: \`${tokenUsage.inputTokens}\``,
    `- Output Tokens: \`${tokenUsage.outputTokens}\``,
    `- Total Tokens: \`${tokenUsage.totalTokens}\``,
    `- Token Source: \`${sourceLabel}\``
  ].join("\n");
}

export function formatDiffHandling(diffPayload, label) {
  return [
    `- ${label} Original Lines: \`${diffPayload.originalLineCount}\``,
    `- ${label} Original Chars: \`${diffPayload.originalCharCount}\``,
    `- ${label} Included Lines: \`${diffPayload.outputLineCount}\``,
    `- ${label} Included Chars: \`${diffPayload.outputCharCount}\``,
    `- ${label} Truncated: \`${diffPayload.wasTruncated ? "yes" : "no"}\``
  ].join("\n");
}

export function formatChangedPaths(changedPaths) {
  if (changedPaths.length === 0) {
    return "_No changed files captured._";
  }

  return changedPaths
    .map((item) => {
      const renameSuffix = item.previousPath ? ` (from ${item.previousPath})` : "";
      return `- \`${item.action}\` ${item.relativePath}${renameSuffix}`;
    })
    .join("\n");
}

export function formatChangeList(backend, changeIds) {
  return changeIds.map((changeId) => backend.formatChangeId(changeId)).join(", ");
}

export function shouldWriteFormat(config, format) {
  return Array.isArray(config.outputFormats) && config.outputFormats.includes(format);
}

export function buildReport(config, backend, targetInfo, details, diffPayloads, reviewer, reviewerResult, tokenUsage) {
  const lang = config.resolvedLang || "en";
  const lines = [
    `# ${backend.displayName} Review Report: ${details.displayId}`,
    "",
    `- ${getPhrase("repoType", lang)}: \`${backend.displayName}\``,
    `- Target: \`${targetInfo.targetDisplay || config.target}\``,
    `- ${getPhrase("changeId", lang)}: \`${details.displayId}\``,
    `- ${getPhrase("author", lang)}: \`${details.author}\``,
    `- ${getPhrase("date", lang)}: \`${formatDate(details.date)}\``,
    `- Generated At: \`${formatDate(new Date())}\``,
    `- Reviewer: \`${reviewer.displayName}\``,
    "",
    "## Token Usage",
    "",
    formatTokenUsage(tokenUsage),
    "",
    `## ${getPhrase("changedFiles", lang)}`,
    "",
    formatChangedPaths(details.changedPaths),
    "",
    `## ${getPhrase("commitMessage", lang)}`,
    "",
    details.message ? "```text\n" + details.message + "\n```" : "_Empty_",
    "",
    "## Diff",
    "",
    "```diff",
    diffPayloads.report.text.trim() || "(empty diff)",
    "```",
    "",
    `## ${reviewer.responseSectionTitle}`,
    "",
    reviewerResult.message?.trim() ? reviewerResult.message.trim() : reviewer.emptyResponseText
  ];

  return `${lines.join("\n")}\n`;
}

export function buildJsonReport(config, backend, targetInfo, details, diffPayloads, reviewer, reviewerResult, tokenUsage) {
  return {
    repositoryType: backend.displayName,
    target: targetInfo.targetDisplay || config.target,
    changeId: details.displayId,
    author: details.author,
    commitDate: formatDate(details.date),
    generatedAt: formatDate(new Date()),
    reviewer: {
      name: reviewer.displayName,
      exitCode: reviewerResult.code,
      timedOut: Boolean(reviewerResult.timedOut)
    },
    tokenUsage: {
      inputTokens: tokenUsage.inputTokens,
      outputTokens: tokenUsage.outputTokens,
      totalTokens: tokenUsage.totalTokens,
      source: tokenUsage.source
    },
    changedFiles: details.changedPaths.map((item) => ({
      action: item.action,
      path: item.relativePath,
      previousPath: item.previousPath || null
    })),
    commitMessage: details.message || "",
    reviewContext: buildPrompt(config, backend, targetInfo, details, diffPayloads.review),
    diffHandling: {
      reviewerInput: {
        originalLines: diffPayloads.review.originalLineCount,
        originalChars: diffPayloads.review.originalCharCount,
        includedLines: diffPayloads.review.outputLineCount,
        includedChars: diffPayloads.review.outputCharCount,
        truncated: diffPayloads.review.wasTruncated
      },
      reportDiff: {
        originalLines: diffPayloads.report.originalLineCount,
        originalChars: diffPayloads.report.originalCharCount,
        includedLines: diffPayloads.report.outputLineCount,
        includedChars: diffPayloads.report.outputCharCount,
        truncated: diffPayloads.report.wasTruncated
      }
    },
    diff: diffPayloads.report.text.trim(),
    reviewerDiagnostics: reviewerResult.stderr?.trim() || "",
    reviewerResponse: reviewerResult.message?.trim() ? reviewerResult.message.trim() : reviewer.emptyResponseText
  };
}
