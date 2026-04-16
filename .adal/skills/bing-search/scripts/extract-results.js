// Bing 搜索结果提取脚本
// 支持翻页和详情提取

/**
 * 提取 Bing 搜索结果
 * @param {number} maxResults - 最大结果数，默认10
 * @returns {Array} 搜索结果数组
 */
function extractBingResults(maxResults = 10) {
  const results = [];
  const items = document.querySelectorAll('#b_results > li');

  items.forEach((item, index) => {
    if (index >= maxResults) return;

    // 获取标题和链接
    const titleEl = item.querySelector('h2 a') || item.querySelector('.b_tpcn h2 a');
    const title = titleEl ? titleEl.textContent.trim() : '';
    let url = titleEl ? titleEl.href : '';

    // 提取真实URL（去除Bing重定向）
    if (url && url.includes('u=')) {
      const match = url.match(/[?&]u=([^&]+)/);
      if (match) {
        let b64 = match[1];
        while (b64.length % 4) b64 += '=';
        try { url = atob(b64); } catch(e) { url = b64; }
      }
    }

    // 获取描述/摘要
    let description = '';
    const descSelectors = [
      '.b_lineclamp2',
      '.b_lineclamp1',
      '.b_lineclamp3',
      '.b_caption p',
      '.b_1linewrap',
      '.b_desc'
    ];
    for (const selector of descSelectors) {
      const descEl = item.querySelector(selector);
      if (descEl && descEl.textContent.trim()) {
        description = descEl.textContent.trim();
        break;
      }
    }

    // 获取来源站点
    let site = '';
    const siteNameEl = item.querySelector('.tptt');
    const citeEl = item.querySelector('.b_attribution cite');

    if (siteNameEl) {
      site = siteNameEl.textContent.trim();
    } else if (citeEl) {
      site = citeEl.textContent.trim().split('›')[0].trim();
    }

    // 获取完整引用信息
    let citeFull = '';
    if (citeEl) {
      citeFull = citeEl.textContent.trim().replace(/翻译此结果$/, '').trim();
    }

    // 获取日期
    let date = '';
    const dateEl = item.querySelector('.b_snippetTime') || item.querySelector('[class*="snippetTime"]');
    if (dateEl) {
      date = dateEl.textContent.trim();
    }

    // 跳过"相关搜索"等非结果项
    if (title && !title.includes('的相关搜索')) {
      results.push({
        title,
        url,
        description,
        site,
        citeFull,
        date
      });
    }
  });

  return results;
}

/**
 * 跳转到下一页
 * @returns {boolean} 是否成功跳转
 */
function goToNextPage() {
  // 方法1: 查找"下一页"链接
  const nextPageLink = document.querySelector('a[href*="first="]') ||
    document.querySelector('[aria-label="下一页"]') ||
    document.querySelector('a[title="下一页"]') ||
    document.querySelector('.sb_pagN') ||
    document.querySelector('nav li[data-value] a');

  if (nextPageLink) {
    nextPageLink.click();
    return true;
  }
  return false;
}

/**
 * 通过URL跳转到指定页
 * @param {string} keyword - 搜索关键词
 * @param {number} page - 页码（从1开始）
 * @returns {string} 新页面URL
 */
function getPageUrl(keyword, page) {
  const first = (page - 1) * 10 + 1;
  return `https://www.bing.com/search?q=${encodeURIComponent(keyword)}&first=${first}`;
}

/**
 * 获取当前页码
 * @returns {number} 当前页码
 */
function getCurrentPage() {
  // 从URL解析
  const url = window.location.href;
  const match = url.match(/[?&]first=(\d+)/);
  if (match) {
    return Math.floor(parseInt(match[1]) / 10) + 1;
  }
  return 1;
}

/**
 * 获取搜索关键词
 * @returns {string} 当前搜索词
 */
function getSearchKeyword() {
  // 从URL获取
  const url = window.location.href;
  const match = url.match(/[?&]q=([^&]+)/);
  if (match) {
    return decodeURIComponent(match[1]);
  }
  // 从搜索框获取
  const searchBox = document.querySelector('input[name="q"]') || document.querySelector('#sb_form_q');
  return searchBox ? searchBox.value : '';
}

// 执行提取
extractBingResults(10);
