"""16K 九页样张：证明版心、镜像边距回退与九类版式。"""
from __future__ import annotations

import html
import json
from pathlib import Path

from . import config
from .fonts import font_css

SAMPLE_SECTIONS = ["章首页样张", "正文样张", "插图样张", "表格样张",
                   "代码样张", "公式样张", "脚注样张", "目录样张", "索引样张"]

MM = 72 / 25.4
TEXT_WIDTH_LIMIT_MM = 145.5
SIZE_TOLERANCE_MM = 0.5


class SampleError(RuntimeError):
    """样张没有达到 16K 版式门槛。"""


def inspect_sample(pdf_path):
    """测量页面尺寸与每页文字块的左右边界（mm）。"""
    import fitz

    doc = fitz.open(pdf_path)
    try:
        page = doc[0]
        size = (page.rect.width / MM, page.rect.height / MM)
        sections = []
        for pno, page in enumerate(doc):
            blocks = [b for b in page.get_text("blocks") if b[4].strip()]
            xs0 = min(b[0] for b in blocks) / MM
            xs1 = max(b[2] for b in blocks) / MM
            sections.append({"page": pno + 1, "left": round(xs0, 2),
                             "right": round(xs1, 2),
                             "width": round(xs1 - xs0, 2)})
        mirrored = abs(sections[1]["left"] - sections[2]["left"]) > 2.0
        report = {
            "page_size_mm": [round(x, 2) for x in size],
            "text_width_mm": max(s["width"] for s in sections),
            "margins_mm": {"top": 20, "bottom": 22},
            "mirrored": mirrored,
            "fallback": "mirrored" if mirrored else "uniform-20mm",
            "sections": sections,
        }
    finally:
        doc.close()
    return report


def build_sample(out_dir, fonts_dir=config.FONTS_DIR, browser_override=None):
    """生成 sample.html / sample.pdf / sample-report.json。"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    html_path = out / config.SAMPLE_HTML_NAME
    pdf_path = out / config.SAMPLE_PDF_NAME
    report_path = out / config.SAMPLE_REPORT_NAME
    html_path.write_text(sample_html(font_css(fonts_dir)), encoding="utf-8")
    _print_pdf(html_path, pdf_path, browser_override)
    report = inspect_sample(pdf_path)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    width, height = report["page_size_mm"]
    if (abs(width - config.TRIM_WIDTH_MM) > SIZE_TOLERANCE_MM
            or abs(height - config.TRIM_HEIGHT_MM) > SIZE_TOLERANCE_MM):
        raise SampleError(f"样张页面不是 16K：{width}×{height} mm")
    if report["text_width_mm"] > TEXT_WIDTH_LIMIT_MM:
        raise SampleError(
            f"样张版心 {report['text_width_mm']} mm 超过 "
            f"{TEXT_WIDTH_LIMIT_MM} mm")
    return html_path, pdf_path, report


def _print_pdf(html_path, pdf_path, browser_override=None):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise SampleError(
            "样张 PDF 需要 Playwright：pip install -r analog-book/requirements.txt"
        ) from exc
    launch = {"headless": True}
    if browser_override:
        executable = Path(browser_override).expanduser()
        if not executable.is_file():
            raise SampleError(f"浏览器不存在: {browser_override}")
        launch["executable_path"] = str(executable)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch)
        try:
            page = browser.new_page()
            page.set_default_timeout(180000)
            page.goto(Path(html_path).resolve().as_uri(), wait_until="load")
            page.evaluate(
                "async () => { if (document.fonts) await document.fonts.ready; }")
            page.pdf(path=str(pdf_path), print_background=True,
                     prefer_css_page_size=True)
        finally:
            browser.close()


def sample_html(fonts_css, manifest=None):
    """返回内联字体与 print.css 的独立九页样张 HTML。"""
    print_css = (config.STYLES_DIR / "print.css").read_text(encoding="utf-8")
    metadata = manifest or {}
    title = str(metadata.get("title") or "通往模拟电路之路")
    author = str(metadata.get("author") or "zhuguang-ZFG 与贡献者")
    sections = "\n".join([
        _chapter_section(),
        _body_section(),
        _figure_section(),
        _table_section(),
        _code_section(),
        _formula_section(),
        _footnote_section(),
        _toc_section(),
        _index_section(),
    ])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="author" content="{html.escape(author)}">
<title>{html.escape(title)} · 16K 样张</title>
<style>
{fonts_css}
</style>
<style>
{print_css}
</style>
</head>
<body>
<main class="book">
<div class="md-typeset">
{sections}
</div>
</main>
</body>
</html>
"""


