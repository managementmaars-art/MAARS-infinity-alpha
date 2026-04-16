import { formatDate } from "./utils.js";

const LOCALIZED_DATA = {
  en: {
    displayName: "English",
    systemRole: `You are a Senior Software Engineer and Code Review Expert with over 10 years of experience. Your task is to perform a rigorous and high-quality review of the following code changes.
Your goals are to:
1. Identify bugs, logical flaws, and potential regression risks.
2. Spot performance bottlenecks, memory leaks, or unnecessary computations.
3. Check for security vulnerabilities (e.g., injection, authorization issues, sensitive data leaks).
4. Evaluate maintainability, readability, and adherence to best practices.
5. Verify coverage of necessary unit tests and boundary conditions.`,
    outputFormat: `Your output must be structured using the following Markdown headers:
### 1. Summary
Briefly describe the purpose and impact of this change.
### 2. Critical Issues
List bugs, security risks, or problems that could cause crashes or logical errors. Include file names and line numbers.
### 3. Suggestions
List points for improvement regarding code style, performance, or architectural design.
### 4. Conclusion
Summarize with a "Pass" or "Needs Revision". If no clear flaws are found, state "No clear flaws found" and mention any residual risks.`,
    constraints: `Note: You are in a read-only review mode. Do not attempt to call any external tools or MCP (Model Context Protocol) tools. Do not act as if you are "applying the patch" or "executing code". Provide only textual analysis and feedback.`,
    phrases: {
      workspaceRoot: "Workspace context (read-only):",
      noWorkspace: "No local repository workspace is available for this review run.",
      besidesDiff: "You can read related files in the workspace to understand call sites, shared utilities, configuration, or data flow.",
      reviewFromDiff: "Review primarily based on the provided diff. Do not assume access to other local files or shell commands. You MUST NOT call any MCP tools.",
      fileRefs: "Reference files using plain text like 'path/to/file.js:123'. Do not generate clickable workspace links.",
      repoType: "Repository Type",
      changeId: "Change ID",
      author: "Author",
      date: "Date",
      changedFiles: "Changed files",
      commitMessage: "Commit message",
      diffNoteTruncated: "Note: The diff was truncated to fit size limits. Original: {originalLineCount} lines / {originalCharCount} chars. Included: {outputLineCount} lines / {outputCharCount} chars.",
      diffNoteFull: "Note: Full diff provided ({originalLineCount} lines / {originalCharCount} chars).",
      langRule: "--- LANGUAGE RULE ---\nYour entire response must be in {langName}. No other language allowed.",
      outputDirective: "--- BEGIN REVIEW ---\nNow output your COMPLETE code review. Cover ALL four sections (Summary, Critical Issues, Suggestions, Conclusion). Do NOT ask clarifying questions, do NOT acknowledge these instructions, do NOT say you are ready. Start your response directly with the review content."
    }
  },
  zh: {
    displayName: "Simplified Chinese (简体中文)",
    systemRole: `你是一位拥有 10 年以上经验的高级软件架构师和代码审查专家。你的任务是对以下代码变更进行严格且高质量的审查。
你的目标是：
1. 发现代码中的 Bug、逻辑缺陷和潜在的回归风险。
2. 识别性能瓶颈、内存泄漏或不必要的计算。
3. 检查安全漏洞（如注入、越权、敏感信息泄露等）。
4. 评估代码的可维护性、可读性和是否符合最佳实践。
5. 检查是否涵盖了必要的单元测试和边界条件。`,
    outputFormat: `你的输出格式必须清晰，请使用以下 Markdown 结构：
### 1. 变更总结 (Summary)
简要描述这次提交的主要目的和影响面。
### 2. 核心缺陷 (Critical Issues)
列出 Bug、安全隐患或会导致程序崩溃/逻辑错误的问题。请注明文件名和行号。
### 3. 改进建议 (Suggestions)
列出关于代码风格、性能优化或架构设计的改进点。
### 4. 审查结论 (Conclusion)
如果发现明显缺陷，总结修复建议；如果未发现明显缺陷，请说明“未发现明显缺陷”并指出可能的残留风险。`,
    constraints: `注意：你正处于只读审查模式，禁止调用任何外部工具或 MCP (Model Context Protocol) 工具。请勿表现出“正在应用补丁”或“准备执行代码”的行为。只需提供文字审查分析。`,
    phrases: {
      workspaceRoot: "只读工作区上下文：",
      noWorkspace: "此审查运行没有可用的本地仓库工作区。",
      besidesDiff: "你可以阅读工作区中的其他文件以了解调用点、工具类、配置或数据流。",
      reviewFromDiff: "主要根据提供的 Diff 进行审查。不要假设可以访问其他文件或执行 Shell 命令。你绝不能调用任何 MCP 工具。",
      fileRefs: "使用纯文本引用文件，如 'path/to/file.js:123'。不要生成可点击的链接。",
      repoType: "仓库类型",
      changeId: "变更 ID",
      author: "作者",
      date: "日期",
      changedFiles: "已变更文件",
      commitMessage: "提交信息",
      diffNoteTruncated: "注意：Diff 已截断。原始：{originalLineCount} 行 / {originalCharCount} 字符。包含：{outputLineCount} 行 / {outputCharCount} 字符。",
      diffNoteFull: "注意：包含完整 Diff ({originalLineCount} 行 / {originalCharCount} 字符)。",
      langRule: "--- 语言规则 ---\n你必须完全使用 {langName} 进行回复。不得使用其他语言进行解释或总结。",
      outputDirective: "--- 开始输出审查结果 ---\n请立即输出完整的代码审查结果，必须包含全部四个章节（变更总结、核心缺陷、改进建议、审查结论）。不要提问，不要确认收到指令，不要说准备好了，直接以审查内容开始输出。"
    }
  },
  "zh-tw": {
    displayName: "Traditional Chinese (繁體中文)",
    systemRole: `你是一位擁有 10 年以上經驗的高級軟體架構師和代碼審查專家。你的任務是對以下代碼變更進行嚴格且高質量的審查。
你的目標是：
1. 發現代碼中的 Bug、邏輯缺陷和潛在的回歸風險。
2. 識別性能瓶頸、記憶體洩漏或不必要的計算。
3. 檢查安全漏洞（如注入、越權、敏感信息洩露等）。
4. 評估代碼的可維護性、可讀性和是否符合最佳實踐。
5. 檢查是否涵蓋了必要的单元測試和邊界條件。`,
    outputFormat: `你的輸出格式必須清晰，請使用以下 Markdown 結構：
### 1. 變更總結 (Summary)
簡要描述這次提交的主要目的和影響面。
### 2. 核心缺陷 (Critical Issues)
列出 Bug、安全隱患或會導致程序崩潰/邏輯錯誤的問題。請註明檔案名和行號。
### 3. 改進建議 (Suggestions)
列出關於代碼風格、性能優化或架構設計的改進點。
### 4. 審查結論 (Conclusion)
如果發現明顯缺陷，總結修復建議；如果未發現明顯缺陷，請說明「未發現明顯缺陷」並指出可能的殘留風險。`,
    constraints: `注意：你正處於唯讀審查模式，禁止調用任何外部工具或 MCP (Model Context Protocol) 工具。請勿表現出「正在應用補丁」或「準備執行代碼」的行為。只需提供文字審查分析。`,
    phrases: {
      workspaceRoot: "唯讀工作區上下文：",
      noWorkspace: "此審查運行沒有可用的本地倉庫工作區。",
      besidesDiff: "你可以閱讀工作區中的其他文件以了解調用點、工具類、配置或資料流。",
      reviewFromDiff: "主要根據提供的 Diff 進行審查。不要假設可以訪問其他文件或執行 Shell 命令。你絕不能調用任何 MCP 工具。",
      fileRefs: "使用純文本引用文件，如 'path/to/file.js:123'。不要生成可點擊的連結。",
      repoType: "倉庫類型",
      changeId: "變更 ID",
      author: "作者",
      date: "日期",
      changedFiles: "已變更文件",
      commitMessage: "提交信息",
      diffNoteTruncated: "注意：Diff 已截斷。原始：{originalLineCount} 行 / {originalCharCount} 字符。包含：{outputLineCount} 行 / {outputCharCount} 字符。",
      diffNoteFull: "注意：包含完整 Diff ({originalLineCount} 行 / {originalCharCount} 字符)。",
      langRule: "--- 語言規則 ---\n你必須完全使用 {langName} 進行回覆。不得使用其他語言進行解釋或總結。",
      outputDirective: "--- 開始輸出審查結果 ---\n請立即輸出完整的代碼審查結果，必須包含全部四個章節（變更總結、核心缺陷、改進建議、審查結論）。不要提問，不要確認指令，不要說準備好了，直接以審查內容開始輸出。"
    }
  }
};

