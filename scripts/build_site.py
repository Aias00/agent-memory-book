#!/usr/bin/env python3
"""Publish the book as a dependency-free GitHub Pages reading site."""

from html import escape, unescape
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
BASE = "https://aias00.github.io/agent-memory-book/"
REPO = "https://github.com/Aias00/agent-memory-book"
EPUB = "Agent记忆：从概念到可落地的工程设计.epub"
CHAPTERS = [
    ("00-preface.md", "preface", "序言", "怎样阅读这本书"),
    ("01-foundations.md", "foundations", "01", "从聊天记录到可用知识"),
    ("02-design-overview.md", "architecture", "02", "目标、边界与总体架构"),
    ("03-records-and-writing.md", "writing", "03", "数据模型与写入协议"),
    ("04-retrieval-and-lifecycle.md", "retrieval", "04", "检索、一致性与遗忘"),
    ("05-evaluation-and-rollout.md", "evaluation", "05", "选型、评估与实施"),
    ("06-sources.md", "sources", "附录", "资料阅读与证据对照"),
]


def menu(current=""):
    links = []
    for _, slug, number, title in CHAPTERS:
        active = ' aria-current="page"' if current == slug else ""
        links.append(f'<li><a href="{slug}.html"{active}><span class="nav-number">'
                     f'{number}</span><span>{title}</span></a></li>')
    return '<ol class="chapter-list">' + "".join(links) + "</ol>"


def head(title, filename, description):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(description, quote=True)}">
<meta name="theme-color" content="#102c3b">
<meta property="og:title" content="{escape(title, quote=True)}">
<meta property="og:type" content="book">
<meta property="og:image" content="{BASE}assets/cover.png">
<link rel="canonical" href="{BASE}{filename}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="site.css">
<title>{escape(title)} · Agent 记忆</title></head>'''


def sidebar(current):
    return f'''<aside class="book-sidebar"><a class="sidebar-brand" href="index.html">
<span class="eyebrow">AGENT MEMORY</span><span class="brand-title">Agent 记忆<span class="brand-dot">.</span></span>
<span class="brand-subtitle">从概念到可落地的工程设计</span></a>
<nav aria-label="全书目录">{menu(current)}</nav>
<div class="sidebar-bottom"><a href="agent-memory.epub" download>下载 EPUB <span aria-hidden="true">↗</span></a>
<a href="{REPO}">GitHub 源码 <span aria-hidden="true">↗</span></a>
<span class="edition">第一版 · 2026.10</span></div></aside>'''


def mobile_header(current):
    return f'''<header class="mobile-header"><a href="index.html">Agent 记忆<span class="brand-dot">.</span></a>
<details class="mobile-menu"><summary>全书目录</summary><nav aria-label="手机全书目录">{menu(current)}
<a class="mobile-download" href="agent-memory.epub" download>下载 EPUB</a></nav></details></header>'''


def footer():
    return f'''<footer class="site-footer"><span>AI 辅助整理 · 第一版研究与设计稿</span>
