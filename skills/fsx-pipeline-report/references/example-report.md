# FSX 需看护流水线运营报表

- 生成时间：2026-04-08 11:48:05
- 范围：FSX 值班需看护的 5 条流水线
- 口径：先聚焦“哪天哪条流水线在哪个步骤失败”，暂不展开失败原因分析

## 汇总信息

| 日期 | 流水线标题 | 流水线 ID | 最近运行 ID | 运行状态 | 失败步骤数 | 阻塞步骤数 | 首个失败步骤 | 是否需要关注 |
|---|---|---:|---:|---|---:|---:|---|---|
| 2026-04-08 | FSX for vePFS/TOS 北京全量流水线 | 1073215225602 | 1136934722050 | 运行中 | 8 | 1 | 升级兼容性测试 | 是 |
| 2026-04-07 | FSX for NAS/EFS 廊坊全量流水线 | 656544971778 | 1136939989506 | 已结束 | 13 | 0 | 升级兼容性测试 | 是 |
| 2026-04-08 | FSProxy for vePFS 全量流水线 | 410812259074 | 1136870052610 | 成功 | 0 | 0 |  | 否 |
| 2026-04-08 | VePFS 接入点 mgr 故障流水线 | 1119183026434 | 1136881409794 | 已结束 | 0 | 0 |  | 否 |
| 2026-04-08 | FSProxy for EFS&NAS 全量流水线 | 865297825538 | 1136942409730 | 成功 | 0 | 0 |  | 否 |

## 失败步骤明细

Use the generated `artifacts/fsx_pipeline_report.md` as the full current example.

This file exists only to show the required section order and table style:

- first `汇总信息`
- then `失败步骤明细`
- no extra conclusion block inside the markdown
