import fs from "node:fs/promises";
import path from "node:path";
import { runCommand } from "./shell.js";

const GIT_COMMAND = "git";
const COMMAND_ENCODING = "utf8";

function toPosixPath(filePath) {
  return filePath.split(path.sep).join("/");
}

function splitLines(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function buildPathArgs(targetInfo) {
  return targetInfo.targetPathspec ? ["--", targetInfo.targetPathspec] : [];
}

async function statPath(targetPath) {
  try {
    return await fs.stat(targetPath);
  } catch {
    return null;
  }
}

async function runGit(config, args, options = {}) {
  return await runCommand(GIT_COMMAND, args, {
    encoding: COMMAND_ENCODING,
    debug: config.debug,
    ...options
  });
}

export async function getTargetInfo(config) {
  const requestedTargetPath = path.resolve(config.baseDir, config.target);
  const targetStat = await statPath(requestedTargetPath);

  if (!targetStat) {
    throw new Error(`Git target path does not exist: ${requestedTargetPath}`);
  }

  const lookupCwd = targetStat.isDirectory() ? requestedTargetPath : path.dirname(requestedTargetPath);
  const topLevelResult = await runGit(config, ["rev-parse", "--show-toplevel"], {
    cwd: lookupCwd,
    trim: true,
    allowFailure: true
  });

  if (topLevelResult.code !== 0) {
    throw new Error(`Git target path is not within a Git repository: ${requestedTargetPath}`);
  }

  const repoRootPath = path.resolve(topLevelResult.stdout);
  const relativeTargetPath = toPosixPath(path.relative(repoRootPath, requestedTargetPath));
  const branchResult = await runGit(config, ["rev-parse", "--abbrev-ref", "HEAD"], {
    cwd: repoRootPath,
    trim: true,
    allowFailure: true
  });

  return {
    repoRootPath,
    requestedTargetPath,
    targetDisplay: requestedTargetPath,
    targetPathspec: relativeTargetPath ? relativeTargetPath : "",
    branchName: branchResult.stdout || "HEAD"
  };
}

export async function getLatestCommit(config, targetInfo) {
  const result = await runGit(
    config,
    ["log", "--format=%H", "-n", "1", "HEAD", ...buildPathArgs(targetInfo)],
    { cwd: targetInfo.repoRootPath, trim: true }
  );
  const latestCommit = splitLines(result.stdout)[0];

  if (!latestCommit) {
    throw new Error(`Unable to determine the latest Git commit for ${targetInfo.targetDisplay}`);
  }

  return latestCommit;
}


export async function resolveCommits(config, targetInfo, revSpec) {
  const result = await runGit(
    config,
    ["rev-list", revSpec],
    { cwd: targetInfo.repoRootPath, trim: true, allowFailure: true }
  );

  if (result.code !== 0) {
    // Attempt fallback to a single hash resolution if rev-list fails (e.g. for non-standard specs)
    const single = await runGit(config, ["rev-parse", revSpec], {
      cwd: targetInfo.repoRootPath, trim: true, allowFailure: true
    });
    if (single.code === 0) return [single.stdout.trim()];
    throw new Error(`Failed to resolve Git revision: ${revSpec}`);
  }

  return splitLines(result.stdout);
}


export async function getLatestCommitIds(config, targetInfo, limit) {
  const result = await runGit(
    config,
    ["rev-list", "-n", String(limit), "HEAD", ...buildPathArgs(targetInfo)],
    { cwd: targetInfo.repoRootPath, trim: true }
  );
  // Reverse to get chronological order (oldest to newest among the latest n)
  return splitLines(result.stdout).reverse();
}

export async function getCommitDiff(config, targetInfo, commitHash) {
  const result = await runGit(
    config,
    [
      "show",
      "--format=",
      "--find-renames",
      "--find-copies",
      "--no-ext-diff",
      commitHash,
      ...buildPathArgs(targetInfo)
    ],
    { cwd: targetInfo.repoRootPath, trim: false }
  );

  return result.stdout;
}

function parseNameStatus(stdout) {
  const entries = stdout.split("\0").filter(Boolean);
  const changedPaths = [];

  for (let index = 0; index < entries.length; index += 1) {
    const status = entries[index];

    if (!status) {
      continue;
    }

    const action = status[0];

    if (status.startsWith("R") || status.startsWith("C")) {
      const oldPath = entries[index + 1];
      const newPath = entries[index + 2];

      if (newPath) {
        changedPaths.push({
          action,
          relativePath: newPath,
          previousPath: oldPath || null
        });
      }

      index += 2;
      continue;
    }

    const filePath = entries[index + 1];

    if (filePath) {
      changedPaths.push({
        action,
        relativePath: filePath,
        previousPath: null
      });
    }

    index += 1;
  }

  return changedPaths;
}

function parseNameStatusLines(stdout) {
  return stdout
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.split("\t"))
    .map((parts) => {
      const status = (parts[0] || "M").trim();
      const action = status[0] || "M";

      if ((action === "R" || action === "C") && parts.length >= 3) {
        return {
          action,
          relativePath: parts[2],
          previousPath: parts[1] || null
        };
      }

      return {
        action,
        relativePath: parts[1] || "",
        previousPath: null
      };
    })
    .filter((item) => item.relativePath);
}