def _chapter_section():
    goals = "".join(
        f"<li>{item}</li>" for item in (
            "说出 1 kΩ 电阻从哪个频率开始“不再是电阻”；",
            "用戴维南等效算出分压器带载后的真实输出；",
            "判断 ESR 与 ESL 谁在目标频段说了算。",
        ))
    return f"""
<section class="book-page" id="sample-chapter">
  <p class="part-kicker">第一部分 · 器件与模型</p>
  <h1>章首页样张</h1>
  <p><strong>导读：</strong>理想元件并不存在。理解寄生参数，是区分“会背公式的人”和“能设计电路的人”的第一道门槛。本章从电阻、电容、电感三件无源元件出发，把数据手册上的数字还原成可以计算的模型。</p>
  <blockquote><p><strong>先修：</strong>第 0 章的水路比喻。本章告诉你“水池也会漏、水管也有惯性”——这就是寄生参数。</p></blockquote>
  <aside class="book-callout book-callout-goal">
    <p class="book-callout-label">学完你应能</p>
    <ul>{goals}</ul>
  </aside>
  <div class="book-reveal">
    <p class="book-reveal-title">自测</p>
    <p>1 kΩ 电阻串联 10 nH 引线电感，在 3 GHz 时感抗约 190 Ω。此时这颗“电阻”实际是什么？如果它用在 3 GHz 匹配网络里，你会换成什么封装？</p>
  </div>
</section>
"""


def _body_section():
    return """
<section class="book-page" id="sample-body">
  <h1>正文样张</h1>
  <h2>2.1 小信号增益的三条路</h2>
  <p>同一个共源放大器，可以从三条路算出同一个电压增益：画负载线、列节点方程，或者直接套用小信号模型。三条路得到的表达式必须一致，这是检查代数错误最便宜的办法。</p>
  <p>先用大信号负载线确定工作点，再把工作点附近的斜率读成跨导。只要信号幅度远小于热电压，这条切线就足够准确；一旦摆幅逼近电源轨，负载线本身开始弯曲，小信号模型也就失效了。</p>
  <h3>2.1.1 三条路的适用边界</h3>
  <ul>
    <li><strong>负载线：</strong>看直流工作点与输出摆幅，最直观。</li>
    <li><strong>节点方程：</strong>适合多管级联，便于交给仿真器。</li>
    <li><strong>小信号模型：</strong>手算增益与阻抗，速度最快。</li>
  </ul>
  <p>三条路并不互相替代。设计时先用小信号模型估增益，再用负载线检查摆幅，最后用节点方程核对仿真网表——顺序反过来也能得到答案，但更容易在单位上出错。</p>
  <blockquote><p>经验法则：先画工作点，再谈增益。工作点错了，增益公式再漂亮也没有意义。</p></blockquote>
</section>
"""


