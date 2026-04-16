const fs = require('fs');
const path = require('path');

// 配置
const config = {
    baseUrl: 'https://api-inference.modelscope.cn/',
    apiKey: process.env.MODELSCOPE_API_KEY || '',
    model: 'Qwen/Qwen-Image-Edit-2511',
    outputDir: './edited-images',
    maxRetries: 60,
    pollInterval: 5000
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
 * 将图片文件转换为 base64 (带 data URI 前缀)
 * @param {string} imagePath - 图片文件路径
 * @returns {string} - base64 编码的图片数据 (带 data URI 前缀)
 */
function imageToBase64(imagePath) {
    const imageBuffer = fs.readFileSync(imagePath);
    const base64 = imageBuffer.toString('base64');
    
    const ext = path.extname(imagePath).toLowerCase();
    const mimeTypes = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp'
    };
    
    const mimeType = mimeTypes[ext] || 'image/jpeg';
    return `data:${mimeType};base64,${base64}`;
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
 * 编辑图片
 * @param {string} imagePath - 图片文件路径
 * @param {string} prompt - 编辑提示词
 * @param {string} outputFilename - 输出文件名（可选）
 * @returns {Object} - 编辑结果
 */
async function editImage(imagePath, prompt, outputFilename = null) {
    const absoluteImagePath = path.resolve(imagePath);
    
    console.log(`\n=== 图片编辑任务 ===`);
    console.log(`原始路径: ${imagePath}`);
    console.log(`绝对路径: ${absoluteImagePath}`);
    console.log(`编辑提示词: ${prompt}`);

    if (!fs.existsSync(absoluteImagePath)) {
        console.error(`❌ 错误: 图片文件不存在 - ${absoluteImagePath}`);
        return {
            success: false,
            error: '图片文件不存在',
            imagePath: absoluteImagePath,
            prompt
        };
    }

    try {
        // 将图片转换为 base64
        console.log('正在读取并编码图片...');
        const imageBase64 = imageToBase64(absoluteImagePath);
        console.log(`图片已编码,大小: ${(imageBase64.length / 1024).toFixed(2)} KB`);

        // 发送编辑请求
        console.log('正在发送编辑请求...');
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
                    prompt: prompt,
                    image_url: [imageBase64]
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
                const originalName = path.basename(imagePath, path.extname(imagePath));
                const filename = outputFilename || `edited_${originalName}_${timestamp}.jpg`;
                const filepath = path.join(config.outputDir, filename);

                // 保存图片
                fs.writeFileSync(filepath, imageBuffer);
                console.log(`✅ 图片编辑成功: ${filename}`);
                console.log(`   文件路径: ${path.resolve(filepath)}`);



                return {
                    success: true,
                    originalImage: absoluteImagePath,
                    prompt,
                    filename,
                    filepath: path.resolve(filepath)
                };

            } else if (taskStatus === 'FAILED') {
                console.log(`❌ 图片编辑失败`);
                return {
                    success: false,
                    originalImage: absoluteImagePath,
                    prompt,
                    error: '任务失败'
                };
            }
        }

        console.log(`⏰ 轮询超时`);
        return {
            success: false,
            originalImage: absoluteImagePath,
            prompt,
            error: '轮询超时'
        };

    } catch (error) {
        console.log(`❌ 请求失败: ${error.message}`);
        return {
            success: false,
            originalImage: absoluteImagePath,
            prompt,
            error: error.message
        };
    }
}

// 命令行参数处理
function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {
        imagePath: null,
        prompt: null,
        output: null
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '-i':
            case '--image':
                parsed.imagePath = args[++i];
                break;
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
使用方法: node image-editor.js [选项]

环境变量:
  MODELSCOPE_API_KEY   ModelScope API密钥（必需）

选项:
  -i, --image    <路径>    输入图片文件路径（必需）
  -p, --prompt   <文本>    编辑提示词（必需）
  -o, --output   <文件名>   输出文件名（可选）
  -h, --help               显示帮助信息

示例:
  set MODELSCOPE_API_KEY=ms-xxx
  node image-editor.js -i ./photo.jpg -p "给图中的人戴上墨镜"
  node image-editor.js -i ./dog.png -p "给狗戴上生日帽" -o birthday_dog.jpg
`);
}

// 主函数
async function main() {
    const args = parseArgs();

    if (!args.imagePath || !args.prompt) {
        console.error('❌ 错误: 必须提供图片路径和编辑提示词');
        showHelp();
        process.exit(1);
    }

    console.log('=== 图片编辑器 ===');
    console.log(`模型: ${config.model}`);
    console.log(`输出目录: ${path.resolve(config.outputDir)}`);
    console.log('='.repeat(50));

    const result = await editImage(args.imagePath, args.prompt, args.output);

    if (result.success) {
        console.log('\n✅ 编辑完成！');
        console.log(`   输出文件: ${result.filepath}`);
        process.exit(0);
    } else {
        console.log('\n❌ 编辑失败');
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

module.exports = { editImage };