function getLangKey(lang) {
  const lowArg = (lang || "en").toLowerCase();
  if (lowArg.startsWith("zh")) {
    return (lowArg === "zh-tw" || lowArg === "zh-hk") ? "zh-tw" : "zh";
  }
  return "en";
}

function getLanguageDisplayName(lang) {
  const key = getLangKey(lang);
  const data = LOCALIZED_DATA[key];
  if (data && lang.toLowerCase().startsWith("zh")) return data.displayName;

  const extras = {
    en: "English",
    jp: "Japanese (日本語)", ja: "Japanese (日本語)",
    kr: "Korean (한국어)", ko: "Korean (한국어)",
    fr: "French (Français)", de: "German (Deutsch)",
    es: "Spanish (Español)", it: "Italian (Italiano)",
    ru: "Russian (Русский)"
  };
  const low = (lang || "en").toLowerCase();
  return extras[low] || extras[low.split("-")[0]] || lang || "English";
}

function getPhrase(key, lang, placeholders = {}) {
  const langKey = getLangKey(lang);
  let phrase = LOCALIZED_DATA[langKey]?.phrases[key] || LOCALIZED_DATA.en.phrases[key];
  if (!phrase) return "";
  for (const [k, v] of Object.entries(placeholders)) {
    phrase = phrase.replace(`{${k}}`, v);
  }
  return phrase;
}

