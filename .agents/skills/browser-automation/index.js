// Browser Automation Skill - OpenClaw Tool Implementation
// 使用 Playwright 实现浏览器自动化，支持连接已有 Chrome

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const os = require('os');

// 配置
const USER_DATA_DIR = path.join(os.homedir(), '.openclaw', 'browser-data');
const CDP_PORT = 9222; // Chrome remote debugging port

// 全局浏览器实例
let browser = null;
let context = null;
let page = null;
let connectionMode = null; // 'cdp' 或 'launch'
let isConnected = false; // 追踪连接状态

/**
 * 尝试连接到已有的 Chrome（通过 CDP）
 */
async function tryConnectCDP() {
  try {
    const browser = await chromium.connectOverCDP(`http://localhost:${CDP_PORT}`);
    isConnected = true; // 成功连接后标记为已连接
    return browser;
  } catch (e) {
    isConnected = false; // 连接失败后标记为未连接
    return null;
  }
}

/**
 * 确保浏览器已启动
 * 优先尝试连接已有的 Chrome，连不上再启动新的
 */
async function ensureBrowser() {
  // 检查是否已连接
  if (isConnected) {
    return; // 已连接且有效，直接返回
  }

  // 1. 优先尝试连接已有的 Chrome (CDP)
  const existingBrowser = await tryConnectCDP();
  if (existingBrowser) {
    browser = existingBrowser;
    context = browser.contexts()[0];
    connectionMode = 'cdp';
    isConnected = true;

    // 获取所有 context 和页面
    const contexts = browser.contexts();
    if (contexts.length > 0) {
      context = contexts[0];
      const pages = context.pages();
      if (pages.length > 0) {
        page = pages[pages.length - 1]; // 使用最后一个页面
      } else {
        page = await context.newPage();
      }
    }

    console.log(`✅ 已连接到现有 Chrome (CDP 端口 ${CDP_PORT})`);
    return;
  }

  // 2. 连接失败，启动新的 Chromium
  console.log('⚠️ 未检测到 Chrome CDP，启动新的 Chromium...');

  // 确保用户数据目录存在
  if (!fs.existsSync(USER_DATA_DIR)) {
    fs.mkdirSync(USER_DATA_DIR, { recursive: true });
  }

  // 启动浏览器（使用持久化上下文）
  context = await chromium.launchPersistentContext(USER_DATA_DIR, {
    headless: false,
    viewport: null,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-session-crashed-bubble',
      '--hide-crash-restore-bubble',
    ]
  });

  browser = null; // launch 模式下 browser 为 null
  connectionMode = 'launch';
  isConnected = true;

  // 获取或创建页面
  const pages = context.pages();
  if (pages.length > 0) {
    page = pages[0];
  } else {
    page = await context.newPage();
  }

  console.log('✅ 新 Chromium 已启动');
}

/**
 * 确保有可用页面
 */
async function ensurePage() {
  await ensureBrowser();

  // 检查页面是否还有效
  if (page && !page.isClosed()) {
    return page;
  }

  // 页面已关闭，创建新页面
  const pages = context.pages();
  if (pages.length > 0) {
    page = pages[0];
  } else {
    page = await context.newPage();
  }

  return page;
}

// ============ Handlers ============

/**
 * 导航到 URL（复用现有页面）
 */
async function handleNavigate(args) {
  const { url } = args || {};

  if (!url) {
    return '❌ 请提供 URL\n💡 用法: navigate({url: "https://example.com"})';
  }

  // 确保 URL 有协议
  let targetUrl = url;
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    targetUrl = 'https://' + url;
  }

  try {
    await ensurePage();
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

    const title = await page.title();
    return `✅ 已打开: ${targetUrl}\n📄 标题: ${title}`;
  } catch (error) {
    return `❌ 导航失败: ${error.message}`;
  }
}

/**
 * 打开新页面
 */
async function handleNewPage(args) {
  const { url } = args || {};

  try {
    await ensureBrowser();

    page = await context.newPage();

    if (url) {
      let targetUrl = url;
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        targetUrl = 'https://' + url;
      }
      await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
      const title = await page.title();
      return `✅ 已打开新页面: ${targetUrl}\n📄 标题: ${title}`;
    }

    return '✅ 已打开新空白页面';
  } catch (error) {
    return `❌ 打开新页面失败: ${error.message}`;
  }
}

/**
 * 点击元素
 */
async function handleClick(args) {
  const { selector, timeout = 10000 } = args || {};

  if (!selector) {
    return '❌ 请提供选择器\n💡 用法: click({selector: "#button"})';
  }

  try {
    await ensurePage();
    await page.click(selector, { timeout });
    return `✅ 已点击: ${selector}`;
  } catch (error) {
    return `❌ 点击失败: ${error.message}\n💡 检查选择器是否正确: ${selector}`;
  }
}

