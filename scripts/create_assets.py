#!/usr/bin/env python3
"""Create original typographic cover and offline-friendly book diagrams."""

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
LATIN = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(size, latin=False):
    return ImageFont.truetype(LATIN if latin else FONT, size)


def centered(draw, y, text, size, fill, width=1440):
    f = font(size)
    box = draw.textbbox((0, 0), text, font=f)
    draw.text(((width - box[2]) / 2, y), text, font=f, fill=fill)


def arrow(draw, start, end, color, width=5):
    draw.line((start, end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 18
    points = [end]
    for delta in (0.48, -0.48):
        points.append((end[0] - length * math.cos(angle + delta),
                       end[1] - length * math.sin(angle + delta)))
    draw.polygon(points, fill=color)


def box(draw, bounds, title, lines, accent="#1b6479"):
    draw.rounded_rectangle(bounds, radius=22, fill="#ffffff", outline=accent, width=3)
    x1, y1, x2, _ = bounds
    f = font(34)
    tw = draw.textbbox((0, 0), title, font=f)[2]
    draw.text(((x1 + x2 - tw) / 2, y1 + 20), title, font=f, fill=accent)
    for i, line in enumerate(lines):
        f = font(25)
        tw = draw.textbbox((0, 0), line, font=f)[2]
        draw.text(((x1 + x2 - tw) / 2, y1 + 77 + 39 * i), line, font=f, fill="#394d5d")


def cover():
    im = Image.new("RGB", (1600, 2400), "#0b2233")
    d = ImageDraw.Draw(im)
    for x in range(110, 1500, 92):
        for y in range(1240, 2270, 92):
            d.ellipse((x, y, x + 3, y + 3), fill="#36505e")
    d.line((120, 158, 1480, 158), fill="#5c7a86", width=2)
    d.text((120, 205), "AGENT MEMORY / RESEARCH & DESIGN", font=font(36, True), fill="#b5d0d4")
    d.text((115, 360), "Agent", font=font(196, True), fill="#f6f3e8")
    d.text((110, 565), "记忆", font=font(244), fill="#f6f3e8")
    d.rectangle((125, 944, 295, 958), fill="#d3e97d")
    d.text((120, 1010), "从概念到可落地的", font=font(65), fill="#cddde0")
    d.text((120, 1110), "工程设计", font=font(65), fill="#cddde0")
    cx, cy = 1010, 1670
    for radius, color in [(408, "#395d6b"), (297, "#63858a"), (180, "#abc5b1")]:
        d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=color, width=3)
    nodes = [(-308, -264), (264, -230), (342, 205), (-180, 360), (0, 0)]
    for dx, dy in nodes[:-1]:
        d.line((cx, cy, cx + dx, cy + dy), fill="#718e86", width=3)
    for i, (dx, dy) in enumerate(nodes):
        r = 20 if i < 4 else 43
        d.ellipse((cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r),
                  fill="#d3e97d" if i in (0, 4) else "#80b5b8")
    d.text((120, 1510), "事实", font=font(40), fill="#cddde0")
    d.text((120, 1590), "经历", font=font(40), fill="#cddde0")
    d.text((120, 1670), "方法", font=font(40), fill="#cddde0")
    d.text((120, 2100), "长期记忆 · 知识治理 · 多 Agent 一致性", font=font(37), fill="#cddde0")
    d.line((120, 2210, 1480, 2210), fill="#5c7a86", width=2)
    d.text((120, 2260), "研究与设计 / 第一版", font=font(32), fill="#b5d0d4")
    d.text((1290, 2260), "2026.10", font=font(38, True), fill="#d3e97d")
    im.save(ASSETS / "cover.png", optimize=True)


def lifecycle():
    im = Image.new("RGB", (1440, 1950), "#f0f5f5")
    d = ImageDraw.Draw(im)
    centered(d, 55, "记忆的生命周期", 54, "#173950")
    steps = [
        ("01  保留原始证据", ["对话 · 工具结果 · 用户反馈"]),
        ("02  提取与校验候选", ["未来价值 · 来源 · 范围 · 敏感信息"]),
        ("03  合并与版本协调", ["去重 · 事实键 · 冲突 · 生效时间"]),
        ("04  写入有效记忆", ["单一权威内容 · 可追溯的修订"]),
        ("05  检索并组装上下文", ["权限过滤 · 适用性 · 证据 · Token 预算"]),
        ("06  接收反馈与修正", ["验证效果 · 更新条件 · 遗忘与删除"]),
    ]
    for i, (title, lines) in enumerate(steps):
        y = 190 + i * 265
        box(d, (185, y, 1255, y + 185), title, lines)
        if i < len(steps) - 1:
            arrow(d, (720, y + 191), (720, y + 248), "#3e7c8a")
    d.line([(1255, 1610), (1350, 1610), (1350, 545)], fill="#718f62", width=4)
    arrow(d, (1350, 545), (1265, 545), "#718f62")
    centered(d, 1810, "原始档案不直接等于可信知识；每次使用都要重新判断。", 26, "#526570")
    im.save(ASSETS / "memory-lifecycle.png", optimize=True)


def architecture():
    im = Image.new("RGB", (1440, 2190), "#f0f5f5")
    d = ImageDraw.Draw(im)
    centered(d, 50, "Agent 记忆层的读写架构", 50, "#173950")
    box(d, (220, 150, 1220, 320), "Agent / Harness", ["可信身份 · 当前任务 · 上下文预算"])
    arrow(d, (535, 325), (360, 410), "#3e7c8a")
    arrow(d, (905, 325), (1080, 410), "#3e7c8a")
    centered(d, 370, "读取链路                         写入链路", 29, "#526570")
    left = [
        ("授权范围内检索", ["结构化键 · 全文 · 可选语义索引"]),
        ("权威版本再校验", ["撤销屏障 · 时效 · 适用条件"]),
        ("组装本次上下文", ["来源与版本 · 去重 · 有界预算"]),
    ]
    right = [
        ("事件与 Outbox", ["幂等接收 · 来源证据 · 后台队列"]),
        ("候选提取与合并", ["来源校验 · 冲突处理 · 版本比较"]),
        ("单一权威写入", ["经评审 Git 或版本化数据库"]),
    ]
    for side, items in [(0, left), (1, right)]:
        x = 65 if side == 0 else 745
        for i, (title, lines) in enumerate(items):
            y = 450 + i * 300
            box(d, (x, y, x + 630, y + 210), title, lines)
            if i < 2:
                arrow(d, (x + 315, y + 216), (x + 315, y + 280), "#3e7c8a")
    box(d, (160, 1425, 1280, 1630), "可重建的检索投影", ["全文 / 向量索引 · 内容哈希 · 权威 revision"])
    arrow(d, (1060, 1268), (1060, 1405), "#3e7c8a")
    d.line([(160, 1525), (25, 1525), (25, 555)], fill="#718f62", width=4)
    arrow(d, (25, 555), (55, 555), "#718f62")
    box(d, (160, 1775, 1280, 1970), "生命周期与撤销屏障", ["纠错 · 过期 · 删除 · 队列失效 · 派生副本清理"], "#607a3e")
    arrow(d, (720, 1765), (720, 1650), "#718f62")
    centered(d, 2055, "单条记录只选择一个权威分支；索引与缓存不能独立反写。", 25, "#526570")
    im.save(ASSETS / "memory-architecture.png", optimize=True)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    cover()
    lifecycle()
    architecture()
    print("Created cover and two diagrams in", ASSETS)
