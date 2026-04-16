// Bing 搜索完整脚本
// 使用方法: 通过 browser_evaluate 工具在 Bing 搜索页面执行

function bingSearch(keyword) {
  // 1. 查找搜索框并输入关键词
  const searchBox = document.querySelector('input[name="q"]') ||
                    document.querySelector('#sb_form_q') ||
                    document.querySelector('input[type="search"]') ||
                    document.querySelector('.sb_form input');

  if (!searchBox) {
    return { error: '找不到搜索框' };
  }

  // 清空并输入关键词
  searchBox.value = keyword;

  // 2. 提交搜索 (按 Enter)
  const form = searchBox.closest('form') || document.querySelector('#sb_form');
  if (form) {
    form.submit();
  } else {
    searchBox.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
  }

  return { status: 'search_submitted', keyword: keyword };
}

// 执行搜索
function executeSearch(keyword) {
  const result = bingSearch(keyword);

  // 等待页面加载后提取结果
  return new Promise((resolve) => {
    setTimeout(() => {
      const results = window.extractBingResults ?
        window.extractBingResults(10) :
        // 如果上面的脚本没加载，手动提取
        (function() {
          const r = [];
          const items = document.querySelectorAll('#b_results > li');
          items.forEach((item, i) => {
            if (i >= 10) return;
            const t = item.querySelector('h2 a');
            if (t) {
              r.push({ title: t.textContent.trim(), url: t.href, description: '' });
            }
          });
          return r;
        })();

      resolve({
        search: result,
        results: results
      });
    }, 2000); // 等待2秒让搜索结果加载
  });
}

// 如果是直接执行（不是被调用），执行搜索
if (typeof window !== 'undefined' && window.location) {
  // 浏览器环境
  window.bingSearch = bingSearch;
}
