#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAPA / 8D 纠正预防措施报告生成器
读入结构化结果 JSON，生成 MD 文档 + 精美网页版 HTML（主色 #C8102E）。

用法：
  python build_report.py --input result.json --md-out report.md --html-out report.html
  python build_report.py --input result.json --html-out report.html      # 仅 HTML
  python build_report.py --demo --md-out report.md --html-out report.html # 用内置小样本跑通

输入 JSON 结构（字段缺失以「待企业补充」占位）：
{
  "capa_id": "CAPA-2026-001",
  "title": "XX 产品外观不良率超标",
  "source": "客诉",
  "level": "一般",
  "team": [{"role":"组长","name":"品质部-张工"}],
  "problem": "5W2H 描述",
  "containment": [{"action":"隔离问题批次","owner":"生产部-李工","due":"2026-01-20"}],
  "root_cause": {"method":"5Why","content":"设备 X 校准偏移…","verified":false},
  "corrective_actions": [{"action":"恢复设备精度","owner":"设备部-王工","due":"2026-02-01","verify":"连续30天 SPC 合格"}],
  "preventive_actions": [{"action":"更新 PM 计划","spread":"同类设备5台","owner":"设备部","due":"2026-02-15"}],
  "verification": [{"node":"30天","date":"2026-03-01","method":"SPC 监控","result":"不良率降至0.1%"}],
  "closure": {"checklist":[True,True,True,True,True,True,True],"approver":"品保经理-杜鼎","close_date":"2026-04-01"},
  "status": "已关闭"
}
"""

import argparse
import json
import sys
import html
from datetime import datetime


PRIMARY = "#C8102E"  # 主色


def esc(s):
    return html.escape(str(s), quote=True)


def load_result(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt(v, placeholder="待企业补充"):
    """空值转为占位符，避免幻觉。"""
    if v is None:
        return placeholder
    if isinstance(v, str) and v.strip() == "":
        return placeholder
    return v


def list_pairs(items, keys):
    out = []
    if not items:
        return ["• " + "（待企业补充）"]
    for it in items:
        if isinstance(it, dict):
            parts = []
            for k in keys:
                val = fmt(it.get(k))
                parts.append(str(val))
            out.append("• " + " ｜ ".join(parts))
        else:
            out.append("• " + str(it))
    return out


# ----------------------------- MD -----------------------------
def build_md(r):
    L = []
    L.append(f"# CAPA 纠正预防措施报告\n")
    L.append(f"> 编号：**{esc(fmt(r.get('capa_id')))}** ｜ 状态：{esc(fmt(r.get('status')))} ｜ 生成：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    L.append("## 一、基础信息\n")
    L.append(f"- 标题：{fmt(r.get('title'))}")
    L.append(f"- 来源：{fmt(r.get('source'))}")
    L.append(f"- 问题等级：{fmt(r.get('level'))}")
    team = r.get("team") or []
    if team:
        L.append("- 团队：" + "；".join(f"{fmt(t.get('role'))}:{fmt(t.get('name'))}" for t in team))
    else:
        L.append("- 团队：（待企业补充）")
    L.append("")

    L.append("## 二、D2 问题描述（5W2H）\n")
    L.append(fmt(r.get("problem")))
    L.append("")

    L.append("## 三、D3 临时措施（遏制）\n")
    L.extend(list_pairs(r.get("containment"), ["action", "owner", "due"]))
    L.append("")

    L.append("## 四、D4 根因分析\n")
    rc = r.get("root_cause") or {}
    L.append(f"- 方法：{fmt(rc.get('method'))}")
    L.append(f"- 内容：\n{fmt(rc.get('content'))}")
    L.append(f"- 已验证：{'是' if rc.get('verified') else '否（待验证）'}")
    L.append("")

    L.append("## 五、D5/D6 纠正措施（永久）\n")
    L.extend(list_pairs(r.get("corrective_actions"), ["action", "owner", "due", "verify"]))
    L.append("")

    L.append("## 六、D7 预防措施（横向展开）\n")
    L.extend(list_pairs(r.get("preventive_actions"), ["action", "spread", "owner", "due"]))
    L.append("")

    L.append("## 七、效果验证（30/60/90 天）\n")
    L.extend(list_pairs(r.get("verification"), ["node", "date", "method", "result"]))
    L.append("")

    L.append("## 八、D8 关闭检查清单\n")
    items = ["根因已明确且经验证", "纠正措施已实施且有效", "预防措施已实施且有效",
             "效果验证通过（≥90天）", "相关文件已更新(FMEA/CP/SOP)", "相关人员已完成培训", "经验教训已沉淀"]
    cl = (r.get("closure") or {}).get("checklist") or [False] * len(items)
    for i, it in enumerate(items):
        ok = cl[i] if i < len(cl) else False
        L.append(f"- [{'x' if ok else ' '}] {it}")
    cl_info = r.get("closure") or {}
    L.append(f"\n- 审批人：{fmt(cl_info.get('approver'))}")
    L.append(f"- 关闭日期：{fmt(cl_info.get('close_date'))}")
    L.append("")

    L.append("> 本报告由 CAPA纠正预防措施管理技能生成，具体内容以企业实际评审结论为准。")
    return "\n".join(L)


# ----------------------------- HTML -----------------------------
CSS = f"""
:root{{--primary:{PRIMARY};--bg:#f7f8fa;--card:#fff;--ink:#1f2933;--muted:#6b7280;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.7;padding:32px}}
.wrap{{max-width:1040px;margin:0 auto}}
header{{background:linear-gradient(135deg,var(--primary),#9c0c24);color:#fff;border-radius:16px;
  padding:30px 34px;margin-bottom:28px;box-shadow:0 8px 24px rgba(200,16,46,.25)}}
header h1{{font-size:27px;letter-spacing:1px}}
header .meta{{margin-top:12px;font-size:14px;opacity:.95}}
.badge{{display:inline-block;background:rgba(255,255,255,.2);border-radius:6px;padding:3px 10px;margin-right:8px;font-size:13px}}
.sec{{background:var(--card);border-radius:14px;padding:24px 26px;box-shadow:0 4px 16px rgba(0,0,0,.06);margin-bottom:22px}}
.sec h2{{font-size:20px;margin-bottom:14px;border-left:5px solid var(--primary);padding-left:12px}}
.sec p{{white-space:pre-wrap;margin:0 0 6px}}
ul{{list-style:none;padding-left:0}}
ul li{{padding:7px 0;border-bottom:1px dashed #eee;font-size:15px}}
.timeline{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:8px}}
.tnode{{background:#fdeef0;border-radius:10px;padding:14px;border-top:4px solid var(--primary)}}
.tnode b{{color:var(--primary)}}
.check{{font-size:15px;padding:6px 0}}
.check .on{{color:#16a34a;font-weight:700}}
.check .off{{color:var(--muted)}}
footer{{text-align:center;color:var(--muted);font-size:12px;margin-top:18px}}
@media(max-width:720px){{.timeline{{grid-template-columns:1fr}}}}
"""


def build_html(r):
    team_html = "；".join(f"{esc(fmt(t.get('role')))}:{esc(fmt(t.get('name')))}" for t in (r.get("team") or [])) or "（待企业补充）"
    rc = r.get("root_cause") or {}

    def items_li(items, keys):
        out = []
        for it in (items or []):
            if isinstance(it, dict):
                vals = " ｜ ".join(esc(fmt(it.get(k))) for k in keys)
                out.append(f"<li>{vals}</li>")
            else:
                out.append(f"<li>{esc(it)}</li>")
        if not out:
            out.append('<li style="color:#9ca3af">（待企业补充）</li>')
        return "\n".join(out)

    ver_html = "\n".join(
        f'<div class="tnode"><b>{esc(fmt(v.get("node")))}</b><br>日期：{esc(fmt(v.get("date")))}'
        f'<br>方式：{esc(fmt(v.get("method")))}<br>结果：{esc(fmt(v.get("result")))}</div>'
        for v in (r.get("verification") or [])
    ) or '<div class="tnode">（待企业补充）</div>'

    items = ["根因已明确且经验证", "纠正措施已实施且有效", "预防措施已实施且有效",
             "效果验证通过（≥90天）", "相关文件已更新(FMEA/CP/SOP)", "相关人员已完成培训", "经验教训已沉淀"]
    cl = (r.get("closure") or {}).get("checklist") or [False] * len(items)
    cl_html = ""
    for i, it in enumerate(items):
        ok = cl[i] if i < len(cl) else False
        mark = '<span class="on">✓</span>' if ok else '<span class="off">✗</span>'
        cl_html += f'<div class="check">{mark} {esc(it)}</div>'
    cl_info = r.get("closure") or {}

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CAPA 报告 · {esc(fmt(r.get('capa_id')))}</title>
<style>{CSS}</style></head>
<body><div class="wrap">
<header>
  <h1>CAPA 纠正预防措施报告</h1>
  <div class="meta">
    <span class="badge">编号 {esc(fmt(r.get('capa_id')))}</span>
    <span class="badge">状态 {esc(fmt(r.get('status')))}</span>
    <span class="badge">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
  </div>
</header>

<section class="sec">
  <h2>一、基础信息</h2>
  <p>标题：{esc(fmt(r.get('title')))}</p>
  <p>来源：{esc(fmt(r.get('source')))} ｜ 等级：{esc(fmt(r.get('level')))}</p>
  <p>团队：{team_html}</p>
</section>

<section class="sec">
  <h2>二、D2 问题描述（5W2H）</h2>
  <p>{esc(fmt(r.get('problem')))}</p>
</section>

<section class="sec">
  <h2>三、D3 临时措施（遏制）</h2>
  <ul>{items_li(r.get('containment'), ['action','owner','due'])}</ul>
</section>

<section class="sec">
  <h2>四、D4 根因分析</h2>
  <p>方法：{esc(fmt(rc.get('method')))}</p>
  <p>{esc(fmt(rc.get('content')))}</p>
  <p>已验证：{'是' if rc.get('verified') else '否（待验证）'}</p>
</section>

<section class="sec">
  <h2>五、D5/D6 纠正措施（永久）</h2>
  <ul>{items_li(r.get('corrective_actions'), ['action','owner','due','verify'])}</ul>
</section>

<section class="sec">
  <h2>六、D7 预防措施（横向展开）</h2>
  <ul>{items_li(r.get('preventive_actions'), ['action','spread','owner','due'])}</ul>
</section>

<section class="sec">
  <h2>七、效果验证（30/60/90 天）</h2>
  <div class="timeline">{ver_html}</div>
</section>

<section class="sec">
  <h2>八、D8 关闭检查清单</h2>
  {cl_html}
  <p style="margin-top:12px">审批人：{esc(fmt(cl_info.get('approver')))} ｜ 关闭日期：{esc(fmt(cl_info.get('close_date')))}</p>
</section>

<footer>本报告由 CAPA纠正预防措施管理技能生成 · 具体内容以企业实际评审结论为准</footer>
</div></body></html>"""


# ----------------------------- demo -----------------------------
def demo_result():
    return {
        "capa_id": "CAPA-2026-001",
        "title": "XX 产品外观不良率超标",
        "source": "客诉",
        "level": "一般",
        "team": [{"role": "组长", "name": "品质部-张工"}, {"role": "成员", "name": "设备部-王工"}],
        "problem": "2026-01-12 客户投诉 A123 批次外观不良率 0.8%（标准≤0.2%），涉及 A 线 3 号工位，已发出 200 件。",
        "containment": [
            {"action": "隔离问题批次并全检", "owner": "生产部-李工", "due": "2026-01-15"},
            {"action": "在制品 100% 目视全检后放行", "owner": "品质部-张工", "due": "2026-01-16"}
        ],
        "root_cause": {
            "method": "5Why",
            "content": "1)为何不良？设备 X 压装偏移→2)为何偏移？校准超期→3)为何超期？PM 计划未纳入该设备→4)为何未纳入？新设备上线未更新点检表→根因：新设备维护保养未纳入体系文件。",
            "verified": True
        },
        "corrective_actions": [
            {"action": "恢复设备精度并重新校准", "owner": "设备部-王工", "due": "2026-01-25", "verify": "校准合格，连续 30 天 SPC 受控"}
        ],
        "preventive_actions": [
            {"action": "更新 PM 计划与点检表，纳入新设备", "spread": "同类新设备 5 台", "owner": "设备部-王工", "due": "2026-02-10"},
            {"action": "更新 FMEA 与控制计划监控点", "spread": "A 线全部工位", "owner": "品质部-张工", "due": "2026-02-15"}
        ],
        "verification": [
            {"node": "30天", "date": "2026-02-25", "method": "SPC 监控", "result": "不良率降至 0.1%"},
            {"node": "60天", "date": "2026-03-25", "method": "趋势分析", "result": "稳定 ≤0.15%"},
            {"node": "90天", "date": "2026-04-25", "method": "客诉复核", "result": "无新增客诉"}
        ],
        "closure": {"checklist": [True, True, True, True, True, True, True],
                    "approver": "品保经理-杜鼎", "close_date": "2026-04-30"},
        "status": "已关闭"
    }


def main():
    ap = argparse.ArgumentParser(description="CAPA / 8D 报告生成器")
    ap.add_argument("--input", help="结构化结果 JSON 路径")
    ap.add_argument("--md-out", help="输出 MD 路径")
    ap.add_argument("--html-out", help="输出 HTML 路径")
    ap.add_argument("--demo", action="store_true", help="用内置小样本生成（便于跑通校验）")
    args = ap.parse_args()

    if args.demo:
        r = demo_result()
    elif args.input:
        try:
            r = load_result(args.input)
        except Exception as e:
            sys.stderr.write(f"读取输入失败：{e}\n")
            sys.exit(1)
    else:
        sys.stderr.write("请提供 --input 或 --demo。\n")
        sys.exit(1)

    if args.md_out:
        with open(args.md_out, "w", encoding="utf-8") as f:
            f.write(build_md(r))
        sys.stderr.write(f"MD 已生成：{args.md_out}\n")
    if args.html_out:
        with open(args.html_out, "w", encoding="utf-8") as f:
            f.write(build_html(r))
        sys.stderr.write(f"HTML 已生成：{args.html_out}\n")
    if not args.md_out and not args.html_out:
        sys.stderr.write("未指定 --md-out / --html-out，无输出。\n")


if __name__ == "__main__":
    main()