def _figure_section():
    return """
<section class="book-page" id="sample-figure">
  <h1>插图样张</h1>
  <p>图内的共源级是全书出现频率最高的电路：栅极经 R<sub>G</sub> 偏置，漏极经 R<sub>D</sub> 接电源，源极接地。读图时先找电源轨和地，再顺信号从输入走到输出，最后看每个元件承担的是偏置还是负载。</p>
  <figure class="book-figure">
    <svg viewBox="0 0 560 280" width="140mm" role="img" aria-label="共源放大器：VDD 经 RD 接漏极，栅极经 RG 偏置，源极接地">
      <g fill="none" stroke="#1f2933" stroke-width="2">
        <path d="M150 30 H420"/>
        <path d="M300 30 V48 L292 56 L308 64 L292 72 L308 80 L292 88 L300 96 V120"/>
        <path d="M300 120 H440"/>
        <path d="M300 120 V146"/>
        <path d="M300 146 V160 M300 168 V182" stroke-width="3"/>
        <path d="M290 146 V182"/>
        <path d="M290 164 H240"/>
        <path d="M300 182 V212"/>
        <path d="M150 212 H320"/>
        <path d="M240 30 V56 L232 64 L248 72 L232 80 L248 88 L232 96 L240 104 V164"/>
        <circle cx="200" cy="164" r="16"/>
        <path d="M192 164 Q196 154 200 164 T208 164"/>
        <path d="M216 164 H240"/>
        <path d="M200 180 V212"/>
      </g>
      <g stroke="#1f2933" stroke-width="2">
        <path d="M260 212 V222 M250 222 H270 M254 228 H266 M258 234 H262"/>
      </g>
      <g fill="#1f2933">
        <circle cx="300" cy="120" r="4"/>
        <circle cx="240" cy="164" r="4"/>
        <circle cx="300" cy="212" r="4"/>
        <circle cx="200" cy="212" r="4"/>
      </g>
      <g fill="#1f2933" font-family="Book Sans, sans-serif" font-size="15">
        <text x="300" y="20" text-anchor="middle">V<tspan dy="5" font-size="11">DD</tspan></text>
        <text x="318" y="78">R<tspan dy="5" font-size="11">D</tspan></text>
        <text x="250" y="78" text-anchor="end">R<tspan dy="5" font-size="11">G</tspan></text>
        <text x="452" y="126">v<tspan dy="5" font-size="11">out</tspan></text>
        <text x="178" y="169" text-anchor="end">v<tspan dy="5" font-size="11">in</tspan></text>
        <text x="318" y="172">M<tspan dy="5" font-size="11">1</tspan></text>
        <text x="260" y="252" text-anchor="middle" font-size="12">GND</text>
      </g>
    </svg>
    <figcaption>图 1　共源放大器：偏置网络与信号通路（样张）</figcaption>
  </figure>
  <h3>读图的三条线</h3>
  <ul>
    <li>电源线：从 V<sub>DD</sub> 经 R<sub>D</sub> 到漏极，决定静态电流。</li>
    <li>信号线：从 v<sub>in</sub> 经栅极到漏极，方向相反所以增益为负。</li>
    <li>回流线：源极到地，任何源极阻抗都会变成反馈。</li>
  </ul>
</section>
"""


TABLE_ROWS = (
    ("电阻", "R = V/I", "串联 L、并联 C", "1/(2πRC)", "0.1–1 GHz", "高频用贴片"),
    ("电容", "C = Q/V", "ESR、ESL", "1/(2π√LC)", "1–100 MHz", "去耦看 ESR"),
    ("电感", "L = Φ/I", "绕组电容、DCR", "1/(2π√LC)", "1–50 MHz", "防止磁饱和"),
    ("二极管", "指数 I–V", "结电容、反向恢复", "1/(2πRCj)", "pF 与 ns", "开关损耗"),
    ("BJT", "β 视为常数", "Cπ、Cμ、rbb'", "gm/(2πCπ)", "0.1–10 GHz", "核对 fT"),
    ("MOS", "平方律", "Cgs、Cgd、Cdb", "gm/(2πCgs)", "1–100 GHz", "沟长调制"),
    ("运放", "增益无穷大", "输入电容、输出阻抗", "GBW", "1–100 MHz", "看相位裕度"),
    ("基准", "零温漂", "噪声、PSRR", "—", "ppm/°C", "长期漂移"),
)
TABLE_HEADER = ("元件", "理想模型", "主要寄生", "拐点频率", "典型量级", "设计提醒")