/**
 * 填写表单
 */
async function handleFill(args) {
  const { selector, value, clear = true } = args || {};

  if (!selector || value === undefined) {
    return '❌ 请提供选择器和值\n💡 用法: fill({selector: "#input", value: "文本内容"})';
  }

  try {
    await ensurePage();

    if (clear) {
      await page.fill(selector, value, { timeout: 10000 });
    } else {
      await page.type(selector, value, { timeout: 10000 });
    }

    return `✅ 已填写: ${selector} = "${value}"`;
  } catch (error) {
    return `❌ 填写失败: ${error.message}\n💡 检查选择器是否正确: ${selector}`;
  }
}

/**
 * 模拟打字（逐字输入）
 */
async function handleType(args) {
  const { selector, text, delay = 50 } = args || {};

  if (!selector || !text) {
    return '❌ 请提供选择器和文本\n💡 用法: type({selector: "#input", text: "文本"})';
  }

  try {
    await ensurePage();
    await page.type(selector, text, { delay, timeout: 10000 });
    return `✅ 已输入: "${text}"`;
  } catch (error) {
    return `❌ 输入失败: ${error.message}`;
  }
}

/**
 * 下拉选择
 */
async function handleSelect(args) {
  const { selector, value } = args || {};

  if (!selector || value === undefined) {
    return '❌ 请提供选择器和值\n💡 用法: select({selector: "#dropdown", value: "option1"})';
  }

  try {
    await ensurePage();
    await page.selectOption(selector, value, { timeout: 10000 });
    return `✅ 已选择: ${value}`;
  } catch (error) {
    return `❌ 选择失败: ${error.message}`;
  }
}

/**
 * 勾选/取消勾选
 */
async function handleCheck(args) {
  const { selector, checked = true } = args || {};

  if (!selector) {
    return '❌ 请提供选择器\n💡 用法: check({selector: "#checkbox", checked: true})';
  }

  try {
    await ensurePage();

    if (checked) {
      await page.check(selector, { timeout: 10000 });
      return `✅ 已勾选: ${selector}`;
    } else {
      await page.uncheck(selector, { timeout: 10000 });
      return `✅ 已取消勾选: ${selector}`;
    }
  } catch (error) {
    return `❌ 操作失败: ${error.message}`;
  }
}

/**
 * 截图
 */
async function handleScreenshot(args) {
  const { selector, fullPage = false } = args || {};

  try {
    await ensurePage();

    const timestamp = Date.now();
    const filename = `screenshot-${timestamp}.png`;
    const screenshotPath = path.join(os.homedir(), '.openclaw', 'browser-data', filename);

    let screenshot;
    if (selector) {
      const element = await page.$(selector);
      if (!element) {
        return `❌ 未找到元素: ${selector}`;
      }
      screenshot = await element.screenshot();
    } else {
      screenshot = await page.screenshot({ fullPage });
    }

    fs.writeFileSync(screenshotPath, screenshot);

    return `✅ 截图已保存: ${screenshotPath}\n📁 文件: ${filename}`;
  } catch (error) {
    return `❌ 截图失败: ${error.message}`;
  }
}

/**
 * 获取页面内容
 */
async function handleGetContent(args) {
  const { selector } = args || {};

  try {
    await ensurePage();

    if (selector) {
      const element = await page.$(selector);
      if (!element) {
        return `❌ 未找到元素: ${selector}`;
      }
      const text = await element.textContent();
      return text || '(空)';
    }

    const content = await page.content();
    // 截取前 5000 字符避免输出过长
    if (content.length > 5000) {
      return content.substring(0, 5000) + '\n\n... (内容过长，已截断)';
    }
    return content;
  } catch (error) {
    return `❌ 获取内容失败: ${error.message}`;
  }
}

/**
 * 获取元素文本
 */
async function handleGetText(args) {
  const { selector } = args || {};

  if (!selector) {
    return '❌ 请提供选择器\n💡 用法: getText({selector: "#element"})';
  }

  try {
    await ensurePage();
    const text = await page.textContent(selector, { timeout: 10000 });
    return text || '(空)';
  } catch (error) {
    return `❌ 获取文本失败: ${error.message}`;
  }
}

/**
 * 获取表单值
 */
async function handleGetValue(args) {
  const { selector } = args || {};

  if (!selector) {
    return '❌ 请提供选择器\n💡 用法: getValue({selector: "#input"})';
  }

  try {
    await ensurePage();
    const value = await page.inputValue(selector, { timeout: 10000 });
    return value || '(空)';
  } catch (error) {
    return `❌ 获取值失败: ${error.message}`;
  }
}

