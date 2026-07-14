#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAPA 纠正措施报告生成器（成熟度定制版）
读入结构化结果 JSON，生成 六段式 纠正措施报告（txt + md 双件）。
产物默认写入当前工作目录（或 --out-dir 指定目录）。

用法：
  python build_report.py --input result.json --out-dir ./输出
  python build_report.py --demo --out-dir ./输出        # 内置小样本跑通
  python build_report.py --input result.json --format txt   # 仅 txt

输入 JSON 结构（字段缺失以「待企业补充」占位）：
{
  "capa_id": "CAPA-2026-001",
  "title": "XX 产品运输划伤",
  "clause": "ISO9001:2015 8.7 / 10.2",
  "maturity_level": "B类（基础规范型）",
  "nonconformity": "不符合项事实描述",
  "correction": "已执行纠正措施（应急止损）",
  "root_cause": "根本原因分析（5Why）",
  "doc_materials": "审核书面合规材料",
  "field_actions": "现场轻量化落地动作",
  "verification": "效果验证方案",
  "prevention": "防反弹固化要求"
}
"""

import argparse
import json
import os
import sys
from datetime import datetime


def load_result(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt(v, placeholder="待企业补充"):
    """空值转为占位符，避免幻觉。"""
    if v is None:
        return placeholder
    if isinstance(v, str) and v.strip() == "":
        return placeholder
    return str(v)


# ----------------------------- MD -----------------------------
def build_md(r):
    L = []
    L.append("# CAPA 纠正措施报告\n")
    L.append(f"> 编号：**{fmt(r.get('capa_id'))}** ｜ 成熟度：**{fmt(r.get('maturity_level'))}** ｜ 生成：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    L.append(f"> 适用条款：{fmt(r.get('clause'))}\n")
    L.append(f"**问题概要：** {fmt(r.get('title'))}\n")

    L.append("## 一、不符合项事实描述\n")
    L.append(fmt(r.get("nonconformity")))
    L.append("")

    L.append("## 二、已执行纠正措施（应急止损）\n")
    L.append(fmt(r.get("correction")))
    L.append("")

    L.append("## 三、根本原因分析（5Why）\n")
    L.append(fmt(r.get("root_cause")))
    L.append("")

    L.append("## 四、分轨纠正措施\n")
    L.append("### 4.1 审核书面合规材料\n")
    L.append(fmt(r.get("doc_materials")))
    L.append("")
    L.append("### 4.2 现场轻量化落地动作\n")
    L.append(fmt(r.get("field_actions")))
    L.append("")

    L.append("## 五、效果验证方案\n")
    L.append(fmt(r.get("verification")))
    L.append("")

    L.append("## 六、防反弹固化要求\n")
    L.append(fmt(r.get("prevention")))
    L.append("")

    L.append("> 本报告由 CAPA纠正预防措施技能（成熟度定制）生成，具体内容以企业实际评审结论为准。")
    return "\n".join(L)


# ----------------------------- TXT -----------------------------
def build_txt(r):
    L = []
    L.append("CAPA 纠正措施报告")
    L.append("=" * 60)
    L.append(f"编号：{fmt(r.get('capa_id'))}")
    L.append(f"成熟度：{fmt(r.get('maturity_level'))}")
    L.append(f"适用条款：{fmt(r.get('clause'))}")
    L.append(f"问题概要：{fmt(r.get('title'))}")
    L.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append("")

    sections = [
        ("一、不符合项事实描述", "nonconformity"),
        ("二、已执行纠正措施（应急止损）", "correction"),
        ("三、根本原因分析（5Why）", "root_cause"),
        ("四、分轨纠正措施", None),
        ("五、效果验证方案", "verification"),
        ("六、防反弹固化要求", "prevention"),
    ]
    for title, key in sections:
        L.append(title)
        L.append("-" * 60)
        if title.startswith("四"):
            L.append("4.1 审核书面合规材料")
            L.append(fmt(r.get("doc_materials")))
            L.append("")
            L.append("4.2 现场轻量化落地动作")
            L.append(fmt(r.get("field_actions")))
        else:
            L.append(fmt(r.get(key)))
        L.append("")

    L.append("=" * 60)
    L.append("本报告由 CAPA纠正预防措施技能（成熟度定制）生成，具体内容以企业实际评审结论为准。")
    return "\n".join(L)


# ----------------------------- demo -----------------------------
def demo_result():
    return {
        "capa_id": "CAPA-2026-001",
        "title": "铁皮柜运输划伤（客户验货不合格）",
        "clause": "ISO9001:2015 8.5.1 / 8.7 / 10.2",
        "maturity_level": "B类（基础规范型）",
        "nonconformity": (
            "2026-03-10 客户验货发现 A 型号铁皮柜侧面划伤 12 件，占该批 200 件的 6%，"
            "位置集中在上沿折弯处，状态为漆面破损见底材。违背标准：成品防护要求（8.5.1）、"
            "不合格输出控制（8.7）。"
        ),
        "correction": (
            "1) 已隔离该批剩余 188 件，全检挑出带划伤的 12 件单独存放并贴不合格标签；"
            "2) 12 件经评估后转返工（打磨补漆），返工后复检合格方放行；"
            "3) 已发运的 2 批同款产品主动通知客户质量接口人，约定到货后重点验看上沿。"
        ),
        "root_cause": (
            "1)为何划伤？上沿折弯处在层叠码放时被上层柜体压磨→2)为何会层叠压磨？周转用珍珠棉仅垫四角，"
            "上沿无保护→3)为何上沿无保护？包装作业无图示、仅靠老师傅口头交代→4)为何靠口头？"
            "包装无受控作业指导书→5)为何无文件？新产品上线未同步输出包装 SOP。根因：新产品质量策划"
            "未覆盖包装防护，包装过程无受控文件与图示。"
        ),
        "doc_materials": (
            "1) 1 页《铁皮柜运输防护临时规定》（受控编号 WI-PKG-023，班组长签字生效），明确层间整张珍珠棉+"
            "上沿护角；2) 不合格品隔离/返工记录表（12 件处置闭环，含复检合格签认）；3) 客户沟通记录截图；"
            "4) 纠正措施验证报告（连续 30 天发货划伤 0 例）。以上四项覆盖审核闭环五件套。"
        ),
        "field_actions": (
            "1) 物料备货：采购整张珍珠棉+纸质护角常备于包装工位；2) 现场 1 分钟示范：班组长每天开工前演示"
            "正确垫放，拍一张合格码放照片发班组群；3) 单点卡点：发货口设 1 张 A4 大字检查卡「上沿护角✓ 层间整棉✓」，"
            "仓管员发货前打勾。无复杂培训、无新增流程审批。"
        ),
        "verification": (
            "节点一（7天）：抽查 5 车发货码放，护角与整棉 100% 到位；节点二（30天）：监控发货划伤率，"
            "目标由 6% 降至 0；节点三（90天）：客户验货不合格反馈 0 起。验证方式：发货前拍照抽查 + 客诉台账回溯。"
        ),
        "prevention": (
            "1) 将《铁皮柜运输防护临时规定》转为正式受控文件并纳入新员工上岗必读；2) 新产品质量策划清单"
            "增加「包装防护」必填项，避免同类遗漏；3) 发货口 A4 检查卡长期保留，月度点检 1 次。"
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="CAPA 纠正措施报告生成器（成熟度定制版）")
    ap.add_argument("--input", help="结构化结果 JSON 路径")
    ap.add_argument("--out-dir", default=os.getcwd(), help="输出目录（默认当前工作目录）")
    ap.add_argument("--format", choices=["txt", "md", "all"], default="all", help="输出格式，默认 all")
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

    try:
        os.makedirs(args.out_dir, exist_ok=True)
    except Exception as e:
        sys.stderr.write(f"创建输出目录失败：{e}\n")
        sys.exit(1)

    capa_id = fmt(r.get("capa_id"), "CAPA")
    date_str = datetime.now().strftime("%Y%m%d")
    base = f"CAPA纠正措施报告_{capa_id}_{date_str}"

    if args.format in ("md", "all"):
        md_path = os.path.join(args.out_dir, base + ".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(build_md(r))
        sys.stderr.write(f"MD 已生成：{md_path}\n")

    if args.format in ("txt", "all"):
        txt_path = os.path.join(args.out_dir, base + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(build_txt(r))
        sys.stderr.write(f"TXT 已生成：{txt_path}\n")


if __name__ == "__main__":
    main()
