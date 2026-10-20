# Agent 记忆：从概念到可落地的工程设计

中文 EPUB 3 电子书，包含序言、五章正文与资料附录。主要资料来自 AWS AgentCore、MachineLearningMastery、LangChain、Mem0 和阿里云 AI Agent Handbook，另补读 LangChain 的记忆概念指南。

## 成品

- [在线阅读](https://aias00.github.io/agent-memory-book/)
- [下载 EPUB](dist/Agent记忆：从概念到可落地的工程设计.epub)
- [浏览器阅读预览](dist/reading-preview.html)

正文、目录和图片已打包，可离线阅读。在线参考链接仍需网络。推荐使用支持 EPUB 3 的阅读器；浏览器预览用于检查排版，不模拟某个专有阅读器的分页。

## 目录结构

```text
manuscript/   可编辑的章节 Markdown，本版正文的权威来源
metadata.yaml 书名、语言、整理日期和书籍标识
assets/       原创封面和两张离线图片
styles/       EPUB 与预览共用样式
scripts/      构建、资源生成与检查脚本
dist/         EPUB 和自包含 HTML 预览
docs/         GitHub Pages 在线阅读站点，由书稿生成
reports/      来源指纹、验证与排版检查记录
```

## 重新构建

需要 Python 3 和 Pandoc。正常构建使用已提交的图片，不需要安装额外 Python 包：

```bash
python3 scripts/build.py
```

如果需要重新生成封面和图示，另需 Pillow，以及脚本中指定的 macOS 字体；其他系统可调整字体路径后执行：

```bash
python3 scripts/create_assets.py
```

构建会同时生成 EPUB、预览和在线站点，并检查包结构、内部链接、目录和图片描述。只修改在线界面时可运行 `python3 scripts/build_site.py`。

在线站点通过 GitHub Pages 的 `main` 分支 `/docs` 目录发布。更改书稿后，先运行构建，再提交并推送生成的 `docs/`；Pages 会自动发布静态页面。正文无需 JavaScript，无外部字体或前端依赖。

可使用 W3C EPUBCheck 进一步验证规范兼容性：

```bash
java -jar /path/to/epubcheck.jar 'dist/Agent记忆：从概念到可落地的工程设计.epub'
```

本版来源读取于 2026-10-19，整理于 2026-10-20。正文是研究与设计提案，没有声称已实现或压测；厂商性能数字与本方案目标保持区分。第三方资料版权归各自作者所有。
