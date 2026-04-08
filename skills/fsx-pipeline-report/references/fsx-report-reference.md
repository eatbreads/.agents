# FSX Pipeline Report Reference

## Current watched pipelines

Only include the pipelines that FSX duty staff need to watch in this report.

| pipeline_id | title |
|---|---|
| `1073215225602` | FSX for vePFS/TOS 北京全量流水线 |
| `656544971778` | FSX for NAS/EFS 廊坊全量流水线 |
| `410812259074` | FSProxy for vePFS 全量流水线 |
| `424594542850` | vePFS 产品全量流水线 |
| `1119183026434` | VePFS 接入点 mgr 故障流水线 |

Do not include these by default:

- 二级流水线
- 三级流水线
- QA 故障注入流水线（无需看护）
- any pipeline maintained fully by another team unless the user explicitly adds it

## Preferred report structure

### 汇总信息

Recommended fields:

- 流水线标题
- 流水线 ID
- 日期
- 最近运行 ID
- 运行状态
- 失败步骤数
- 阻塞步骤数
- 首个失败步骤
- 流水线链接
- 是否需要关注

### 失败步骤明细

Recommended fields:

- 明细编号
- 日期
- 流水线标题
- 流水线 ID
- 运行 ID
- 运行状态
- 失败步骤
- 失败状态
- Job Run ID
- 任务链接

## Default local conventions

- Bits service-account secret local file: `.agents/secret`
- Raw output directory: `artifacts/`
- Markdown report path: `artifacts/fsx_pipeline_report.md`

## Group message target used in this workspace

Likely target group:

- chat name: `Zhenguo Hu, Junhao Sun`
- chat id: `oc_fb9b3bb366d930e54f0471362c3b9e8e`

If chat search returns multiple similar groups, prefer confirming by exact member set before sending.