def _table_section():
    head = "".join(f"<th>{cell}</th>" for cell in TABLE_HEADER)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in TABLE_ROWS)
    return f"""
<section class="book-page" id="sample-table">
  <h1>表格样张</h1>
  <p>表 1 把常用元件的理想模型、主要寄生和失效拐点放在同一张六列表里。阅读时先横向比较同一列的典型量级，再回到具体元件核对设计提醒。</p>
  <figure class="book-table">
    <table>
      <thead><tr>{head}</tr></thead>
      <tbody>{body}</tbody>
    </table>
    <figcaption>表 1　常用元件的理想模型与主要寄生（样张数据）</figcaption>
  </figure>
  <p>注意：拐点频率一列只是数量级提示，实际值取决于封装、偏压和温度。任何一张表都不能替代数据手册，但它能告诉你应该先翻到手册的哪一页。</p>
</section>
"""


CODE_LINES = (
    "* CS amplifier: 1.8 V, 65 nm, gain and bandwidth",
    ".param vdd=1.8 vin=0.9",
    "VDD  vdd 0 1.8",
    "VIN  in  0 dc 0.9 ac 1",
    "RD   vdd out 2k",
    "M1   out in 0 0 nmos W=10u L=65n",
    ".model nmos nmos level=1 vto=0.45 kp=200u lambda=0.05",
    ".op",
    ".ac dec 10 1 1G",
    ".tran 1n 20u",
    ".meas ac gain max vdb(out)",
    ".end",
)


def _code_section():
    code = html.escape("\n".join(CODE_LINES))
    return f"""
<section class="book-page" id="sample-code">
  <h1>代码样张</h1>
  <p>网表按“标题行、参数、电源、器件、分析、结束”的顺序组织。每一行都以元件名开头，续行用 <code>+</code>，注释用 <code>*</code>——这些规则在所有 SPICE 方言里都一样。</p>
  <figure class="book-figure">
    <pre><code>{code}</code></pre>
    <figcaption>清单 1　共源放大器的 ngspice 网表（12 行）</figcaption>
  </figure>
  <p>运行后用 <code>meas</code> 语句直接读出增益，再与手算的 <em>A</em><sub>v</sub> = −<em>g</em><sub>m</sub>·<em>R</em><sub>D</sub> 对照。如果两者相差超过 20%，先检查模型参数的单位，再检查工作点是否落在饱和区。</p>
</section>
"""


