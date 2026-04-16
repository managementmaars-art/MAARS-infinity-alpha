import path from "node:path";
import * as gitClient from "./git-client.js";
import * as svnClient from "./svn-client.js";
import { pathExists, getTimestampPrefix } from "./utils.js";

function isLikelyUrl(value) {
  return /^[a-z][a-z0-9+.-]*:\/\//i.test(value);
}

function createSvnBackend() {
  return {
    kind: "svn",
    displayName: "SVN",
    changeName: "revision",
    formatChangeId(revision) {
      if (revision === "UNCOMMITTED") return "uncommitted";
      return `r${revision}`;
    },
    getReportFileName(revision) {
      if (revision === "UNCOMMITTED") {
        return `${getTimestampPrefix()}-svn-uncommitted.md`;
      }
      return `${getTimestampPrefix()}-svn-r${revision}.md`;
    },

    async resolveChangeIds(config, targetInfo, revString) {
      if (!revString) return [];
      return String(revString).split(',').map(s => s.trim()).filter(Boolean);
    },
    async getTargetInfo(config) {
      return await svnClient.getTargetInfo(config);
    },
    async getLatestChangeId(config, targetInfo) {
      return await svnClient.getLatestRevision(config, targetInfo);
    },
    async getLatestChangeIds(config, targetInfo, limit) {
      return await svnClient.getLatestRevisionIds(config, targetInfo, limit);
    },
    async getChangeDiff(config, targetInfo, revision) {
      if (revision === "UNCOMMITTED") {
        return await svnClient.getUncommittedDiff(config, targetInfo);
      }
      return await svnClient.getRevisionDiff(config, revision);
    },
    async getChangeDetails(config, targetInfo, revision) {
      if (revision === "UNCOMMITTED") {
        const details = await svnClient.getUncommittedDetails(config, targetInfo);

        return {
          id: "UNCOMMITTED",
          displayId: "uncommitted",
          author: details.author,
          date: details.date,
          message: details.message,
          changedPaths: details.changedPaths
        };
      }

      const details = await svnClient.getRevisionDetails(config, targetInfo, revision);

      return {
        id: revision,
        displayId: `r${details.revision}`,
        author: details.author,
        date: details.date,
        message: details.message,
        changedPaths: details.changedPaths
      };
    }
  };
}

function createGitBackend() {
  return {
    kind: "git",
    displayName: "Git",
    changeName: "commit",
    formatChangeId(commitHash) {
      if (commitHash === "UNCOMMITTED") return "uncommitted";
      return commitHash.slice(0, 12);
    },
    getReportFileName(commitHash) {
      if (commitHash === "UNCOMMITTED") {
        return `${getTimestampPrefix()}-git-uncommitted.md`;
      }
      return `${getTimestampPrefix()}-git-${commitHash.slice(0, 12)}.md`;
    },

    async resolveChangeIds(config, targetInfo, revString) {
      if (!revString) return [];
      const specs = String(revString).split(',').map(s => s.trim()).filter(Boolean);
      const allHashes = [];
      for (const spec of specs) {
        const hashes = await gitClient.resolveCommits(config, targetInfo, spec);
        allHashes.push(...hashes);
      }
      return [...new Set(allHashes)];
    },
    async getTargetInfo(config) {
      return await gitClient.getTargetInfo(config);
    },
    async getLatestChangeId(config, targetInfo) {
      return await gitClient.getLatestCommit(config, targetInfo);
    },
    async getLatestChangeIds(config, targetInfo, limit) {
      return await gitClient.getLatestCommitIds(config, targetInfo, limit);
    },
    async getChangeDiff(config, targetInfo, commitHash) {
      if (commitHash === "UNCOMMITTED") {
        return await gitClient.getUncommittedDiff(config, targetInfo);
      }
      return await gitClient.getCommitDiff(config, targetInfo, commitHash);
    },
    async getChangeDetails(config, targetInfo, commitHash) {
      if (commitHash === "UNCOMMITTED") {
        const details = await gitClient.getUncommittedDetails(config, targetInfo);

        return {
          id: "UNCOMMITTED",
          displayId: "uncommitted",
          author: details.author,
          date: details.date,
          message: details.message,
          changedPaths: details.changedPaths
        };
      }

      const details = await gitClient.getCommitDetails(config, targetInfo, commitHash);

      return {
        id: details.commitHash,
        displayId: details.commitHash.slice(0, 12),
        author: details.author,
        date: details.date,
        message: details.message,
        changedPaths: details.changedPaths
      };
    }
  };
}

const backends = {
  svn: createSvnBackend(),
  git: createGitBackend()
};

export async function resolveRepositoryContext(config) {
  const candidateTargetPath = path.resolve(config.baseDir, config.target);

  if (!isLikelyUrl(config.target) && (await pathExists(candidateTargetPath))) {
    try {
      return {
        backend: backends.git,
        targetInfo: await backends.git.getTargetInfo(config)
      };
    } catch {
      // Fall through to SVN auto-detection.
    }
  }

  return {
    backend: backends.svn,
    targetInfo: await backends.svn.getTargetInfo(config)
  };
}
