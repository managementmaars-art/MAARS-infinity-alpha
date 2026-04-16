export function estimateTokenCount(text) {
  if (!text) {
    return 0;
  }

  return Math.ceil(text.length / 4);
}

export function parseTokenUsage(stderr) {
  if (!stderr) {
    return null;
  }

  const patterns = [
    /input[_ ]tokens?\s*[:=]\s*(\d+)/i,
    /output[_ ]tokens?\s*[:=]\s*(\d+)/i,
    /total[_ ]tokens?\s*[:=]\s*(\d+)/i
  ];

  const inputMatch = stderr.match(patterns[0]);
  const outputMatch = stderr.match(patterns[1]);
  const totalMatch = stderr.match(patterns[2]);

  if (!inputMatch && !outputMatch && !totalMatch) {
    return null;
  }

  const inputTokens = inputMatch ? Number(inputMatch[1]) : 0;
  const outputTokens = outputMatch ? Number(outputMatch[1]) : 0;
  const totalTokens = totalMatch ? Number(totalMatch[1]) : inputTokens + outputTokens;

  return { inputTokens, outputTokens, totalTokens };
}

function normalizeUsageObject(usage) {
  if (!usage || typeof usage !== "object") {
    return null;
  }

  const inputTokens = Number(usage.inputTokens || 0);
  const outputTokens = Number(usage.outputTokens || 0);
  const totalTokens = Number(usage.totalTokens || (inputTokens + outputTokens));

  if (totalTokens <= 0 && inputTokens <= 0 && outputTokens <= 0) {
    return null;
  }

  return { inputTokens, outputTokens, totalTokens };
}

export function resolveTokenUsage(reviewerName, usage, stderr, promptText, diffText, responseText) {
  const normalizedUsage = normalizeUsageObject(usage);

  if (normalizedUsage) {
    return { ...normalizedUsage, source: "reviewer" };
  }

  const parsed = parseTokenUsage(stderr);

  if (parsed && parsed.totalTokens > 0) {
    return { ...parsed, source: "reviewer" };
  }

  const inputTokens = estimateTokenCount((promptText || "") + (diffText || ""));
  const outputTokens = estimateTokenCount(responseText || "");

  return {
    inputTokens,
    outputTokens,
    totalTokens: inputTokens + outputTokens,
    source: "estimate"
  };
}
