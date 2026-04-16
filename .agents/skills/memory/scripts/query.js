#!/usr/bin/env node

/**
 * Memory 检索：按 tagExpr 查询记忆
 * GET {MEMORY_API_BASE_URL}/api/agent/v1/memories?tagExpr=...&limit=...
 *
 * 用法:
 *   node scripts/query.js "work" [--limit 10]
 *   node scripts/query.js "work AND important" [--limit 20]
 *   node scripts/query.js "(work OR personal) AND important"
 * tagExpr 中的空格会在 URL 中编码为 %20
 */

import https from 'https';

const API_BASE = process.env.MEMORY_API_BASE_URL || 'https://www.mixlab.top';

function parseArgs() {
    const args = process.argv.slice(2);
    let tagExpr = '';
    let limit = 10;
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--limit' && args[i + 1] != null) {
            limit = parseInt(args[++i], 10) || 10;
        } else if (!args[i].startsWith('--')) {
            tagExpr = args[i];
            break;
        }
    }
    return { tagExpr, limit };
}

function getMemories(tagExpr, limit) {
    return new Promise((resolve, reject) => {
        const apiKey = process.env.MEMORY_API_KEY;
        if (!apiKey) {
            reject(new Error('MEMORY_API_KEY is not set.'));
            return;
        }
        const encoded = encodeURIComponent(tagExpr);
        const url = new URL(API_BASE);
        const pathWithQuery = `${url.pathname.replace(/\/$/, '')}/api/agent/v1/memories`.replace(/\/\/+/g, '/') + `?tagExpr=${encoded}&limit=${limit}`;

        const req = https.request(
            {
                hostname: url.hostname,
                port: url.port || 443,
                path: pathWithQuery.startsWith('/') ? pathWithQuery : '/' + pathWithQuery,
                method: 'GET',
                headers: {
                    Authorization: `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
            },
            (res) => {
                const chunks = [];
                res.on('data', (c) => chunks.push(c));
                res.on('end', () => {
                    const data = Buffer.concat(chunks).toString('utf8');
                    if (res.statusCode >= 300) {
                        reject(new Error(`GET 返回 ${res.statusCode}: ${data.slice(0, 300)}`));
                        return;
                    }
                    try {
                        resolve(data ? JSON.parse(data) : []);
                    } catch {
                        resolve({ raw: data });
                    }
                });
            }
        );
        req.on('error', reject);
        req.end();
    });
}

function main() {
    const { tagExpr, limit } = parseArgs();
    if (!tagExpr) {
        console.error('用法: node scripts/query.js "<tagExpr>" [--limit N]');
        process.exit(1);
    }
    getMemories(tagExpr, limit)
        .then((data) => console.log(JSON.stringify(data, null, 2)))
        .catch((e) => {
            console.error(e.message);
            process.exit(1);
        });
}

main();
