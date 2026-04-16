#!/usr/bin/env node

const fs = require("fs");
const https = require("https");

// 解析命令行参数
function parseArgs() {
  const args = {
    text: "",
    model: "mimo-v2-tts",
    format: "mp3",
    voice: "mimo_default",
    output: null,
  };

  const argv = process.argv.slice(2);

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];

    switch (arg) {
      case "--text":
      case "-t":
        if (next && !next.startsWith("--")) {
          args.text = next;
          i++;
        }
        break;
      case "--model":
      case "-m":
        if (next && !next.startsWith("--")) {
          args.model = next;
          i++;
        }
        break;
      case "--format":
      case "-f":
        if (next && !next.startsWith("--")) {
          args.format = next;
          i++;
        }
        break;
      case "--voice":
        if (next && !next.startsWith("--")) {
          args.voice = next;
          i++;
        }
        break;
      case "--output":
      case "-o":
        if (next && !next.startsWith("--")) {
          args.output = next;
          i++;
        }
        break;
      case "--help":
      case "-h":
        printHelp();
        process.exit(0);
    }
  }

  if (!args.text) {
    console.error("错误: 请使用 --text 指定要转换的文本");
    process.exit(1);
  }

  if (!args.output) {
    args.output = `output.${args.format}`;
  }

  return args;
}

function printHelp() {
  console.log(`
MiMo TTS 语音合成工具

用法: node tts.js [选项]

必需参数:
  --text, -t <文本>        要转换为语音的文本内容

可选参数:
  --model, -m <模型>       TTS 模型 (默认: mimo-v2-tts)
  --format, -f <格式>      输出格式 mp3/wav (默认: mp3)
  --voice <音色>           音色选择 (默认: mimo_default)
                           可选: mimo_default, default_zh, default_en
  --output, -o <路径>     输出文件路径 (默认: output.<格式>)
  --help, -h              显示帮助信息

示例:
  node tts.js --text "你好世界"
  node tts.js --text "Hello" --voice default_en --format mp3
  `);
}

// 检查环境变量
function checkApiKey() {
  const apiKey = process.env.MIMO_API_KEY;
  if (!apiKey) {
    console.error("╔══════════════════════════════════════════════════════════╗");
    console.error("║                    MiMo TTS 配置引导                        ║");
    console.error("╠══════════════════════════════════════════════════════════╣");
    console.error("║  看起来还没有配置 MiMo API Key，让我来帮你：              ║");
    console.error("║                                                          ║");
    console.error("║  1. 访问以下网址获取 API Key:                             ║");
    console.error("║     https://platform.xiaomimimo.com/#/console/api-keys   ║");
    console.error("║                                                          ║");
    console.error("║  2. 获取后，运行以下命令设置环境变量:                     ║");
    console.error("║     Linux/macOS:                                         ║");
    console.error('║       export MIMO_API_KEY="你的API Key"                  ║');
    console.error("║     Windows (PowerShell):                                ║");
    console.error('║       $env:MIMO_API_KEY = "你的API Key"                  ║');
    console.error("║                                                          ║");
    console.error("║  3. 设置完成后，重新运行 TTS 命令即可                    ║");
    console.error("╚══════════════════════════════════════════════════════════╝");
    process.exit(1);
  }
  return apiKey;
}

// 调用 TTS API
function callTTSApi(apiKey, params) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: params.model,
      messages: [
        {
          role: "user",
          content: "",
        },
        {
          role: "assistant",
          content: params.text,
        },
      ],
      audio: {
        format: params.format,
        voice: "mimo_default",
      },
    });

    const options = {
      hostname: "api.xiaomimimo.com",
      path: "/v1/chat/completions",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "api-key": apiKey,
      },
    };

    const req = https.request(options, (res) => {
      const chunks = [];

      res.on("data", (chunk) => {
        chunks.push(chunk);
      });

      res.on("end", () => {
        try {
          const body = Buffer.concat(chunks).toString();
          const result = JSON.parse(body);

          if (result.error) {
            reject(new Error(result.error.message || "API 错误"));
            return;
          }

          if (
            result.choices &&
            result.choices[0] &&
            result.choices[0].message
          ) {
            const audioData = result.choices[0].message.audio;
            if (audioData && audioData.data) {
              resolve({
                audioData: audioData.data,
                audioId: audioData.id,
              });
              return;
            }
          }

          reject(new Error("未获取到音频数据"));
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on("error", (e) => {
      reject(e);
    });

    req.write(data);
    req.end();
  });
}

// 保存音频文件
function saveAudioFile(audioData, outputPath) {
  const buffer = Buffer.from(audioData, "base64");
  fs.writeFileSync(outputPath, buffer);
  console.log(`音频已保存到: ${outputPath}`);
  return outputPath;
}

// 主函数
async function main() {
  const args = parseArgs();
  const apiKey = checkApiKey();

  console.log("正在生成语音...");
  console.log(`文本: ${args.text}`);
  console.log(`模型: ${args.model}`);
  console.log(`格式: ${args.format}`);

  try {
    const result = await callTTSApi(apiKey, args);
    const outputPath = saveAudioFile(result.audioData, args.output);
    console.log(`完成! 音频ID: ${result.audioId}`);
  } catch (e) {
    console.error("错误:", e.message);
    process.exit(1);
  }
}

main();
