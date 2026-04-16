#!/usr/bin/env node

import { resolveConfig, parseCliArgs, printHelp, printVersion } from "./config.js";
import { runReviewCycle } from "./review-runner.js";
import { logger } from "./logger.js";

let cliArgs;

try {
  cliArgs = parseCliArgs(process.argv.slice(2));
} catch (error) {
  console.error(error?.message || String(error));
  printHelp();
  // CLI/usage errors -> exit code 2
  const code = Number(error?.exitCode) || 2;
  process.exit(code);
}

if (cliArgs.help) {
  printHelp();
  process.exit(0);
}

if (cliArgs.version) {
  printVersion();
  process.exit(0);
}

try {
  const config = await resolveConfig(cliArgs);
  logger.init(config);

  if (config.reviewerWasAutoSelected) {
    logger.info(
      `Reviewer "auto" selected ${config.reviewer}${config.reviewerCommandPath ? ` (${config.reviewerCommandPath})` : ""}.`,
      {
        scope: "session",
        reviewer: config.reviewer,
        reviewerCommandPath: config.reviewerCommandPath || "",
        console: true
      }
    );
  }

  logger.debug("Resolved config", {
    scope: "session",
    reviewer: config.reviewer,
    reviewerCommandPath: config.reviewerCommandPath || "",
    reviewerWasAutoSelected: config.reviewerWasAutoSelected || false,
    openaiBaseUrl: config.openaiBaseUrl,
    openaiModel: config.openaiModel,
    openaiOrganization: config.openaiOrganization || "",
    openaiProject: config.openaiProject || "",
    target: config.target,
    outputDir: config.outputDir,
    lang: config.lang,
    resolvedLang: config.resolvedLang,
    debug: config.debug,
    outputFormats: config.outputFormats,
    mode: config.uncommitted ? "uncommitted" : config.rev ? "rev" : "last",
    rev: config.rev || "",
    last: config.last || 0,
    console: "debug"
  });

  logger.info("Session started", {
    scope: "session",
    target: config.target,
    reviewer: config.reviewer,
    outputDir: config.outputDir,
    mode: config.uncommitted ? "uncommitted" : config.rev ? "rev" : "last",
    rev: config.rev || "",
    last: config.last || 0
  });
  await runReviewCycle(config);
  logger.info("Session completed successfully", {
    scope: "session",
    target: config.target,
    reviewer: config.reviewer
  });
} catch (error) {
  logger.error("Session failed", error, {
    scope: "session",
    console: true
  });
  // Map any attached exitCode (from thrown errors) to process exitCode, fallback to 1
  process.exitCode = Number(error?.exitCode) || 1;
}
process.exit(process.exitCode || 0);
