const fs = require("fs");
const path = require("path");
const pty = require("node-pty");

const sourceFile = "C:\\Users\\Yaleena Yara\\Desktop\\skills-export\\skills-repos-only.txt";
const successFile = path.join(process.cwd(), "skills-installed-success.txt");
const failedFile = path.join(process.cwd(), "skills-installed-failed.txt");
const progressFile = path.join(process.cwd(), "skills-progress.log");
const progressJsonFile = path.join(process.cwd(), "skills-progress.json");

const TARGET_SUMMARY_MORE_COUNT = 40;
const BUFFER_LIMIT = 1500000;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function stripAnsi(text) {
  return (text || "")
    .replace(/\x1b\[[0-9;?]*[ -/]*[@-~]/g, "")
    .replace(/\x1b\].*?\x07/g, "");
}

function appendProgress(line) {
  fs.appendFileSync(progressFile, line + "\n", "utf8");
}

function writeProgressJson(data) {
  fs.writeFileSync(progressJsonFile, JSON.stringify(data, null, 2), "utf8");
}

async function waitForMatch(state, testFn, timeoutMs, label) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (testFn(state.buffer)) return;
    await sleep(120);
  }
  throw new Error(`Timeout waiting for ${label}`);
}

async function key(term, seq, delay = 450) {
  term.write(seq);
  await sleep(delay);
}

function commandHasExplicitSkill(cmd) {
  return /\s--skill\s+\S+/.test(cmd);
}

function hasNoMatchingSkill(buffer) {
  return /No matching skills found for:/i.test(buffer);
}

function hasNoValidSkills(buffer) {
  return /No skills found/i.test(buffer) ||
         /No valid skills found/i.test(buffer) ||
         /Skills require a SKILL\.md/i.test(buffer);
}

function hasCloneFailure(buffer) {
  return /Failed to clone repository/i.test(buffer) ||
         /Authentication failed for/i.test(buffer) ||
         /Repository not found/i.test(buffer) ||
         /could not read Username/i.test(buffer) ||
         /fatal: unable to checkout working tree/i.test(buffer) ||
         /invalid path /i.test(buffer) ||
         /Installation failed/i.test(buffer);
}

function hasInstallSuccess(buffer) {
  return /Installation complete/i.test(buffer) ||
         /Installed\s+\d+\s+skill/i.test(buffer) ||
         /Done!/i.test(buffer);
}

function getFoundSkillCount(buffer) {
  const matches = [...buffer.matchAll(/Found\s+(\d+)\s+skills?/gi)];
  if (!matches.length) return null;
  return Number(matches[matches.length - 1][1]);
}

function getAgentSummaryMoreCount(buffer) {
  const matches = [...buffer.matchAll(/Selected:\s*Amp,\s*Antigravity,\s*Cline\s*\+(\d+)\s+more/gi)];
  if (!matches.length) return null;
  return Number(matches[matches.length - 1][1]);
}

function classifyFailure(buffer, fallback = "Unknown failure") {
  if (hasNoMatchingSkill(buffer)) return "No matching skill in repo";
  if (hasNoValidSkills(buffer)) return "No valid skills in repo";
  if (/Authentication failed for/i.test(buffer)) return "Clone/auth failure";
  if (/Repository not found/i.test(buffer)) return "Repository not found";
  if (/could not read Username/i.test(buffer)) return "Git credentials failure";
  if (/fatal: unable to checkout working tree/i.test(buffer)) return "Windows checkout path failure";
  if (/invalid path /i.test(buffer)) return "Windows invalid path failure";
  if (/Failed to clone repository/i.test(buffer)) return "Repository clone failure";
  if (/Installation failed/i.test(buffer)) return "Installation failed";
  return fallback;
}

async function waitForFoundSkillCount(state, timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const n = getFoundSkillCount(state.buffer);
    if (n !== null) return n;
    await sleep(120);
  }
  throw new Error("Could not detect found skill count");
}

async function waitForAgentSummary(state, timeoutMs = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const n = getAgentSummaryMoreCount(state.buffer);
    if (n !== null) return n;
    await sleep(120);
  }
  throw new Error("Could not detect Selected summary");
}

function getChecklistTail(buffer) {
  const idx = buffer.lastIndexOf("Select skills to install");
  return idx >= 0 ? buffer.slice(idx) : buffer;
}

