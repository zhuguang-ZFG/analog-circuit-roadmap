"""印刷用 SVG 净化：去掉模板背景、深色模式、动效与高饱和配色。

仅处理 108 张旧模板图（同时带 ``bgL`` 渐变与深色模式），
手绘图、站点动画图与路线图保持原样。
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
REMOVE_TAGS = {
    "linearGradient", "radialGradient", "pattern", "filter",
    "animate", "animateMotion", "animateTransform", "set",
    "style", "script", "foreignObject",
}
ANIMATION_TAGS = {"animate", "animateMotion", "animateTransform", "set"}
PAGE_CLASSES = {"page-bg", "page-vig", "page-hdr", "waveform-phase"}
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}")
URL_RE = re.compile(r"url\(#[^)]+\)")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\uFE0F\u200D]+")

# 旧模板的 Tailwind 高饱和色 -> 书籍印刷色。蓝/青绿分开保留，
# 让同一张图里的多条曲线仍然可区分。
COLOR_MAP = {
    "#ffffff": "#fffdf8", "#fff": "#fffdf8",
    "#f8fafc": "#fbf7ef", "#f1f5f9": "#f4eee2",
    "#eff6ff": "#e6f1ef", "#ecfdf5": "#eef0e2",
    "#fffbeb": "#faf0dd", "#fff7ed": "#faf0dd",
    "#fef2f2": "#f7e8e5", "#fee2e2": "#f7e8e5",
    "#dbeafe": "#d5e5e2", "#e0f2fe": "#e0efec",
    "#d1fae5": "#eef0e2", "#e2e8f0": "#ded5c4",
    "#cbd5e1": "#d8cfbf",
    "#94a3b8": "#52606d", "#8497ad": "#52606d",
    "#64748b": "#52606d", "#475569": "#52606d",
    "#334155": "#14213d", "#1e293b": "#14213d",
    "#0f172a": "#14213d", "#0a1020": "#14213d",
    "#141d30": "#14213d",
    "#2563eb": "#0f766e", "#1d4ed8": "#0f766e",
    "#3b82f6": "#0f766e", "#0284c7": "#0f766e",
    "#0369a1": "#0f766e", "#0ea5e9": "#0f766e",
    "#60a5fa": "#0f766e", "#7dd3fc": "#0f766e",
    "#38bdf8": "#0f766e", "#0891b2": "#0f766e",
    "#93c5fd": "#0f766e", "#082f49": "#0b5e57",
    "#172554": "#0b5e57", "#1e3a8a": "#0b5e57",
    "#059669": "#3f6f4f", "#10b981": "#3f6f4f",
    "#34d399": "#3f6f4f", "#065f46": "#3f6f4f",
    "#022c22": "#3f6f4f", "#6ee7b7": "#3f6f4f",
    "#7c3aed": "#7b4b6e", "#a78bfa": "#7b4b6e",
    "#dc2626": "#b42318", "#b91c1c": "#b42318",
    "#991b1b": "#b42318", "#f87171": "#b42318",
    "#fca5a5": "#b42318", "#fecaca": "#b42318",
    "#450a0a": "#b42318",
    "#f59e0b": "#b45309", "#b45309": "#b45309",
    "#92400e": "#b45309", "#fbbf24": "#b45309",
    "#fcd34d": "#b45309", "#451a03": "#b45309",
    "#431407": "#b45309",
    "#eef2f8": "#fbf7ef",
}
FONT_STACK = ('"Microsoft YaHei","Noto Sans SC","PingFang SC",'
              '"Hiragino Sans GB",sans-serif')
PRINT_STYLE = (
    f"text{{font-family:{FONT_STACK}}}"
    "line,path,polyline,polygon{stroke-linecap:round;"
    "stroke-linejoin:round}"
)


def is_legacy_svg(text: str) -> bool:
    """旧模板同时带 bgL 渐变和 prefers-color-scheme，手绘图不会误判。"""
    return 'id="bgL"' in text and "prefers-color-scheme" in text


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _map_colors(value: str) -> str:
    return HEX_RE.sub(
        lambda match: COLOR_MAP.get(match.group(0).lower(), match.group(0)),
        value)


def refine_svg(text: str) -> str:
    if not is_legacy_svg(text):
        return text
    if "<!DOCTYPE" in text or "<!ENTITY" in text:
        raise ValueError("SVG 含 DTD 或实体声明，拒绝解析")
    root = ET.fromstring(text)
    namespace = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
    parent = {child: node for node in root.iter() for child in node}

    def drop(element) -> None:
        holder = parent.get(element)
        if holder is not None:
            holder.remove(element)
            parent.pop(element, None)

    # 1) 先整块移除带直接动画子节点的元素；粒子与逐帧字幕不再残留。
    for element in list(root.iter()):
        if element is root:
            continue
        if any(_local(child.tag) in ANIMATION_TAGS for child in element):
            drop(element)

    # 2) 模板 defs 里的渐变/图案/滤镜与主题样式整体移除。
    for element in list(root.iter()):
        if element is root:
            continue
        if _local(element.tag) in REMOVE_TAGS:
            drop(element)

    # 3) 页面底纹、全屏渐变、深色叠层、零透明度元素。
    for element in list(root.iter()):
        if element is root:
            continue
        classes = set(element.get("class", "").split())
        fill = element.get("fill", "")
        stroke = element.get("stroke", "")
        if classes & PAGE_CLASSES:
            drop(element)
        elif URL_RE.search(fill) or URL_RE.search(stroke):
            drop(element)
        elif element.get("opacity", "").strip().lower() in {"0", "0.0", "0.00"}:
            drop(element)
        else:
            element.attrib.pop("filter", None)
            style = element.get("style")
            if style and ("filter:" in style or "animation" in style):
                element.attrib.pop("style", None)
            if "font-family" in element.attrib:
                element.set("font-family",
                            "Microsoft YaHei, Noto Sans SC, sans-serif")

    # 4) 清掉动画移除后留下的空组与空 defs。
    changed = True
    while changed:
        changed = False
        for element in list(root.iter()):
            if element is root:
                continue
            if _local(element.tag) in {"g", "defs"} and len(element) == 0 \
                    and not (element.text or "").strip():
                drop(element)
                changed = True

    # 5) 统一的印刷字体与线帽；SVG data URI 无法使用父页面的字体。
    style = ET.Element(namespace + "style")
    style.text = PRINT_STYLE
    root.insert(0, style)

    # 6) 文字与属性里的旧配色、emoji 一并清理。
    for element in root.iter():
        for key, value in list(element.attrib.items()):
            element.set(key, _map_colors(EMOJI_RE.sub("", value)))
        if element.text:
            element.text = EMOJI_RE.sub("", element.text)
        if element.tail:
            element.tail = EMOJI_RE.sub("", element.tail)

    if namespace:
        ET.register_namespace("", SVG_NS)
    return ET.tostring(root, encoding="unicode")
