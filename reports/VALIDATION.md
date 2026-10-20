# 本版验证记录

- 格式：EPUB 3，可重排版，语言标记 `zh-CN`。
- 内容：序言、五章正文、来源附录；另含封面、书名页和目录。
- 素材：原创封面与两张 PNG 图示均内嵌，不依赖 Mermaid 或外部脚本。
- W3C EPUBCheck 5.4.0：0 fatal、0 error、0 warning、0 info，详见 `epubcheck.json`。
- 包结构检查：ZIP mimetype、OPF manifest/spine、导航、XML 和资源引用通过，144 处内部引用已检查，详见 `package-validation.json`。
- 移动宽度：使用浏览器渲染从最终 EPUB 提取的实际 XHTML/CSS，在 390 × 844 像素视口下逐章检查；7 个内容单元均无横向溢出，图片载入正常，详见 `mobile-layout.json`。
- 视觉抽查：封面、架构图、章节开头和 YAML 代码。截图见 `chapter-mobile.png` 与 `code-mobile.png`。
- 内容检查：文章七节、设计十二节、S1—S6 来源说明完整保留；章节内链接已转为 EPUB 内部跳转，正文无临时路径或原工作目录引用。

浏览器验证检查排版和资源，不模拟 Apple Books、Kindle 或其他阅读器的专有分页。没有宣称这些阅读器均已实机测试。
