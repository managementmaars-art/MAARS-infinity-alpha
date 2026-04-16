const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');
const cheerio = require('cheerio');
const axios = require('axios');

// 配置
const USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1';



async function main() {
  // 1. 校验参数
  const url = process.argv[2];
  const domain = process.argv[3]; // 领域分类，第二个参数传入，不传则不分类
  if (!url || !url.startsWith('https://mp.weixin.qq.com/s/')) {
    console.error('❌ 请输入有效的微信公众号文章URL，格式：https://mp.weixin.qq.com/s/xxx [领域分类]');
    console.error('📌 示例1：node scripts/fetch.js https://mp.weixin.qq.com/s/xxx （无分类）');
    console.error('📌 示例2：node scripts/fetch.js https://mp.weixin.qq.com/s/xxx AI （分类为AI）');
    process.exit(1);
  }

  // 2. 创建跨平台兼容临时目录
  const timestamp = Date.now();
  // 自动获取各系统默认临时目录：Linux/Mac=/tmp, Windows=%TEMP%
  const systemTempDir = os.tmpdir();
  // 路径结构：系统临时目录/wechat-article/wechat-article-时间戳/
  const baseDir = path.join(systemTempDir, 'wechat-article');
  const articleDir = path.join(baseDir, `wechat-article-${timestamp}`);
  const attachmentsDir = path.join(articleDir, 'attachments');
  // 递归创建目录，跨平台兼容
  fs.mkdirSync(attachmentsDir, { recursive: true });
  console.log(`📂 创建临时目录：${articleDir}`);

  try {
    // 3. 抓取网页HTML
    console.log('🌐 正在抓取文章内容...');
    const response = await axios.get(url, {
      headers: { 'User-Agent': USER_AGENT },
      timeout: 10000
    });
    const html = response.data;
    const $ = cheerio.load(html);

    // 4. 提取元数据（优先从全局变量提取，更稳定）
    const htmlStr = response.data;
    // 匹配全局变量
    const officialAccountName = htmlStr.match(/var nickname = htmlDecode\("([^"]+)"\)/)?.[1] || htmlStr.match(/var nickname = "([^"]+)"/)?.[1] || '未知公众号';
    const title = htmlStr.match(/var msg_title = '([^']+)'/)?.[1]?.replace(/\.html\(false\)/, '') || $('#activity-name').text().trim() || $('h1').first().text().trim() || '微信公众号文章';
    const author = htmlStr.match(/var author = "([^"]*)"/)?.[1] || $('.rich_media_meta_text').text().trim() || $('#js_author_name').text().trim() || '';
    const coverImage = htmlStr.match(/var msg_cdn_url = "([^"]+)"/)?.[1] || '';
    // 提取发布时间
    const publishTime = htmlStr.match(/var createTime = '([^']+)'/)?.[1] || htmlStr.match(/create_time: JsDecode\('([^']+)'\)/)?.[1] || '未知时间';
    // 公众号头像
    const officialAccountAvatar = htmlStr.match(/<img class="profile_avatar_img" src="([^"]+)"/)?.[1] || '';
    
    console.log(`📝 文章标题：${title}`);
    console.log(`📢 公众号：${officialAccountName}`);
    if (author) console.log(`👤 作者：${author}`);
    console.log(`⏰ 发布时间：${publishTime}`);

    // 5. 提取正文并处理图片
    const $content = $('#js_content');
    if ($content.length === 0) throw new Error('未找到文章正文内容');

    // 下载所有图片并替换路径
    console.log('🖼️  正在下载图片...');
    const imgElements = $content.find('img');
    let downloadedCount = 0;

    for (let i = 0; i < imgElements.length; i++) {
      const $img = $(imgElements[i]);
      let imgUrl = $img.attr('data-src') || $img.attr('src');
      if (!imgUrl) continue;

      // 补全协议
      if (imgUrl.startsWith('//')) imgUrl = 'https:' + imgUrl;
      if (!imgUrl.startsWith('http')) continue;

      // 生成文件名
      const ext = path.extname(new URL(imgUrl).pathname) || '.jpg';
      const imgName = `img-${i + 1}${ext}`;
      const imgPath = path.join(attachmentsDir, imgName);

      // 下载图片
      try {
        const imgResponse = await axios.get(imgUrl, {
          responseType: 'arraybuffer',
          headers: { 'User-Agent': USER_AGENT },
          timeout: 5000
        });
        fs.writeFileSync(imgPath, imgResponse.data);
        // 替换为相对路径
        $img.attr('src', `./attachments/${imgName}`);
        $img.removeAttr('data-src');
        downloadedCount++;
      } catch (e) {
        console.log(`⚠️  下载图片失败：${imgUrl}`);
      }
    }
    console.log(`✅ 共下载 ${downloadedCount} 张图片`);

    // 6. 转换为Markdown
    console.log('🔄 正在转换为Markdown格式...');
    let markdown = await htmlToMarkdown($, $content);

    // 7. 生成Obsidian Front Matter + 正文
    // 提取纯文本内容，固定取前150字作为摘要
    const textWithoutImages = markdown.replace(/!\[.*?\]\(.*?\)/g, ''); // 完全删除图片Markdown标记
    const plainText = textWithoutImages.replace(/[#*`\-+>]/g, '').replace(/\n+/g, ' ').replace(/\s+/g, ' ').trim();
    let description = plainText.length > 150 ? plainText.slice(0, 150) + '...' : plainText;
    // 替换冒号避免YAML语法错误
    description = description.replace(/:/g, '：').replace(/\n/g, ' ');
    // 处理发布时间为YYYY-MM-DD格式
    const createdDate = publishTime.match(/\d{4}-\d{2}-\d{2}/)?.[0] || new Date().toISOString().slice(0, 10);
    // 构造Front Matter
    let frontMatter = '---\n';
    frontMatter += `title: ${title.replace(/:/g, '：')}\n`; // 替换冒号避免YAML语法错误
    frontMatter += `source: ${url}\n`;
    // 始终保留author字段，无作者则留空
    frontMatter += `author:\n  - "[[${author ? author.replace(/:/g, '：') : ''}]]"\n`;
    frontMatter += `published: ${officialAccountName}微信公众号\n`;
    frontMatter += `created: ${createdDate}\n`;
    frontMatter += `description: ${description.replace(/:/g, '：').replace(/\n/g, ' ')}\n`;
    frontMatter += `tags:\n  - 摘录\n`;
    // 仅当分类存在时添加分类标签
    if (domain) {
      frontMatter += `  - ${domain}\n`;
    }
    frontMatter += '---\n\n';

    // 正文部分（去掉重复元数据，直接显示标题和内容）
    const content = `# ${title}\n\n${markdown}`;
    const finalMarkdown = frontMatter + content;

    // 8. 生成安全文件名（兼容Windows/Linux/Mac，替换非法字符）
    const safeTitle = title.replace(/[\\/:*?"<>|]/g, '_').replace(/\s+/g, '-').slice(0, 100); // 限制文件名长度
    const fileName = domain ? `${domain}-${safeTitle}.md` : `${safeTitle}.md`;
    const mdPath = path.join(articleDir, fileName);

    // 保存文件
    fs.writeFileSync(mdPath, finalMarkdown, 'utf8');

    console.log('\n🎉 抓取完成！');
    console.log(`📄 Markdown文件：${mdPath}`);
    console.log(`🖼️  图片目录：${attachmentsDir}`);

  } catch (error) {
    console.error('❌ 抓取失败：', error.message);
    process.exit(1);
  }
}

// HTML转Markdown函数
async function htmlToMarkdown($, $content) {
  let markdown = '';

  function processNode(el) {
    const $el = $(el);
    const tagName = el.tagName ? el.tagName.toLowerCase() : '';

    if (el.type === 'text') {
      const text = $(el).text().replace(/\s+/g, ' ').trim();
      return text ? text + ' ' : '';
    }

    switch (tagName) {
      case 'h1': return `\n# ${$el.text().trim()}\n\n`;
      case 'h2': return `\n## ${$el.text().trim()}\n\n`;
      case 'h3': return `\n### ${$el.text().trim()}\n\n`;
      case 'h4': return `\n#### ${$el.text().trim()}\n\n`;
      
      case 'p':
        let pContent = '';
        $el.contents().each((i, child) => { pContent += processNode(child); });
        return pContent.trim() ? `${pContent.trim()}\n\n` : '';
      
      case 'strong':
      case 'b': return `**${$el.text().trim()}**`;
      case 'em':
      case 'i': return `*${$el.text().trim()}*`;
      case 'u': return `<u>${$el.text().trim()}</u>`;
      case 's': return `~~${$el.text().trim()}~~`;
      
      case 'img':
        const src = $el.attr('src') || '';
        const alt = $el.attr('alt') || '';
        return src ? `\n![${alt}](${src})\n\n` : '';
      
      case 'a':
        const href = $el.attr('href') || '';
        const linkText = $el.text().trim();
        return (href && linkText) ? `[${linkText}](${href})` : linkText;
      
      case 'ul':
      case 'ol':
        let listContent = '\n';
        $el.children('li').each((j, li) => {
          let liContent = '';
          $(li).contents().each((k, child) => { liContent += processNode(child); });
          listContent += `- ${liContent.trim()}\n`;
        });
        return listContent + '\n';
      
      case 'blockquote':
        let quoteContent = '';
        $el.contents().each((i, child) => { quoteContent += processNode(child); });
        return quoteContent.trim() ? `\n> ${quoteContent.trim().replace(/\n/g, '\n> ')}\n\n` : '';
      
      case 'pre':
      case 'code':
        const code = $el.text().trim();
        return code ? `\n\`\`\`\n${code}\n\`\`\`\n\n` : '';
      
      case 'br': return '\n';
      case 'hr': return '\n---\n\n';
      
      case 'div':
      case 'section':
        let divContent = '';
        $el.contents().each((i, child) => { divContent += processNode(child); });
        return divContent;
      
      case 'span':
        let spanContent = '';
        $el.contents().each((i, child) => { spanContent += processNode(child); });
        return spanContent;
      
      default:
        return $el.text().trim() ? $el.text().trim() + ' ' : '';
    }
  }

  $content.contents().each((i, el) => {
    markdown += processNode(el);
  });

  return markdown.replace(/\n{3,}/g, '\n\n').trim();
}

main();