def _formula_section():
    return """
<section class="book-page" id="sample-formula">
  <h1>公式样张</h1>
  <p>公式用本地内联 SVG 排版，不依赖 MathJax 初始化。下面的共源级增益同时写出“电导形式”与“电阻形式”，两者只差一个倒数关系。</p>
  <figure class="book-figure">
    <div class="arithmatex">
      <svg viewBox="0 0 560 150" width="140mm" role="img" aria-label="共源级小信号增益、输出电阻与特征频率公式">
        <g fill="#1f2933" font-family="Book Serif, serif" font-size="21">
          <text x="280" y="40" text-anchor="middle">
            <tspan font-style="italic">A</tspan><tspan dy="7" font-size="14">v</tspan><tspan dy="-7"> = −</tspan><tspan font-style="italic">g</tspan><tspan dy="7" font-size="14">m</tspan><tspan dy="-7"> (</tspan><tspan font-style="italic">R</tspan><tspan dy="7" font-size="14">D</tspan><tspan dy="-7"> ∥ </tspan><tspan font-style="italic">r</tspan><tspan dy="7" font-size="14">o</tspan><tspan dy="-7">)</tspan>
          </text>
          <text x="280" y="92" text-anchor="middle">
            <tspan font-style="italic">R</tspan><tspan dy="7" font-size="14">out</tspan><tspan dy="-7"> = </tspan><tspan font-style="italic">R</tspan><tspan dy="7" font-size="14">D</tspan><tspan dy="-7"> ∥ </tspan><tspan font-style="italic">r</tspan><tspan dy="7" font-size="14">o</tspan><tspan dy="-7"> ≈ </tspan><tspan font-style="italic">R</tspan><tspan dy="7" font-size="14">D</tspan>
          </text>
          <text x="280" y="136" text-anchor="middle">
            <tspan font-style="italic">f</tspan><tspan dy="7" font-size="14">T</tspan><tspan dy="-7"> ≈ </tspan><tspan font-style="italic">g</tspan><tspan dy="7" font-size="14">m</tspan><tspan dy="-7"> / (2π(</tspan><tspan font-style="italic">C</tspan><tspan dy="7" font-size="14">gs</tspan><tspan dy="-7"> + </tspan><tspan font-style="italic">C</tspan><tspan dy="7" font-size="14">gd</tspan><tspan dy="-7">))</tspan>
          </text>
        </g>
      </svg>
    </div>
    <figcaption>式 1　共源级的小信号增益、输出电阻与特征频率</figcaption>
  </figure>
  <ul>
    <li><em>g</em><sub>m</sub>：工作点处的跨导，单位 A/V；</li>
    <li><em>R</em><sub>D</sub>：漏极负载电阻，单位 Ω；</li>
    <li><em>r</em><sub>o</sub>：沟道长度调制引入的输出电阻。</li>
  </ul>
  <p>当 <em>r</em><sub>o</sub> ≫ <em>R</em><sub>D</sub> 时，输出电阻近似等于 <em>R</em><sub>D</sub>，增益化简为 <em>A</em><sub>v</sub> ≈ −<em>g</em><sub>m</sub>·<em>R</em><sub>D</sub>。若 <em>R</em><sub>D</sub> 换成电流源负载，<em>r</em><sub>o</sub> 就不能再被忽略——这也是电流源负载增益更高的原因。</p>
  <div class="book-reveal">
    <p class="book-reveal-title">展开推导</p>
    <p>在漏极节点列 KCL：<em>g</em><sub>m</sub><em>v</em><sub>in</sub> + <em>v</em><sub>out</sub>/<em>R</em><sub>D</sub> + <em>v</em><sub>out</sub>/<em>r</em><sub>o</sub> = 0，两边同乘 <em>R</em><sub>D</sub>·<em>r</em><sub>o</sub> 即得 <em>v</em><sub>out</sub>/<em>v</em><sub>in</sub> = −<em>g</em><sub>m</sub>(<em>R</em><sub>D</sub> ∥ <em>r</em><sub>o</sub>)。</p>
  </div>
</section>
"""


def _footnote_section():
    return """
<section class="book-page" id="sample-footnote">
  <h1>脚注样张</h1>
  <p>正文里的上标数字指向页末或章末的注释，读者不必翻到全书末尾。<sup>1</sup> 本书把短注释排在章末，把数据来源与延伸阅读放到书末的参考文献。<sup>2</sup></p>
  <p>注释的编号以章为单位重新开始，避免出现四位数页码式的编号。<sup>3</sup> 同一页出现多个注释时，按正文出现顺序排列，并与正文中的上标一一对应。</p>
  <h2>关于样张数据的说明</h2>
  <p>本页的数值用于演示版式，不代表任何具体工艺。<sup>4</sup> 需要复现实验时，请以对应章节给出的网表和模型卡为准。</p>
  <aside class="book-endnotes">
    <h2>注释</h2>
    <ol>
      <li>上标与注释之间的对应关系由排版阶段自动生成，样张使用固定编号。</li>
      <li>参考文献按作者排序，中文文献按拼音排序。</li>
      <li>章末注释与书末参考文献使用两套独立编号，互不干扰。</li>
      <li>样张中的 65 nm、1.8 V 等参数仅用于演示，不构成设计建议。</li>
    </ol>
  </aside>
</section>
"""