function parseChecklistVisibleItems(buffer) {
  const tail = getChecklistTail(buffer);
  const lines = tail.split(/\r?\n/);
  const items = [];

  for (const raw of lines) {
    const line = raw.replace(/\r/g, "");
    if (!/[◻◼]/.test(line)) continue;

    const m = line.match(/[◻◼]\s+(.+)$/);
    if (!m) continue;

    const text = m[1].trim();
    if (!text) continue;

    const depth = (line.match(/│/g) || []).length;
    const checked = line.includes("◼");

    const isParentCategory =
      depth <= 1 &&
      !/\(/.test(text) &&
      !/^[a-z0-9._-]+$/i.test(text);

    const isLeaf =
      depth >= 2 ||
      /\(/.test(text) ||
      /^[a-z0-9][a-z0-9._-]*$/i.test(text) ||
      /^[a-z0-9][a-z0-9._-]*\s+\(/i.test(text);

    items.push({
      raw: line,
      text,
      depth,
      checked,
      isParentCategory,
      isLeaf: !isParentCategory && isLeaf
    });
  }

  return items;
}

function visibleLeafItems(buffer) {
  return parseChecklistVisibleItems(buffer).filter(x => x.isLeaf);
}

function visibleParentItems(buffer) {
  return parseChecklistVisibleItems(buffer).filter(x => x.isParentCategory);
}

function checkedLeafCount(buffer) {
  return visibleLeafItems(buffer).filter(x => x.checked).length;
}

function hasGroupedTree(buffer) {
  return visibleParentItems(buffer).length > 0;
}

async function waitForChecklist(state, timeoutMs = 30000) {
  await waitForMatch(
    state,
    txt => /Select skills to install/i.test(txt),
    timeoutMs,
    "skills checklist"
  );

  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (visibleLeafItems(state.buffer).length > 0 || visibleParentItems(state.buffer).length > 0) return;
    await sleep(120);
  }
  throw new Error("Checklist appeared but no selectable rows were detected");
}

async function focusChecklist(term) {
  await key(term, "\t", 160);
  await key(term, "\t", 160);
}

async function jumpChecklistTop(term) {
  for (let i = 0; i < 14; i++) {
    await key(term, "\x1b[A", 70);
  }
}

async function selectViaParentToggle(term, state, foundCount) {
  await focusChecklist(term);
  await jumpChecklistTop(term);
  await sleep(250);

  const parentsBefore = visibleParentItems(state.buffer);
  if (!parentsBefore.length) return false;

  const beforeCheckedLeaves = checkedLeafCount(state.buffer);

  await key(term, " ", 250);
  await sleep(700);

  const afterCheckedLeaves = checkedLeafCount(state.buffer);
  const parentsAfter = visibleParentItems(state.buffer);

  if (afterCheckedLeaves >= foundCount) {
    await key(term, "\r", 800);
    return true;
  }

  if (
    parentsAfter.length &&
    parentsAfter[0].checked &&
    afterCheckedLeaves > beforeCheckedLeaves
  ) {
    // give the UI one more beat to finish repainting the expanded check state
    await sleep(500);
    if (checkedLeafCount(state.buffer) >= foundCount) {
      await key(term, "\r", 800);
      return true;
    }
  }

  return false;
}

async function selectFlatOrLeafByLeaf(term, state, foundCount) {
  await focusChecklist(term);
  await jumpChecklistTop(term);
  await sleep(250);

  let selected = checkedLeafCount(state.buffer);
  let guard = 0;
  let stagnant = 0;
  let lastSelected = selected;

  while (selected < foundCount && guard < foundCount * 12) {
    const items = parseChecklistVisibleItems(state.buffer);
    const first = items[0];

    if (first && first.isLeaf && !first.checked) {
      await key(term, " ", 170);
      await sleep(140);
    }

    await key(term, "\x1b[B", 100);
    await sleep(100);

    selected = checkedLeafCount(state.buffer);

    if (selected > lastSelected) {
      lastSelected = selected;
      stagnant = 0;
    } else {
      stagnant += 1;
    }

    if (stagnant >= 18) {
      await focusChecklist(term);
      await key(term, "\x1b[B", 120);
      stagnant = 0;
    }

    guard += 1;
  }

  if (selected < foundCount) {
    throw new Error(`Checklist selection incomplete. Expected ${foundCount}, got ${selected}`);
  }

  await key(term, "\r", 800);
  return foundCount;
}

async function selectAllChecklist(term, state, foundCount) {
  await waitForChecklist(state, 30000);

  if (foundCount <= 0) {
    await key(term, "\r", 700);
    return 0;
  }

  if (hasGroupedTree(state.buffer)) {
    const parentWorked = await selectViaParentToggle(term, state, foundCount);
    if (parentWorked) return foundCount;
  }

  await selectFlatOrLeafByLeaf(term, state, foundCount);
  return foundCount;
}

async function handleSkillPhase(term, state, cmd) {
  if (commandHasExplicitSkill(cmd)) {
    return { repoMode: false, foundCount: 1 };
  }

  await waitForMatch(
    state,
    txt =>
      /Found\s+\d+\s+skills?/i.test(txt) ||
      /●\s+Skill:/i.test(txt) ||
      hasNoMatchingSkill(txt) ||
      hasNoValidSkills(txt) ||
      hasCloneFailure(txt),
    120000,
    "skill discovery"
  );

  if (hasNoMatchingSkill(state.buffer) || hasNoValidSkills(state.buffer) || hasCloneFailure(state.buffer)) {
    return { repoMode: true, foundCount: 0 };
  }

  const foundCount = await waitForFoundSkillCount(state, 30000);

  if (/●\s+Skill:/i.test(state.buffer) || foundCount <= 1) {
    return { repoMode: true, foundCount: Math.max(foundCount, 1) };
  }

  await selectAllChecklist(term, state, foundCount);
  return { repoMode: true, foundCount };
}

function currentScreenHasAgents(buffer) {
  const tail = buffer.slice(-14000);
  return /Which agents do you want to install to\?/i.test(tail) &&
         /Selected:\s*Amp,\s*Antigravity,\s*Cline\s*\+\d+\s+more/i.test(tail);
}

async function handleAgentsPhase(term, state) {
  await waitForMatch(
    state,
    txt => /Which agents do you want to install to\?/i.test(txt),
    120000,
    "agent picker"
  );

  if (!currentScreenHasAgents(state.buffer)) {
    throw new Error("Agents screen not stable");
  }

  const selected = await waitForAgentSummary(state, 15000);
  if (selected < TARGET_SUMMARY_MORE_COUNT) {
    throw new Error(`Picker is not fully selected. Expected +${TARGET_SUMMARY_MORE_COUNT} more, got +${selected}`);
  }

  await key(term, "\r", 800);
}

async function handleScopeMethodProceed(term, state) {
  await waitForMatch(
    state,
    txt => /Installation scope/i.test(txt),
    30000,
    "installation scope"
  );
  await key(term, "\r", 650);

  await waitForMatch(
    state,
    txt => /Installation method/i.test(txt),
    30000,
    "installation method"
  );
  await key(term, "\r", 650);

  await waitForMatch(
    state,
    txt => /Proceed with installation\?/i.test(txt) || /Installation Summary/i.test(txt),
    30000,
    "installation summary"
  );

  if (!/Proceed with installation\?/i.test(state.buffer)) {
    await waitForMatch(
      state,
      txt => /Proceed with installation\?/i.test(txt),
      30000,
      "proceed prompt"
    );
  }

  await key(term, "\r", 750);
}

async function installOne(cmd) {
  const term = pty.spawn("powershell.exe", ["-NoLogo"], {
    name: "xterm-color",
    cols: 140,
    rows: 45,
    cwd: process.cwd(),
    env: process.env
  });

  const state = { buffer: "" };

  term.onData(data => {
    state.buffer += stripAnsi(data);
    if (state.buffer.length > BUFFER_LIMIT) {
      state.buffer = state.buffer.slice(-BUFFER_LIMIT);
    }
  });

  try {
    await sleep(600);
    term.write(cmd + "\r");

    const skillPhase = await handleSkillPhase(term, state, cmd);

    if (hasNoMatchingSkill(state.buffer) || hasNoValidSkills(state.buffer) || hasCloneFailure(state.buffer)) {
      term.kill();
      return {
        ok: false,
        log: state.buffer,
        reason: classifyFailure(state.buffer, "Skill discovery failed"),
        foundCount: skillPhase.foundCount || 0,
        repoMode: skillPhase.repoMode
      };
    }

    await handleAgentsPhase(term, state);
    await handleScopeMethodProceed(term, state);

    await waitForMatch(
      state,
      txt => hasInstallSuccess(txt) || hasCloneFailure(txt) || hasNoValidSkills(txt),
      180000,
      "installation completion"
    );

    const ok = hasInstallSuccess(state.buffer);
    term.kill();

    return {
      ok,
      log: state.buffer,
      reason: ok ? "" : classifyFailure(state.buffer, "Install reported failure"),
      foundCount: skillPhase.foundCount || 0,
      repoMode: skillPhase.repoMode
    };
  } catch (err) {
    term.kill();
    return {
      ok: false,
      log: state.buffer + "\n" + err.message,
      reason: classifyFailure(state.buffer, err.message),
      foundCount: 0,
      repoMode: !commandHasExplicitSkill(cmd)
    };
  }
}

async function main() {
  if (!fs.existsSync(sourceFile)) {
    console.error("Missing source file:", sourceFile);
    process.exit(1);
  }

  const commands = fs.readFileSync(sourceFile, "utf8")
    .split(/\r?\n/)
    .map(x => x.trim())
    .filter(Boolean);

  fs.writeFileSync(progressFile, "", "utf8");
  writeProgressJson({
    totalCommands: commands.length,
    currentCommandIndex: 0,
    installedCommands: 0,
    failedCommands: 0,
    remainingCommands: commands.length,
    installedSkills: 0,
    failedSkills: 0,
    currentCommand: "",
    currentRepoSkillCount: 0
  });

  const success = [];
  const failed = [];
  let installedSkills = 0;
  let failedSkills = 0;

  appendProgress(`Started at: ${new Date().toLocaleString()}`);
  appendProgress(`Total commands: ${commands.length}`);
  appendProgress("--------------------------------------------------");

  for (let i = 0; i < commands.length; i++) {
    const cmd = commands[i];
    const index = i + 1;

    console.log(`\n[${index}/${commands.length}] Installing: ${cmd}`);
    appendProgress(`[${index}/${commands.length}] START  ${cmd}`);

    writeProgressJson({
      totalCommands: commands.length,
      currentCommandIndex: index,
      installedCommands: success.length,
      failedCommands: failed.length,
      remainingCommands: commands.length - index + 1,
      installedSkills,
      failedSkills,
      currentCommand: cmd,
      currentRepoSkillCount: 0
    });

    const result = await installOne(cmd);

    if (result.ok) {
      success.push(cmd);
      const skillCount = result.repoMode ? Math.max(result.foundCount || 0, 1) : 1;
      installedSkills += skillCount;

      appendProgress(
        `[${index}/${commands.length}] OK     repoMode=${result.repoMode} skills=${skillCount} installedCommands=${success.length} failedCommands=${failed.length} installedSkills=${installedSkills} failedSkills=${failedSkills} remainingCommands=${commands.length - index}`
      );
    } else {
      failed.push(cmd);
      fs.writeFileSync(path.join(process.cwd(), `failed-${index}.log`), result.log, "utf8");

      const skillCount = result.repoMode ? Math.max(result.foundCount || 0, 1) : 1;
      failedSkills += skillCount;

      appendProgress(
        `[${index}/${commands.length}] FAIL   repoMode=${result.repoMode} skills=${skillCount} installedCommands=${success.length} failedCommands=${failed.length} installedSkills=${installedSkills} failedSkills=${failedSkills} remainingCommands=${commands.length - index}`
      );
      appendProgress(`Reason: ${result.reason || "Unknown failure"}`);
    }

    fs.writeFileSync(successFile, success.join("\n"), "utf8");
    fs.writeFileSync(failedFile, failed.join("\n"), "utf8");

    writeProgressJson({
      totalCommands: commands.length,
      currentCommandIndex: index,
      installedCommands: success.length,
      failedCommands: failed.length,
      remainingCommands: commands.length - index,
      installedSkills,
      failedSkills,
      currentCommand: cmd,
      currentRepoSkillCount: result.repoMode ? (result.foundCount || 0) : 1
    });

    await sleep(500);
  }

  appendProgress("--------------------------------------------------");
  appendProgress(`Finished at: ${new Date().toLocaleString()}`);
  appendProgress(`Installed commands: ${success.length}`);
  appendProgress(`Failed commands: ${failed.length}`);
  appendProgress(`Installed skills: ${installedSkills}`);
  appendProgress(`Failed skills: ${failedSkills}`);
  appendProgress("Remaining commands: 0");

  writeProgressJson({
    totalCommands: commands.length,
    currentCommandIndex: commands.length,
    installedCommands: success.length,
    failedCommands: failed.length,
    remainingCommands: 0,
    installedSkills,
    failedSkills,
    currentCommand: "",
    currentRepoSkillCount: 0
  });

  console.log("\nDone.");
  console.log("Successful commands:", success.length);
  console.log("Failed commands:", failed.length);
  console.log("Installed skills:", installedSkills);
  console.log("Failed skills:", failedSkills);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});