<span><a href="sources.html">来源与阅读边界</a> · <a href="{REPO}">在 GitHub 查看源码</a></span></footer>'''


def text_only(markup):
    return unescape(re.sub(r"<[^>]+>", "", markup)).strip()


def build():
    if not shutil.which("pandoc"):
        raise SystemExit("Pandoc is required to build the reading site.")
    SITE.mkdir(exist_ok=True)
    (SITE / ".nojekyll").write_text("")
    shutil.copytree(ROOT / "assets", SITE / "assets", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "styles/site.css", SITE / "site.css")
    shutil.copyfile(ROOT / "dist" / EPUB, SITE / "agent-memory.epub")
    (SITE / "assets/favicon.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#102c3b"/><circle cx="32" cy="32" r="17" fill="none" stroke="#d3e97d" stroke-width="3"/><circle cx="32" cy="32" r="5" fill="#d3e97d"/></svg>''')

    rendered = {}
    anchors = {}
    for source, slug, _, _ in CHAPTERS:
        result = subprocess.run([
            "pandoc", str(ROOT / "manuscript" / source), "--from=markdown",
            "--to=html5", "--no-highlight", "--wrap=none", "--fail-if-warnings",
        ], capture_output=True, text=True, check=True)
        rendered[slug] = result.stdout
        for anchor in re.findall(r'\bid="([^"]+)"', result.stdout):
            anchors.setdefault(anchor, set()).add(slug)

    for i, (_, slug, number, title) in enumerate(CHAPTERS):
        body = rendered[slug]

        def resolve(match):
            anchor = match.group(1)
            if anchor in re.findall(r'\bid="([^"]+)"', rendered[slug]):
                return match.group(0)
            owners = anchors.get(anchor, set())
            if len(owners) != 1:
                raise ValueError("Unresolved or ambiguous chapter anchor: " + anchor)
            return 'href="' + next(iter(owners)) + '.html#' + anchor + '"'

        body = re.sub(r'href="#([^"]+)"', resolve, body)
        sections = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, flags=re.S)
        toc = "".join(f'<li><a href="#{anchor}">{escape(text_only(label))}</a></li>'
                      for anchor, label in sections)
        local_toc = f'<details class="section-nav"><summary>本章目录</summary><ol>{toc}</ol></details>' if toc else ""
        previous = (f'<a href="{CHAPTERS[i - 1][1]}.html"><span>上一章</span>'
                    f'{CHAPTERS[i - 1][3]}</a>') if i else '<a href="index.html"><span>返回</span>全书首页</a>'
        following = (f'<a class="next" href="{CHAPTERS[i + 1][1]}.html"><span>下一章</span>'
                     f'{CHAPTERS[i + 1][3]}</a>') if i + 1 < len(CHAPTERS) else '<a class="next" href="agent-memory.epub" download><span>离线阅读</span>下载 EPUB</a>'
        description = f"《Agent 记忆》{number}：{title}。记忆分类、工程架构与实践设计。"
        page = (head(title, slug + ".html", description) + '<body class="reading-layout">'
                '<a class="skip-link" href="#main">跳到正文</a>' + sidebar(slug) + mobile_header(slug)
                + '<main class="reading-main" id="main"><div class="reading-inner">'
                f'<div class="reading-meta"><a href="index.html">Agent 记忆</a><span>{number} / 在线阅读</span></div>'
                + local_toc + '<article class="prose">' + body + '</article>'
                + '<nav class="chapter-pagination" aria-label="前后章导航">' + previous + following + '</nav>'
                + footer() + '</div></main></body></html>')
        (SITE / (slug + ".html")).write_text(page)

    chapters = "".join(f'<li><a href="{slug}.html"><span class="chapter-index">{number}</span>'
                       f'<span class="chapter-name">{title}</span><span aria-hidden="true">↗</span></a></li>'
                       for _, slug, number, title in CHAPTERS)
    landing = head("从概念到可落地的工程设计", "index.html", "一本关于 Agent 长期记忆的中文读本：事实、经历、方法，以及可追溯、可纠正、可遗忘的工程设计。") + f'''<body class="landing">
<a class="skip-link" href="#main">跳到正文</a>
<header class="landing-header"><a class="wordmark" href="index.html">AGENT MEMORY<span class="brand-dot">.</span></a>
<nav aria-label="首页导航"><a href="#chapters">目录</a><a href="{REPO}">GitHub ↗</a></nav></header>
<main id="main"><section class="hero"><div class="hero-copy"><p class="eyebrow">一本写给 Agent 开发者的记忆读本</p>
<h1>让 Agent 记住，<br>也懂得<span class="title-emphasis">修正与遗忘。</span></h1>
<p class="hero-description">从事实、经历与方法出发，走向可追溯的知识、可靠的读写协议，以及能被验证的长期记忆。</p>
<div class="hero-actions"><a class="primary-action" href="preface.html">开始阅读 <span aria-hidden="true">→</span></a><a class="download-action" href="agent-memory.epub" download>下载 EPUB ↗</a></div>
<p class="hero-note">五章正文 · 工程方案 · 来源附录<br>第一版 / 2026 年 10 月</p></div>
<figure class="hero-cover"><img src="assets/cover.png" width="1600" height="2400" alt="《Agent 记忆：从概念到可落地的工程设计》封面"><figcaption>AGENT MEMORY / RESEARCH & DESIGN</figcaption></figure></section>
<section class="contents-section" id="chapters"><div class="section-heading"><div><p class="eyebrow">READ THE BOOK</p><h2>从理解记忆，到设计系统。</h2></div><p>按顺序阅读，或直接进入你关心的章节。</p></div>
<ol class="contents-list">{chapters}</ol></section>
<section class="about-section"><h2>保留知识，也保留证据。</h2><div><p>这本书综合 AWS AgentCore、LangChain、Mem0、MachineLearningMastery 与阿里云 AI Agent Handbook，区分来源描述、设计判断与待验证目标。</p><p>正文讨论架构与协议，不把厂商基准数字当成通用承诺。所有章节均可在线阅读，也可下载 EPUB 离线阅读。</p><a href="sources.html">查看来源与阅读边界 →</a></div></section></main>{footer()}</body></html>'''
    (SITE / "index.html").write_text(landing)
    (SITE / "404.html").write_text(head("页面未找到", "404.html", "返回 Agent 记忆全书目录。")
        + '<body class="landing"><main class="not-found"><p class="eyebrow">404</p>'
        + '<h1>这页暂时不在书里。</h1><p><a href="' + BASE + '">返回全书首页 →</a></p></main></body></html>')
    manifest_path = ROOT / "reports/source-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["notes"] = ("sources contains historical editorial input hashes, not repository file paths. "
                         "manuscript contains the current, reproducible source files for this edition.")
    manifest["manuscript"] = {"manuscript/" + source: {"sha256": hashlib.sha256(
        (ROOT / "manuscript" / source).read_bytes()).hexdigest()} for source, *_ in CHAPTERS}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    subprocess.run([sys.executable, "scripts/validate_site.py"], cwd=ROOT, check=True)
    print("GitHub Pages site:", SITE)


if __name__ == "__main__":
    build()
