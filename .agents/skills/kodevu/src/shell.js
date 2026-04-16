import spawn from "cross-spawn";
import iconv from "iconv-lite";
import { logger } from "./logger.js";


function summarizeOutput(text) {
  if (!text) {
    return "(empty)";
  }

  const normalized = text.replace(/\s+/g, " ").trim();
  return normalized.length > 400 ? `${normalized.slice(0, 400)}...` : normalized;
}

export async function runCommand(command, args = [], options = {}) {
  const {
    cwd,
    env,
    input,
    encoding = "utf8",
    allowFailure = false,
    timeoutMs = 0,
    trim = false,
    debug = false
  } = options;

  logger.debug(`run: ${command}`, {
    scope: "command",
    command,
    args,
    cwd: cwd || "",
    timeoutMs: timeoutMs || 0,
    input: input ? summarizeOutput(input) : "",
    console: debug ? "debug" : false
  });

  return await new Promise((resolve, reject) => {
    const startedAt = Date.now();
    const child = spawn(command, args, {
      cwd,
      env: {
        ...process.env,
        ...env
      },
      stdio: ["pipe", "pipe", "pipe"]
    });

    const stdoutChunks = [];
    const stderrChunks = [];
    let timedOut = false;
    let timer = null;

    child.stdout.on("data", (chunk) => {
      stdoutChunks.push(Buffer.from(chunk));
    });

    child.stderr.on("data", (chunk) => {
      stderrChunks.push(Buffer.from(chunk));
    });

    child.on("error", (err) => {
      logger.error(`spawn error: ${command}`, err, {
        scope: "command",
        command,
        args,
        cwd: cwd || ""
      });
      // Mark spawn/runtime errors as runtime failures (exit code 3)
      try {
        if (!err || typeof err !== "object") err = new Error(String(err));
        if (err.exitCode == null) err.exitCode = 3;
      } catch (e) {
        // ignore
      }
      reject(err);
    });

    child.on("close", (code) => {
      if (timer) {
        clearTimeout(timer);
      }

      const stdout = iconv.decode(Buffer.concat(stdoutChunks), encoding);
      const stderr = iconv.decode(Buffer.concat(stderrChunks), encoding);
      const result = {
        code: code ?? 1,
        timedOut,
        stdout: trim ? stdout.trim() : stdout,
        stderr: trim ? stderr.trim() : stderr
      };
      const durationMs = Date.now() - startedAt;

      const exitMeta = {
        scope: "command",
        command,
        args,
        cwd: cwd || "",
        code: result.code,
        timedOut: result.timedOut,
        allowFailure,
        durationMs,
        stdout: summarizeOutput(result.stdout),
        stderr: summarizeOutput(result.stderr),
        console: debug ? "debug" : false
      };
      
      if ((result.code !== 0 || result.timedOut) && !allowFailure) {
        logger.error(`exit: ${command}`, null, exitMeta);
      } else {
        logger.debug(`exit: ${command}`, exitMeta);
      }

      if ((result.code !== 0 || result.timedOut) && !allowFailure) {
        const error = new Error(
          `Command failed: ${command} ${args.join(" ")}\n${result.stderr || result.stdout}`.trim()
        );
        error.result = result;
        // Map command failures to exit code 3 (runtime / external command failure)
        error.exitCode = 3;
        reject(error);
        return;
      }

      resolve(result);
    });

    if (input) {
      child.stdin.write(input);
    }

    child.stdin.end();

    if (timeoutMs > 0) {
      timer = setTimeout(() => {
        timedOut = true;
        child.kill("SIGTERM");
      }, timeoutMs);
    }
  });
}

export async function findCommandOnPath(command, options = {}) {
  const locator = process.platform === "win32" ? "where" : "which";
  const result = await runCommand(locator, [command], {
    allowFailure: true,
    trim: true,
    debug: options.debug
  });

  if (result.code !== 0 || result.timedOut || !result.stdout) {
    return null;
  }

  return (
    result.stdout
      .split(/\r?\n/)
      .map((item) => item.trim())
      .find(Boolean) || null
  );
}
