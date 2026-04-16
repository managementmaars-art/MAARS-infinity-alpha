const net = require('net');

const PROXY_PORT = 10808;

function fetchIPInfo(proxyPort = PROXY_PORT) {
  return new Promise((resolve, reject) => {
    const socket = new net.Socket();
    let connectedToProxy = false;
    let connectedToTarget = false;
    let responseData = '';

    socket.connect(proxyPort, '127.0.0.1', () => {
      const connectReq = [
        'CONNECT ip-api.com:80 HTTP/1.1',
        'Host: ip-api.com:80',
        'Proxy-Connection: Keep-Alive',
        '',
        ''
      ].join('\r\n');
      socket.write(connectReq);
    });

    socket.on('data', (chunk) => {
      if (!connectedToProxy) {
        const response = chunk.toString();
        if (response.includes('200') || response.includes('Connection established')) {
          connectedToProxy = true;
          const httpReq = [
            'GET /json/?lang=zh-CN HTTP/1.1',
            'Host: ip-api.com',
            'Connection: close',
            '',
            ''
          ].join('\r\n');
          socket.write(httpReq);
        }
      } else {
        responseData += chunk.toString();
      }
    });

    socket.on('end', () => {
      const body = responseData.split('\r\n\r\n')[1];
      if (body) {
        try {
          const json = JSON.parse(body);
          if (json.status === 'success') {
            resolve(json);
          } else {
            reject(new Error('API返回失败'));
          }
        } catch (e) {
          reject(e);
        }
      } else {
        reject(new Error('响应解析失败'));
      }
    });

    socket.on('error', (err) => {
      if (err.code === 'ECONNREFUSED') {
        reject(new Error(`代理端口 ${proxyPort} 未开启`));
      } else {
        reject(err);
      }
    });

    socket.setTimeout(10000, () => {
      socket.destroy();
      reject(new Error('请求超时'));
    });
  });
}

async function main() {
  const args = process.argv.slice(2);
  const port = args[0] ? parseInt(args[0]) : PROXY_PORT;

  console.log(`通过 HTTP 代理 localhost:${port} 查询IP信息...\n`);

  try {
    const info = await fetchIPInfo(port);
    console.log('=== 代理IP 地理位置查询结果 ===');
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