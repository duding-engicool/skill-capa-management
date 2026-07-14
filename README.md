# CAPA纠正预防措施管理技能（capa-management）

> 主色：`#C8102E` ｜ 类型：混合式双版（生成/改进类）

## 一句话简介
以 8D 风格引导构建 CAPA 纠正预防措施报告，输出 **MD + HTML 双版**，解决根因浅、措施无效、无跟踪的闭环难题。

## 适用角色
质量工程师、CAPA 负责人、品质经理、过程改进工程师。

## 何时使用
- 处理客诉 / 审核不符合项 / 过程异常，需要正式 CAPA；
- 用 8D 方法系统解决重复性、重大质量问题；
- 编写纠正预防措施报告，需要统一格式便于评审与归档；
- PDCA 改进需要把"措施—验证—标准化"落到纸面。

## 产出物
| 文件 | 说明 |
|------|------|
| `CAPA报告.md` | 标准结构化文档（八步闭环） |
| `CAPA报告.html` | 精美网页版，用于评审与演示（主色 #C8102E） |

## 使用方式
1. 在对话中按引导逐项提供信息（团队 / 问题 / 临时措施 / 根因 / 纠正 / 预防 / 验证 / 关闭）；
2. 确认大纲；
3. Agent 调用 `scripts/build_report.py` 生成双版。

本地脚本跑通（内置小样本）：
```bash
python scripts/build_report.py --demo --md-out CAPA报告.md --html-out CAPA报告.html
```
或用自己的结构化 JSON：
```bash
python scripts/build_report.py --input result.json --md-out CAPA报告.md --html-out CAPA报告.html
```

## 设计规范
- 所有文档简体中文；代码标识符英文；
- 主色 `#C8102E`；
- 防幻觉：不确定项标「待企业补充」，不编造标准号 / 数据；
- 去商业化：无营销人设、无付费引导。

## 联动
上游 `8d-report-assistant`；下游 `cqi-improvement`；横向可协同 `5why-analysis`、鱼骨图、CQI 系列、FMEA/CP。