/**
 * 获取属性
 */
async function handleGetAttribute(args) {
  const { selector, attribute } = args || {};

  if (!selector || !attribute) {
    return '❌ 请提供选择器和属性名\n💡 用法: getAttribute({selector: "#link", attribute: "href"})';
  }

  try {
    await ensurePage();
    const value = await page.getAttribute(selector, attribute, { timeout: 10000 });
    return value || '(无)';
  } catch (error) {
    return `❌ 获取属性失败: ${error.message}`;
  }
}

/**
 * 等待元素
 */
async function handleWait(args) {
  const { selector, timeout = 30000 } = args || {};

  if (!selector) {
    return '❌ 请提供选择器\n💡 用法: wait({selector: "#element", timeout: 10000})';
  }

  try {
    await ensurePage();
    await page.waitForSelector(selector, { timeout, state: 'visible' });
    return `✅ 元素已出现: ${selector}`;
  } catch (error) {
    return `❌ 等待超时: ${error.message}`;
  }
}

/**
 * 等待页面跳转
 */
async function handleWaitForNavigation(args) {
  const { timeout = 30000 } = args || {};

  try {
    await ensurePage();
    await page.waitForNavigation({ timeout, waitUntil: 'domcontentloaded' });
    const url = page.url();
    return `✅ 页面已跳转: ${url}`;
  } catch (error) {
    return `❌ 等待跳转超时: ${error.message}`;
  }
}

/**
 * 执行 JavaScript
 */
async function handleEvaluate(args) {
  const { script } = args || {};

  if (!script) {
    return '❌ 请提供 JavaScript 代码\n💡 用法: evaluate({script: "document.title"})';
  }

  try {
    await ensurePage();
    const result = await page.evaluate(script);
    return JSON.stringify(result, null, 2);
  } catch (error) {
    return `❌ 执行失败: ${error.message}`;
  }
}

/**
 * 上传文件
 */
async function handleUpload(args) {
  const { selector, filePath } = args || {};

  if (!selector || !filePath) {
    return '❌ 请提供选择器和文件路径\n💡 用法: upload({selector: "input[type=file]", filePath: "C:/path/to/file"})';
  }

  try {
    await ensurePage();

    // 检查文件是否存在
    if (!fs.existsSync(filePath)) {
      return `❌ 文件不存在: ${filePath}`;
    }

    const input = await page.$(selector);
    if (!input) {
      return `❌ 未找到上传控件: ${selector}`;
    }

    await input.setInputFiles(filePath);
    return `✅ 已上传文件: ${filePath}`;
  } catch (error) {
    return `❌ 上传失败: ${error.message}`;
  }
}

/**
 * 按键
 */
async function handlePress(args) {
  const { key } = args || {};

  if (!key) {
    return '❌ 请提供按键\n💡 用法: press({key: "Enter"})\n   常用: Enter, Escape, Tab, ArrowUp, ArrowDown, Backspace';
  }

  try {
    await ensurePage();
    await page.keyboard.press(key);
    return `✅ 已按下: ${key}`;
  } catch (error) {
    return `❌ 按键失败: ${error.message}`;
  }
}

/**
 * 鼠标悬停
 */
async function handleHover(args) {
  const { selector } = args || {};

  if (!selector) {
    return '❌ 请提供选择器\n💡 用法: hover({selector: "#element"})';
  }

  try {
    await ensurePage();
    await page.hover(selector, { timeout: 10000 });
    return `✅ 已悬停: ${selector}`;
  } catch (error) {
    return `❌ 悬停失败: ${error.message}`;
  }
}

/**
 * 滚动页面
 */
async function handleScroll(args) {
  const { direction = 'down', amount = 500 } = args || {};

  try {
    await ensurePage();

    const delta = direction === 'up' ? -amount : amount;
    await page.evaluate((d) => {
      window.scrollBy(0, d);
    }, delta);

    return `✅ 已向${direction === 'up' ? '上' : '下'}滚动 ${amount}px`;
  } catch (error) {
    return `❌ 滚动失败: ${error.message}`;
  }
}

/**
 * 关闭当前页面
 */
async function handleClose() {
  try {
    if (page && !page.isClosed()) {
      await page.close();

      // 切换到其他页面
      const pages = context.pages();
      if (pages.length > 0) {
        page = pages[0];
        return '✅ 已关闭当前页面，切换到其他页面';
      } else {
        page = null;
        return '✅ 已关闭当前页面（无其他页面）';
      }
    }
    return '⚠️ 没有打开的页面';
  } catch (error) {
    return `❌ 关闭失败: ${error.message}`;
  }
}

