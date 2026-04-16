import path from "node:path";
import { XMLParser } from "fast-xml-parser";
import { runCommand } from "./shell.js";

const SVN_COMMAND = "svn";
const COMMAND_ENCODING = "utf8";

const xmlParser = new XMLParser({
  ignoreAttributes: false,
  attributeNamePrefix: ""
});

function asArray(value) {
  if (!value) {
    return [];
  }

  return Array.isArray(value) ? value : [value];
}

function normalizeRepoPath(repoPath) {
  if (!repoPath) {
    return "/";
  }

  return repoPath.startsWith("/") ? repoPath : `/${repoPath}`;
}

function repoPathFromUrl(rootUrl, url) {
  if (!url.startsWith(rootUrl)) {
    throw new Error(`URL ${url} is not under repository root ${rootUrl}`);
  }

  const suffix = url.slice(rootUrl.length) || "/";
  return normalizeRepoPath(suffix);
}

export async function getTargetInfo(config) {
  const result = await runCommand(SVN_COMMAND, ["info", "--xml", config.target], {
    encoding: COMMAND_ENCODING,
    trim: true,
    debug: config.debug
  });
  const parsed = xmlParser.parse(result.stdout);
  const entry = parsed?.info?.entry;

  if (!entry?.url || !entry?.repository?.root) {
    throw new Error(`Unable to read svn info for target ${config.target}`);
  }

  const repoRootUrl = entry.repository.root;
  const targetUrl = entry.url;
  const targetRepoPath = repoPathFromUrl(repoRootUrl, targetUrl);

  return {
    repoRootUrl,
    targetUrl,
    targetRepoPath,
    targetDisplay: config.target,
    workingCopyPath:
      entry["wc-info"]?.["wcroot-abspath"] || (path.isAbsolute(config.target) ? config.target : null)
  };
}

function getRemoteTarget(targetInfo, config) {
  return targetInfo?.targetUrl || config.target;
}

export async function getLatestRevision(config, targetInfo) {
  const result = await runCommand(
    SVN_COMMAND,
    ["log", "--xml", "-r", "HEAD:1", "-l", "1", getRemoteTarget(targetInfo, config)],
    { encoding: COMMAND_ENCODING, trim: true, debug: config.debug }
  );
  const parsed = xmlParser.parse(result.stdout);
  const entry = parsed?.log?.logentry;
  const revision = Number(entry?.revision);

  if (!Number.isInteger(revision)) {
    throw new Error(`Unable to determine latest SVN revision for ${config.target}`);
  }

  return revision;
}


export async function getLatestRevisionIds(config, targetInfo, limit) {
  const result = await runCommand(
    SVN_COMMAND,
    ["log", "--xml", "--quiet", "-l", String(limit), "-r", "HEAD:1", getRemoteTarget(targetInfo, config)],
    { encoding: COMMAND_ENCODING, trim: true, debug: config.debug }
  );
  const parsed = xmlParser.parse(result.stdout);

  return asArray(parsed?.log?.logentry)
    .map((entry) => Number(entry?.revision))
    .filter((revision) => Number.isInteger(revision))
    .sort((left, right) => left - right);
}

export async function getRevisionDiff(config, revision) {
  const result = await runCommand(
    SVN_COMMAND,
    ["diff", "--git", "--internal-diff", "--ignore-properties", "-c", String(revision), config.target],
    { encoding: COMMAND_ENCODING, trim: false, debug: config.debug }
  );

  return result.stdout;
}

function isPathInsideTarget(targetRepoPath, repoPath) {
  if (targetRepoPath === "/") {
    return true;
  }

  return repoPath === targetRepoPath || repoPath.startsWith(`${targetRepoPath}/`);
}

function toRelativePath(targetRepoPath, repoPath) {
  if (repoPath === targetRepoPath) {
    return path.posix.basename(repoPath);
  }

  if (targetRepoPath === "/") {
    return repoPath.replace(/^\/+/, "");
  }

  return repoPath.slice(targetRepoPath.length).replace(/^\/+/, "");
}

function parseSvnStatus(statusText) {
  return statusText
    .split(/\r?\n/)
    .map((line) => line.replace(/\r$/, ""))
    .filter(Boolean)
    .map((line) => {
      const action = (line[0] || " ").trim();
      const relativePath = line.length > 8 ? line.slice(8).trim() : "";
      return {
        action,
        relativePath,
        previousPath: null
      };
    })
    .filter((item) => item.relativePath)
    .filter((item) => ["A", "D", "M", "R"].includes(item.action));
}

export async function getRevisionDetails(config, targetInfo, revision) {
  const result = await runCommand(
    SVN_COMMAND,
    ["log", "--xml", "-v", "-c", String(revision), getRemoteTarget(targetInfo, config)],
    { encoding: COMMAND_ENCODING, trim: true, debug: config.debug }
  );
  const parsed = xmlParser.parse(result.stdout);
  const entry = parsed?.log?.logentry;

  if (!entry?.revision) {
    throw new Error(`Unable to load SVN log for revision r${revision}`);
  }

  const changedPaths = asArray(entry.paths?.path)
    .map((item) => {
      const repoPath = normalizeRepoPath(item["#text"] || item);
      return {
        action: item.action || "M",
        kind: item.kind || "unknown",
        repoPath,
        relativePath: toRelativePath(targetInfo.targetRepoPath, repoPath),
        copyFromPath: item["copyfrom-path"] ? normalizeRepoPath(item["copyfrom-path"]) : null,
        copyFromRev: item["copyfrom-rev"] ? Number(item["copyfrom-rev"]) : null
      };
    })
    .filter((item) => isPathInsideTarget(targetInfo.targetRepoPath, item.repoPath))
    .filter((item) => item.relativePath.length > 0)
    .filter((item) => item.kind === "file" || item.kind === "unknown");

  return {
    revision: Number(entry.revision),
    author: entry.author || "unknown",
    date: entry.date || "",
    message: entry.msg || "",
    changedPaths
  };
}

export async function getUncommittedDiff(config, targetInfo) {
  if (!targetInfo.workingCopyPath) {
    throw new Error("SVN --uncommitted requires a working copy path target.");
  }

  const result = await runCommand(
    SVN_COMMAND,
    ["diff", "--git", "--internal-diff", "--ignore-properties", config.target],
    { encoding: COMMAND_ENCODING, trim: false, debug: config.debug }
  );

  return result.stdout;
}

export async function getUncommittedDetails(config, targetInfo) {
  if (!targetInfo.workingCopyPath) {
    throw new Error("SVN --uncommitted requires a working copy path target.");
  }

  const statusResult = await runCommand(
    SVN_COMMAND,
    ["status", config.target],
    { encoding: COMMAND_ENCODING, trim: false, debug: config.debug }
  );

  return {
    revision: "UNCOMMITTED",
    author: "working-copy",
    date: new Date().toISOString(),
    message: "Uncommitted changes in working copy.",
    changedPaths: parseSvnStatus(statusResult.stdout)
  };
}
