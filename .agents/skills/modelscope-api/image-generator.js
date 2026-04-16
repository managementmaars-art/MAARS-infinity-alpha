const fs = require('fs');
const path = require('path');

// 配置
const config = {
    baseUrl: 'https://api-inference.modelscope.cn/',
    apiKey: process.env.MODELSCOPE_API_KEY || '',
    model: 'Tongyi-MAI/Z-Image-Turbo',
    outputDir: './generated-images',
    maxRetries: 30,
    pollInterval: 2000
};

// 检查 API Key
if (!config.apiKey) {
    console.error('❌ 错误: 未设置 MODELSCOPE_API_KEY 环境变量');
    console.error('   请设置环境变量: set MODELSCOPE_API_KEY=ms-xxx');
    process.exit(1);
}

// 通用请求头
const commonHeaders = {
    'Authorization': `Bearer ${config.apiKey}`,
    'Content-Type': 'application/json'
};

// 确保输出目录存在
if (!fs.existsSync(config.outputDir)) {
    fs.mkdirSync(config.outputDir, { recursive: true });
}

/**
 * 显示模型调用限制信息
 * @param {Object} headers - HTTP响应头
 * @returns {number|null} - 剩余调用次数
 */
function displayModelLimits(headers) {
    const modelRequestsRemaining = headers.get('modelscope-ratelimit-model-requests-remaining');
    const requestsRemaining = headers.get('modelscope-ratelimit-requests-remaining');

    console.log('\n📊 模型调用限制信息:');

    if (modelRequestsRemaining !== null) {
        console.log(`  模型剩余调用次数: ${modelRequestsRemaining}`);
    }

    if (requestsRemaining !== null) {
        console.log(`  总请求剩余次数: ${requestsRemaining}`);
    }

    const remaining = modelRequestsRemaining !== null
        ? parseInt(modelRequestsRemaining, 10)
        : (requestsRemaining !== null ? parseInt(requestsRemaining, 10) : null);

    if (remaining !== null) {
        console.log(`\n💡 还剩 ${remaining} 次模型调用`);
    }

    return remaining;
}

/**
 * 生成图片
 * @param {string} prompt - 生成提示词
 * @param {string} outputFilename - 输出文件名（可选）
 * @returns {Object} - 生成结果
 */
async function generateImage(prompt, outputFilename = null) {
    console.log(`\n=== 图片生成任务 ===`);
    console.log(`生成提示词: ${prompt}`);

    try {
        // 发送生成请求
        console.log('正在发送生成请求...');
        const response = await fetch(
            `${config.baseUrl}v1/images/generations`,
            {
                method: 'POST',
                headers: {
                    ...commonHeaders,
                    'X-ModelScope-Async-Mode': 'true'
                },
                body: JSON.stringify({
                    model: config.model,
                    prompt: prompt
                })
            }
        );

        // 显示模型限制信息
        displayModelLimits(response.headers);

        const data = await response.json();
        const taskId = data.task_id;
        console.log(`任务ID: ${taskId}`);

        // 轮询任务状态
        for (let i = 0; i < config.maxRetries; i++) {
            await new Promise(resolve => setTimeout(resolve, config.pollInterval));

            const result = await fetch(
                `${config.baseUrl}v1/tasks/${taskId}`,
                {
                    headers: {
                        ...commonHeaders,
                        'X-ModelScope-Task-Type': 'image_generation'
                    }
                }
            );

            const resultData = await result.json();
            const taskStatus = resultData.task_status;
            console.log(`轮询 ${i + 1}/${config.maxRetries}: 状态 ${taskStatus}`);

            if (taskStatus === 'SUCCEED') {
                // 显示任务完成后的限制信息
                console.log('\n📊 任务完成 - 模型调用限制信息:');
                displayModelLimits(result.headers);

                // 下载并保存图片
                const imageUrl = resultData.output_images[0];
                const imageResponse = await fetch(imageUrl);
                const imageBuffer = Buffer.from(await imageResponse.arrayBuffer());

                // 生成文件名
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const filename = outputFilename || `generated_${timestamp}.jpg`;
                const filepath = path.join(config.outputDir, filename);

                // 保存图片
                fs.writeFileSync(filepath, imageBuffer);
                console.log(`✅ 图片生成成功: ${filename}`);
                console.log(`   文件路径: ${path.resolve(filepath)}`);



                return {
                    success: true,
                    prompt,
                    filename,
                    filepath: path.resolve(filepath)
                };

            } else if (taskStatus === 'FAILED') {
                console.log(`❌ 图片生成失败`);
                return {
                    success: false,
                    prompt,
                    error: '任务失败'
                };
            }
        }

        console.log(`⏰ 轮询超时`);
        return {
            success: false,
            prompt,
            error: '轮询超时'
        };

    } catch (error) {
        console.log(`❌ 请求失败: ${error.message}`);
        return {
            success: false,
            prompt,
            error: error.message
        };
    }
}

// 命令行参数处理
function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {
        prompt: null,
        output: null
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '-p':
            case '--prompt':
                parsed.prompt = args[++i];
                break;
            case '-o':
            case '--output':
                parsed.output = args[++i];
                break;
            case '-h':
            case '--help':
                showHelp();
                process.exit(0);
                break;
        }
    }

    return parsed;
}

function showHelp() {
    console.log(`
使用方法: node image-generator.js [选项]

环境变量:
  MODELSCOPE_API_KEY   ModelScope API密钥（必需）

选项:
  -p, --prompt   <文本>    生成提示词（必需）
  -o, --output   <文件名>   输出文件名（可选）
  -h, --help               显示帮助信息

示例:
  set MODELSCOPE_API_KEY=ms-xxx
  node image-generator.js -p "一只可爱的猫咪"
  node image-generator.js -p "科幻城市夜景" -o city_night.jpg
`);
}

// 主函数
async function main() {
    const args = parseArgs();

    if (!args.prompt) {
        console.error('❌ 错误: 必须提供生成提示词');
        showHelp();
        process.exit(1);
    }

    console.log('=== 图片生成器 ===');
    console.log(`模型: ${config.model}`);
    console.log(`输出目录: ${path.resolve(config.outputDir)}`);
    console.log('='.repeat(50));

    const result = await generateImage(args.prompt, args.output);

    if (result.success) {
        console.log('\n✅ 生成完成！');
        console.log(`   输出文件: ${result.filepath}`);
        process.exit(0);
    } else {
        console.log('\n❌ 生成失败');
        console.log(`   错误: ${result.error}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(error => {
        console.error('❌ 程序错误:', error);
        process.exit(1);
    });
}

module.exports = { generateImage };
