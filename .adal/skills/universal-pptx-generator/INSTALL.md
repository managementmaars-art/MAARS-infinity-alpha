# Universal PPTX Generator Skill 安装指南

## 安装方法

### 方法 1：手动安装

1. 在你的项目根目录下创建 skill 目录：

```bash
mkdir -p .codebuddy/skills/universal-pptx-generator
```

2. 将 `SKILL.md` 文件复制到该目录：

```bash
cp SKILL.md .codebuddy/skills/universal-pptx-generator/
```

3. 重启 CodeBuddy 或刷新技能列表

### 方法 2：通过 Git 克隆

```bash
# 克隆仓库
git clone https://github.com/ajaxhe/universal-pptx-generator-skill.git

# 复制到你的项目
cp universal-pptx-generator-skill/SKILL.md your-project/.codebuddy/skills/universal-pptx-generator/
```

## 目录结构

安装完成后，你的项目应该有以下结构：

```
your-project/
├── .codebuddy/
│   └── skills/
│       └── universal-pptx-generator/
│           └── SKILL.md
└── ... 其他项目文件
```

## 验证安装

在 CodeBuddy 中输入以下命令验证技能是否正确安装：

```
/universal-pptx-generator
```

如果看到技能加载成功的提示，说明安装完成。

## 使用前准备

在使用技能前，确保项目环境中安装了必要的依赖：

```bash
npm install pptxgenjs
```

## 故障排除

### 技能未显示

1. 确保 `SKILL.md` 文件位于正确的目录
2. 检查文件权限
3. 尝试重启 CodeBuddy

### 生成 PPT 失败

1. 确保已安装 `pptxgenjs` 依赖
2. 检查 Node.js 版本是否 >= 14
3. 确保模板文件路径正确

## 获取帮助

如有问题，请在 GitHub Issues 中提交：
https://github.com/ajaxhe/universal-pptx-generator-skill/issues
