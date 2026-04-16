function clampProgress(value) {
  if (!Number.isFinite(value)) {
    return 0;
  }

  return Math.max(0, Math.min(1, value));
}

function formatStatusLine(label, progress, stage) {
  const pct = `${Math.round(progress * 100)}`.padStart(3, " ");
  return `[progress] ${pct}% ${label}${stage ? ` | ${stage}` : ""}`;
}

export function createProgressReporter(label, options = {}) {
  const stream = options.stream || process.stdout;
  let lastStatusLine = "";

  function writeLine(message) {
    stream.write(`${message}\n`);
  }

  return {
    update(progress, stage = "") {
      const line = formatStatusLine(label, clampProgress(progress), stage);

      if (line === lastStatusLine) {
        return;
      }

      lastStatusLine = line;
      writeLine(line);
    },

    finish(status, message) {
      const prefix = status === "fail" ? "[fail]" : "[done]";
      writeLine(`${prefix} ${message || label}`);
    }
  };
}