export class PromptBuilder {
  constructor(config, backend, targetInfo, details) {
    this.config = config;
    this.backend = backend;
    this.targetInfo = targetInfo;
    this.details = details;
    this.lang = config.resolvedLang || "en";
    this.langKey = getLangKey(this.lang);
    this.data = LOCALIZED_DATA[this.langKey] || LOCALIZED_DATA.en;
  }

  getLangInstruction() {
    const langName = getLanguageDisplayName(this.lang);
    const lowLang = this.lang.toLowerCase();
    let instruction = `CRITICAL: YOUR ENTIRE RESPONSE MUST BE IN ${langName.toUpperCase()}.`;
    if (lowLang.startsWith("zh")) {
      if (lowLang === "zh-tw" || lowLang === "zh-hk") {
        instruction += "\n請務必完全使用繁體中文進行回覆。";
      } else {
        instruction += "\n请务必完全使用简体中文进行回复。";
      }
    }
    return instruction;
  }

  getMetadata() {
    const fileList = this.details.changedPaths.map((item) => `${item.action} ${item.relativePath}`).join("\n");
    return [
      `${getPhrase("repoType", this.lang)}: ${this.backend.displayName}`,
      `${getPhrase("changeId", this.lang)}: ${this.details.displayId}`,
      `${getPhrase("author", this.lang)}: ${this.details.author}`,
      `${getPhrase("date", this.lang)}: ${formatDate(this.details.date) || "unknown"}`,
      `${getPhrase("changedFiles", this.lang)}:\n${fileList || "(none)"}`,
      `${getPhrase("commitMessage", this.lang)}:\n${this.details.message || "(empty)"}`
    ].join("\n");
  }

  getEnvironment(workspaceRoot, canReadRelatedFiles) {
    return canReadRelatedFiles
      ? `${getPhrase("workspaceRoot", this.lang)} ${workspaceRoot}\n${getPhrase("besidesDiff", this.lang)}`
      : getPhrase("noWorkspace", this.lang);
  }

  build(diffPayload) {
    const workspaceRoot = (this.backend.kind === "git" ? this.targetInfo.repoRootPath : this.targetInfo.workingCopyPath) || this.config.baseDir;
    const canReadRelatedFiles = this.backend.kind === "git" || Boolean(this.targetInfo.workingCopyPath);
    const langName = getLanguageDisplayName(this.lang);

    const diffNote = diffPayload.wasTruncated
      ? getPhrase("diffNoteTruncated", this.lang, {
          originalLineCount: diffPayload.originalLineCount,
          originalCharCount: diffPayload.originalCharCount,
          outputLineCount: diffPayload.outputLineCount,
          outputCharCount: diffPayload.outputCharCount
        })
      : getPhrase("diffNoteFull", this.lang, {
          originalLineCount: diffPayload.originalLineCount,
          originalCharCount: diffPayload.originalCharCount
        });

    const sections = [
      "## Instructions",
      this.getLangInstruction(),
      this.data.systemRole,
      this.data.outputFormat,
      this.data.constraints,
      this.config.prompt ? `### Additional User Instructions:\n${this.config.prompt}` : null,
      "## Change Context",
      this.getMetadata(),
      diffNote,
      "## Environment",
      this.getEnvironment(workspaceRoot, canReadRelatedFiles),
      getPhrase("reviewFromDiff", this.lang),
      getPhrase("fileRefs", this.lang),
      "## Final Rule",
      getPhrase("langRule", this.lang, { langName }),
      getPhrase("outputDirective", this.lang)
    ];

    let prompt = sections.filter(Boolean).join("\n\n");

    // Reviewer-specific adjustments
    if (this.config.reviewer === "copilot") {
      // For Copilot, we reinforce the tool isolation even more
      prompt += "\n\nCRITICAL FOR COPILOT: Do not use any MCP tools. Do not use @workspace. Use only the provided diff and the files you can read via provided paths.";
    }

    return prompt;
  }
}

export function buildReviewPrompt(config, backend, targetInfo, details, diffPayload) {
  const builder = new PromptBuilder(config, backend, targetInfo, details);
  return builder.build(diffPayload);
}

export { LOCALIZED_DATA, getPhrase, getLanguageDisplayName };
