#!/usr/bin/env node

/**
 * Memory 提交：创建一条记忆
 * POST {MEMORY_API_BASE_URL}/api/agent/v1/memories
 * Body: { source, category, content, tags }
 *
 * 用法:
 *   node scripts/submit.js --source "用户口述" --category "笔记" --content "内容" --tags "tag1,tag2"
 * 或从 stdin 读 JSON 一行：
 *   echo '{"source":"x","category":"y","content":"z","tags":["a","b"]}' | node scripts/submit.js --stdin
 */

import https from 'https';
import { createInterface } from 'readline';

const API_BASE = process.env.MEMORY_API_BASE_URL || 'https://www.mixlab.top';

function parseArgs() {
    const args = process.argv.slice(2);
    const out = { source: '', category: '', content: '', tags: [], stdin: false };
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--stdin') {
            out.stdin = true;
        } else if (args[i] === '--source' && args[i + 1] != null) {
            out.source = args[++i];
        } else if (args[i] === '--category' && args[i + 1] != null) {
            out.category = args[++i];
        } else if (args[i] === '--content' && args[i + 1] != null) {
            out.content = args[++i];
        } else if (args[i] === '--tags' && args[i + 1] != null) {
            out.tags = args[++i].split(',').map((t) => t.trim()).filter(Boolean);
        }
    }
    return out;
}

function postMemory(body) {
    return new Promise((resolve, reject) => {
        const apiKey = process.env.MEMORY_API_KEY;
        if (!apiKey) {
            reject(new Error('MEMORY_API_KEY is not set.'));
            return;
        }
        const url = new URL(API_BASE);
        const pathSeg = `${url.pathname.replace(/\/$/, '')}/api/agent/v1/memories`.replace(/\/\/+/g, '/');
        const pathStr = pathSeg.startsWith('/') ? pathSeg : '/' + pathSeg;
        const payload = JSON.stringify(body);
        const opts = {
            hostname: url.hostname,
            port: url.port || 443,
            path: pathStr,
            method: 'POST',
            headers: {
                Authorization: `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(payload, 'utf8'),
            },
        };
        const req = https.request(opts, (res) => {
            const chunks = [];
            res.on('data', (c) => chunks.push(c));
            res.on('end', () => {
                const data = Buffer.concat(chunks).toString('utf8');
                if (res.statusCode >= 300) {
                    reject(new Error(`POST 返回 ${res.statusCode}: ${data.slice(0, 300)}`));
                    return;
                }
                try {
                    resolve(data ? JSON.parse(data) : {});
                } catch {
                    resolve({ raw: data });
                }
            });
        });
        req.on('error', reject);
        req.write(payload);
        req.end();
    });
}

function main() {
    const opts = parseArgs();

    if (opts.stdin) {
        const rl = createInterface({ input: process.stdin });
        let line = '';
        rl.on('line', (l) => (line = l));
        rl.on('close', () => {
            try {
                const body = JSON.parse(line);
                postMemory(body)
                    .then((data) => console.log(JSON.stringify(data, null, 2)))
                    .catch((e) => {
                        console.error(e.message);
                        process.exit(1);
                    });
            } catch (e) {
                console.error('无效 JSON:', e.message);
                process.exit(1);
            }
        });
        return;
    }

    if (!opts.content) {
        console.error('用法: node scripts/submit.js --source "..." --category "..." --content "..." --tags "t1,t2"');
        console.error('  或: echo \'{"source":"x","category":"y","content":"z","tags":["a"]}\' | node scripts/submit.js --stdin');
        process.exit(1);
    }

    const body = {
        source: opts.source || 'Agent',
        category: opts.category || '笔记',
        content: opts.content,
        tags: Array.isArray(opts.tags) && opts.tags.length ? opts.tags : ['未分类'],
    };

    postMemory(body)
        .then((data) => console.log(JSON.stringify(data, null, 2)))
        .catch((e) => {
            console.error(e.message);
            process.exit(1);
        });
}

main();