function mergeChangedPaths(...groups) {
  const merged = [];
  const seen = new Set();

  for (const group of groups) {
    for (const item of group) {
      const key = `${item.action}|${item.relativePath}|${item.previousPath || ""}`;
      if (seen.has(key)) continue;
      seen.add(key);
      merged.push(item);
    }
  }

  return merged;
}

export async function getCommitDetails(config, targetInfo, commitHash) {
  const metaResult = await runGit(
    config,
    ["show", "--no-patch", "--format=%H%x00%an%x00%aI%x00%B", commitHash],
    { cwd: targetInfo.repoRootPath, trim: false }
  );
  const [hash = "", author = "", date = "", ...messageParts] = metaResult.stdout.split("\0");
  const message = messageParts.join("\0").trim();
  const changedFilesResult = await runGit(
    config,
    [
      "diff-tree",
      "--no-commit-id",
      "--name-status",
      "-r",
      "--root",
      "-z",
      "-M",
      "-C",
      commitHash,
      ...buildPathArgs(targetInfo)
    ],
    { cwd: targetInfo.repoRootPath, trim: false }
  );

  return {
    commitHash: hash.trim() || commitHash,
    author: author.trim() || "unknown",
    date: date.trim(),
    message,
    changedPaths: parseNameStatus(changedFilesResult.stdout)
  };
}

export async function getUncommittedDiff(config, targetInfo) {
  const unstaged = await runGit(
    config,
    [
      "diff",
      "--find-renames",
      "--find-copies",
      "--no-ext-diff",
      ...buildPathArgs(targetInfo)
    ],
    { cwd: targetInfo.repoRootPath, trim: false }
  );
  const staged = await runGit(
    config,
    [
      "diff",
      "--cached",
      "--find-renames",
      "--find-copies",
      "--no-ext-diff",
      ...buildPathArgs(targetInfo)
    ],
    { cwd: targetInfo.repoRootPath, trim: false }
  );

  const sections = [];
  if (unstaged.stdout.trim()) {
    sections.push("# Unstaged changes", unstaged.stdout.trimEnd());
  }
  if (staged.stdout.trim()) {
    sections.push("# Staged changes", staged.stdout.trimEnd());
  }

  return sections.join("\n\n");
}

export async function getUncommittedDetails(config, targetInfo) {
  const unstagedFiles = await runGit(
    config,
    ["diff", "--name-status", "-M", "-C", ...buildPathArgs(targetInfo)],
    { cwd: targetInfo.repoRootPath, trim: false }
  );
  const stagedFiles = await runGit(
    config,
    ["diff", "--cached", "--name-status", "-M", "-C", ...buildPathArgs(targetInfo)],
    { cwd: targetInfo.repoRootPath, trim: false }
  );

  const unstagedChanged = parseNameStatusLines(unstagedFiles.stdout);
  const stagedChanged = parseNameStatusLines(stagedFiles.stdout);

  return {
    commitHash: "UNCOMMITTED",
    author: "working-tree",
    date: new Date().toISOString(),
    message: "Uncommitted changes (staged + unstaged).",
    changedPaths: mergeChangedPaths(unstagedChanged, stagedChanged)
  };
}