/**
 * 获取浏览器状态
 */
async function handleStatus() {
  try {
    if (!isConnected) {
      return `📊 浏览器状态: 未连接

💡 要复用已有 Chrome，请用 debug 模式启动:
   1. 关闭所有 Chrome 窗口
   2. 双击桌面的 "Chrome (Agent模式).bat"
   3. 或 Win+R 输入: chrome.exe --remote-debugging-port=9222

💡 或直接使用 navigate 启动新的 Chromium`;
    }

    const pages = context.pages();
    let currentUrl = '(空白页)';
    let currentTitle = '(无标题)';

    if (page && !page.isClosed()) {
      currentUrl = page.url();
      currentTitle = await page.title();
    }

    const modeText = connectionMode === 'cdp'
      ? `🔗 连接模式: CDP (复用现有 Chrome - 端口 ${CDP_PORT})`
      : '🔗 连接模式: 新建 Chromium';

    return `📊 浏览器状态:
✅ 运行中
${modeText}
📄 打开页面数: ${pages.length}
🔗 当前页面: ${currentUrl}
📝 标题: ${currentTitle}`;
  } catch (error) {
    return `❌ 获取状态失败: ${error.message}`;
  }
}

/**
 * 断开连接（不关闭浏览器）
 */
async function handleCloseBrowser() {
  try {
    if (!isConnected) {
      return '⚠️ 浏览器未连接';
    }

    if (connectionMode === 'cdp' && browser) {
      // CDP 模式：只断开连接，不关闭用户的 Chrome
      await browser.close();
      browser = null;
      context = null;
      page = null;
      connectionMode = null;
      isConnected = false;
      return '✅ 已断开与 Chrome 的连接\n\n💡 你的 Chrome 窗口保持打开，所有登录状态保留';
    } else if (context) {
      // 启动模式：关闭浏览器
      await context.close();
      browser = null;
      context = null;
      page = null;
      connectionMode = null;
      isConnected = false;
      return '✅ Chromium 已关闭';
    }
    return '⚠️ 浏览器未连接';
  } catch (error) {
    return `❌ 操作失败: ${error.message}`;
  }
}

/**
 * 显示帮助信息
 */
async function handleHelp() {
  return `
🌐 浏览器自动化 Skill - 命令列表

📌 复用已有 Chrome（推荐）:
   1. 关闭所有 Chrome 窗口
   2. Win+R 输入: chrome.exe --remote-debugging-port=9222
   3. 重新打开 Chrome，登录你需要的网站
   4. 现在 agent 会自动连接到这个 Chrome

📄 页面操作:
  navigate({url})          导航到 URL（复用现有页面）
  newPage({url?})          打开新页面
  screenshot({selector?})  截图（可指定元素）
  getContent({selector?})  获取页面内容
  close()                  关闭当前页面

👆 交互操作:
  click({selector})        点击元素
  fill({selector, value})  填写表单（会先清空）
  type({selector, text})   模拟打字（追加）
  select({selector, value}) 下拉选择
  check({selector, checked?}) 勾选/取消勾选

🔍 获取信息:
  getText({selector})      获取元素文本
  getValue({selector})     获取表单值
  getAttribute({selector, attribute}) 获取属性

⏳ 等待:
  wait({selector, timeout?}) 等待元素出现
  waitForNavigation()      等待页面跳转

⚡ 高级:
  evaluate({script})       执行 JavaScript
  upload({selector, filePath}) 上传文件
  press({key})             按键 (Enter/Escape/Tab等)
  hover({selector})        鼠标悬停
  scroll({direction, amount?}) 滚动页面

📊 状态:
  status()                 获取浏览器状态和连接模式
  closeBrowser()           断开连接/关闭浏览器

💡 选择器示例:
  CSS: #login-btn, .submit, input[name="email"]
  文本: text=登录, text=提交
  组合: button:has-text("提交")
  `.trim();
}

// Export for OpenClaw
module.exports = {
  // 页面操作
  handleNavigate,
  handleNewPage,
  handleScreenshot,
  handleGetContent,
  handleClose,

  // 交互操作
  handleClick,
  handleFill,
  handleType,
  handleSelect,
  handleCheck,

  // 获取信息
  handleGetText,
  handleGetValue,
  handleGetAttribute,

  // 等待
  handleWait,
  handleWaitForNavigation,

  // 高级操作
  handleEvaluate,
  handleUpload,
  handlePress,
  handleHover,
  handleScroll,

  // 状态
  handleStatus,
  handleCloseBrowser,
  handleHelp,
};
