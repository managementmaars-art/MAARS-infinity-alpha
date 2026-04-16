const http = require('http');

function fetchIPInfo() {
  return new Promise((resolve, reject) => {
    http.get('http://ip-api.com/json/?lang=zh-CN', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.status === 'success') {
            resolve(json);
          } else {
            reject(new Error('API返回失败'));
          }
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function main() {
  try {
    const info = await fetchIPInfo();
    console.log('=== IP 地理位置查询结果 ===');
    console.log(`IP 地址: ${info.query}`);
    console.log(`国家: ${info.country} (${info.countryCode})`);
    console.log(`省份: ${info.regionName}`);
    console.log(`城市: ${info.city}`);
    console.log(`ISP: ${info.isp}`);
    console.log(`时区: ${info.timezone}`);
  } catch (err) {
    console.error('获取失败:', err.message);
    process.exit(1);
  }
}

main();