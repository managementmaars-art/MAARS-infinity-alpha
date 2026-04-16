import { countLines } from "./utils.js";

export const DIFF_LIMITS = {
  review: {
    maxLines: 4000,
    maxChars: 120000
  },
  report: {
    maxLines: 1500,
    maxChars: 40000
  },
  tailLines: 200
};

export function trimBlockToChars(text, maxChars, keepTail = false) {
  if (text.length <= maxChars) {
    return text;
  }

  if (maxChars <= 3) {
    return ".".repeat(Math.max(maxChars, 0));
  }

  return keepTail ? `...${text.slice(-(maxChars - 3))}` : `${text.slice(0, maxChars - 3)}...`;
}

export function truncateDiffText(diffText, maxLines, maxChars, tailLines, purposeLabel) {
  const normalizedDiff = diffText.replace(/\r\n/g, "\n");
  const originalLineCount = countLines(normalizedDiff);
  const originalCharCount = normalizedDiff.length;

  if (originalLineCount <= maxLines && originalCharCount <= maxChars) {
    return {
      text: diffText,
      wasTruncated: false,
      originalLineCount,
      originalCharCount,
      outputLineCount: originalLineCount,
      outputCharCount: originalCharCount
    };
  }

  const lines = normalizedDiff.split("\n");
  const safeTailLines = Math.min(Math.max(tailLines, 0), Math.max(maxLines - 2, 0));
  const headLineCount = Math.max(maxLines - safeTailLines - 1, 1);
  let headBlock = lines.slice(0, headLineCount).join("\n");
  let tailBlock = safeTailLines > 0 ? lines.slice(-safeTailLines).join("\n") : "";
  const omittedLineCount = Math.max(originalLineCount - headLineCount - safeTailLines, 0);
  const markerBlock = [
    `... diff truncated for ${purposeLabel} ...`,
    `original lines: ${originalLineCount}, original chars: ${originalCharCount}`,
    `omitted lines: ${omittedLineCount}`
  ].join("\n");

  let truncatedText = [headBlock, markerBlock, tailBlock].filter(Boolean).join("\n");

  if (truncatedText.length > maxChars) {
    const reservedChars = markerBlock.length + (tailBlock ? 2 : 1);
    const remainingChars = Math.max(maxChars - reservedChars, 0);
    const headBudget = tailBlock ? Math.floor(remainingChars * 0.7) : remainingChars;
    const tailBudget = tailBlock ? Math.max(remainingChars - headBudget, 0) : 0;
    headBlock = trimBlockToChars(headBlock, headBudget, false);
    tailBlock = trimBlockToChars(tailBlock, tailBudget, true);
    truncatedText = [headBlock, markerBlock, tailBlock].filter(Boolean).join("\n");
  }

  return {
    text: truncatedText,
    wasTruncated: true,
    originalLineCount,
    originalCharCount,
    outputLineCount: countLines(truncatedText),
    outputCharCount: truncatedText.length
  };
}

export function prepareDiffPayloads(config, diffText) {
  return {
    review: truncateDiffText(
      diffText,
      DIFF_LIMITS.review.maxLines,
      DIFF_LIMITS.review.maxChars,
      DIFF_LIMITS.tailLines,
      "reviewer input"
    ),
    report: truncateDiffText(
      diffText,
      DIFF_LIMITS.report.maxLines,
      DIFF_LIMITS.report.maxChars,
      Math.min(DIFF_LIMITS.tailLines, DIFF_LIMITS.report.maxLines),
      "report output"
    )
  };
}