TOC_ROWS = (
    (1, "第一部分　器件与模型", "1"),
    (2, "第 1 章　无源元件的真实面目", "3"),
    (3, "1.1　真实电阻的等效模型", "3"),
    (3, "1.2　真实电容：ESR 与 ESL", "5"),
    (2, "第 2 章　二极管的三种面孔", "9"),
    (3, "2.1　PN 结的电容", "9"),
    (1, "第二部分　放大与反馈", "15"),
    (2, "第 3 章　共源级", "17"),
    (3, "3.1　小信号模型", "17"),
    (3, "3.2　增益与带宽", "20"),
    (2, "第 4 章　差分对", "24"),
    (3, "4.1　尾电流源", "24"),
    (1, "第三部分　频率与稳定性", "31"),
    (2, "第 5 章　极点与零点", "33"),
    (3, "5.1　米勒近似", "33"),
    (3, "5.2　相位裕度", "36"),
    (2, "第 6 章　反馈网络", "40"),
    (3, "6.1　环路增益", "40"),
    (1, "第四部分　噪声与精度", "47"),
    (2, "第 7 章　噪声入门", "49"),
    (3, "7.1　热噪声", "49"),
    (3, "7.2　闪烁噪声", "52"),
    (2, "第 8 章　失调与温漂", "56"),
    (3, "8.1　斩波稳零", "56"),
    (1, "第五部分　从电路到芯片", "63"),
    (2, "第 9 章　版图与寄生", "65"),
    (3, "9.1　匹配与失配", "65"),
    (3, "9.2　衬底耦合", "68"),
    (2, "第 10 章　基准与电源", "72"),
    (3, "10.1　带隙基准", "72"),
    (3, "10.2　LDO 与 PSRR", "76"),
    (1, "附录 A　公式速查", "81"),
)


def _toc_section():
    rows = "".join(
        f'<li class="toc-row toc-level-{level}"><a href="#">'
        f'<span class="toc-title">{title}</span>'
        f'<span class="toc-dots"></span>'
        f'<span class="toc-page">{page}</span></a></li>'
        for level, title, page in TOC_ROWS)
    return f"""
<section class="book-page" id="sample-toc">
  <div class="book-toc">
    <h1>目录样张</h1>
    <ul class="book-toc-list">
{rows}
    </ul>
    <p>页码为样张合成数据，仅用于检查双栏目录的对齐与分页。</p>
  </div>
</section>
"""


INDEX_TERMS = (
    "BJT", "CMOS", "ESR", "ESL", "GBW", "MOS", "PSRR", "Q 值", "SPICE",
    "版图", "比较器", "闭环", "带隙基准", "电感", "电容", "电阻", "二极管",
    "反馈", "放大器", "沟道长度调制", "共模抑制比", "极点", "寄生电容",
    "结电容", "跨导", "米勒效应", "偏置", "频率响应", "迁移率", "热噪声",
    "三极管", "闪烁噪声", "失调电压", "输出阻抗", "输入阻抗", "锁相环",
    "体效应", "温漂", "相位裕度", "小信号模型",
)


def _index_section():
    entries = []
    for index, term in enumerate(INDEX_TERMS):
        primary = 3 + (index * 7) % 190
        secondary = primary + 3 + index % 9 if index % 3 == 0 else None
        pages = (f'<span class="book-index-page is-primary">{primary}</span>'
                 + (f', <span class="book-index-page">{secondary}</span>'
                    if secondary else ""))
        entries.append(
            f'<p class="book-index-entry">{term} {pages}</p>')
    body = "\n".join(entries)
    return f"""
<section class="book-page" id="sample-index">
  <h1>索引样张</h1>
  <p>索引按术语排序，40 条记录分两栏排布；黑体页码表示该术语的定义页。</p>
  <div class="book-index">
{body}
  </div>
</section>
"""
