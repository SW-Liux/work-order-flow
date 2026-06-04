# Changelog

All notable changes to this skill will be documented in this file.

## [1.10.0] - 2026-06-04

### Added
- **跨项目文件搜索能力**（Phase 2.4.1）：通过 Shell + `fd`/`rg` 突破 workspace 范围限制
  - `fd`：按文件名全盘搜索（毫秒级）
  - `rg`：按文件内容全盘搜索（支持正则、上下文显示）
  - 明确了 IDE 内置搜索 vs Shell 搜索的优先级规则
  - 安装命令：`winget install sharkdp.fd BurntSushi.ripgrep.MSVC`
- **Cursor Rule**：创建 `cross-project-search.mdc`（alwaysApply），让非 Skill 场景下也有跨项目搜索意识

## [1.9.0] - 2026-05-26

### Added
- **锚定偏差防御机制**（Phase 4.4.1）：连续 2-3 次修改仍未解决问题时，强制跳出当前思路
  - 四步强制重审流程：验证存在性 → 对比参照物 → 区分"缺失"与"错误" → 重新定位
  - 长对话锚定预防策略：主动建议压缩上下文、全新视角重审
  - 反面案例记录：高喷 drawDesignCircle 缺失事件

### Changed
- Phase 4.4 上下文对齐原则扩展：新增连续失败时的升级处理策略

## [1.8.0] - 2026-05-23

### Added
- **GitHub 反馈自动提交机制**：AI 主动替用户执行 `gh issue create` / `gh pr create`，用户只需确认"行/不行"
- **npx 一键安装**：`npx @xxx/work-order-flow install` 自动检测平台并安装到对应 skills 目录
- **对话压缩后的上下文确认机制**：Phase -1 新增规则，检测到对话压缩/摘要后必须先确认工作焦点

### Changed
- **反馈提交流程重构**：从"建议用户提交"改为"AI 全权代办，用户只做决策"
- **分发方式排序**：npx 安装提升为第一推荐（最低门槛），Git 仓库降为第二（团队协作场景）

## [1.6.0] - 2026-05-23

### Added
- **日报个性化机制**：Phase 5.1 支持学习用户日报风格，保存本地模板 `local/daily-report-style.md`
- **Skills 分发机制**：平台无关的三级分发方案（Git 仓库 / 平台适配 / 直接复制）
- **反馈优化机制**：工作流缺陷 vs 个人偏好二分法，低频精准触发
- **版本更新提醒**：frontmatter 版本号 + `local/version.txt` 对比 + CHANGELOG 变更摘要
- **保底机制**：无 Git 用户通过维护者联系方式提交反馈
- **维护者信息**：文件末尾配置联系方式
- **CHANGELOG.md**：强制维护变更日志
- **`.gitignore`**：排除 `local/` 个人配置目录

### Changed
- 定位从 Cursor 专属调整为**平台无关的通用 Skills**
- 分发机制以 Git 仓库为主推荐，Cursor Plugin 降为可选增强
- 反馈触发策略优化：正常工作时不触发，情绪信号时精准触发

## [1.5.0] - 2026-05-22

### Added
- **提交建议机制**：AI 在适当时机主动建议 git commit，提供中文 commit 信息草稿
- **批量零散优化模式**：处理多个分散小优化点时的上下文隔离方案
- **阶段回退规则**：非线性流程处理，支持轻量回退
- **反面案例记录**：git stash apply staged 状态污染问题及解决方案

## [1.4.0] - 2026-05-22

### Added
- **三级 Review 机制**（Phase 4.5）：L1 模块级 → L2 全局自检 → L3 用户验收
- **移植残留扫描规则**：Review 时强制检查未替换的旧工艺名称
- **细粒度上下文回读**（Phase 4.1.1）：执行每个模块前重新读取相关需求段落

### Fixed
- L1 Review 增加"禁止基于模式匹配的推断"规则

## [1.3.0] - 2026-05-21

### Added
- **工单评论检查**（Phase 2.2）：需求文档不是唯一真相来源
- **图片阅读**（Phase 1.2）：支持读取文档中的嵌入图片
- **轻量留痕**（Phase 3.4）：spec.md + progress.md 双文档结构

## [1.2.0] - 2026-05-21

### Added
- **会话恢复**（Phase -1）：通过 spec.md + progress.md 恢复上下文
- **容错机制**：文档不可靠时的四级降级策略

## [1.1.0] - 2026-05-21

### Added
- **完整度检查**（Phase 4.6）：需求-实现全面对照
- **交付总结文档**（Phase 5.3）：需求概览 + 实现范围 + 决策 + 遗留事项

## [1.0.0] - 2026-05-21

### Added
- 初始版本：6 阶段工作流（Phase 0-5）
- 支持 PDF/Word/纯文本/聊天记录输入
- 日报生成模板
- 多平台兼容（Cursor / Claude Code / Qoder）
