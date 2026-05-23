# work-order-flow

AI Agent 通用工单驱动开发工作流 —— 从接收工单到交付的全流程规范。

## What

一个 **SKILL.md** 文件，定义了 AI 编码助手处理工单/需求的标准工作流。不绑定任何特定平台，支持 Cursor、Claude Code、Codex、Windsurf、Tare、Qoder 等任何能读取文件的 AI Agent。

核心功能：
- **6 阶段工作流**：接收识别 → 解析文档 → 分析验证 → 规划设计 → 执行迭代 → 收尾输出
- **三级 Review 机制**：模块级 → 全局自检 → 用户验收
- **轻量留痕**：spec.md + progress.md 双文档结构
- **日报自动生成**：支持个性化风格学习
- **反馈闭环**：工作流缺陷自动提 Issue，个人偏好本地保存

## Install

```bash
# 方式一：npx（推荐）
npx @sw-liux/work-order-flow install

# 指定平台
npx @sw-liux/work-order-flow install --platform cursor
npx @sw-liux/work-order-flow install --platform claude-code

# 指定自定义路径
npx @sw-liux/work-order-flow install --path ~/my-skills/work-order-flow
```

```bash
# 方式二：Git clone
git clone https://github.com/SW-Liux/work-order-flow.git ~/.cursor/skills/work-order-flow
```

```bash
# 方式三：直接下载
# 从 GitHub 页面下载 SKILL.md 和 scripts/ 文件夹，放到任意位置
```

## Usage

安装后，在 AI 对话中引用即可自动触发。例如：

- 发送一个工单 PDF / Word 文档
- 说 "帮我做这个需求"、"看下这个 bug"
- 发送聊天记录截图

AI 会自动按照 SKILL.md 中定义的工作流执行。

如果平台不支持 skills 自动加载，手动告诉 AI：

> 请读取 `~/.cursor/skills/work-order-flow/SKILL.md` 并按其中的工作流执行。

## Platform Support

| Platform | Install Path | Auto-detect |
|----------|-------------|-------------|
| Cursor | `~/.cursor/skills/work-order-flow/` | ✅ |
| Claude Code | `~/.claude/skills/work-order-flow/` | ✅ |
| Codex / GPT Agent | `~/.agents/skills/work-order-flow/` | ✅ |
| Windsurf | `~/.windsurf/skills/work-order-flow/` | ✅ |
| Others | Any path (use `--path`) | Manual |

## Feedback

发现工作流问题？欢迎提 Issue：[GitHub Issues](https://github.com/SW-Liux/work-order-flow/issues)

如果你在使用过程中遇到工作流缺陷，AI 会自动帮你整理反馈内容并提交 Issue，你只需确认即可。

## License

MIT
