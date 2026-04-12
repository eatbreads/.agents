---
name: fsx-pipeline-report-feishu
description: 面向 FSX 值班/看护场景的 Bits 流水线看护与飞书播报 Skill。用于抓取固定五条 FSX 流水线的最新已结束 run，生成 overview/top10/jobs 三份总 CSV，写入每日飞书电子表格，并将 AI 简报发送到飞书群。
---

# FSX 流水线看护与飞书播报

本 Skill 用于 FSX 值班场景下的固定流水线看护，而不是泛化的任意 Bits 报表导出。

它现在覆盖三类事情：

1. 对某一条指定 `pipelineId + runId` 的运行结果做详细统计
2. 对固定的 FSX 看护流水线集合做“取最新已结束 run -> 生成汇总产物”的日常巡检
3. 将每日巡检结果整理成飞书电子表格并自动发送群消息

## 何时使用

当你需要做以下事情时，应优先使用本 Skill：

- 看护 FSX 值班范围内的 Bits 流水线
- 获取某条流水线最近一次已结束 run 的测试统计
- 输出适合直接查看和筛选的 CSV 报表
- 快速定位失败贡献最高的测试节点
- 生成可直接发飞书群的值班播报
- 将三份 CSV 汇总为一张飞书电子表格

它尤其适合：

- FSX 日常值班巡检
- 发布前质量看护
- 回归执行结果快速过一遍
- 每日自动运营播报

## 支持的工作模式

### 1. 单条运行统计

适用于你已经知道：

- `pipelineId`
- `runId`

调用：

```bash
python3 scripts/bits_pipeline_report.py {pipelineId} {runId}
```

或：

```bash
python3 scripts/bits_pipeline_report.py --pipeline-id {pipelineId} --run-id {runId}
```

### 2. 单条固定流水线看护

适用于固定看护一条 FSX 流水线，脚本会：

1. 用写死的 service-account secret 换 JWT
2. 调 `GetPipeline` 获取 `last_run_id`
3. 调 `GetPipelineRun` 获取最新 run
4. 只接受“最新且已结束”的 run
5. 生成该 run 的统计产物

调用：

```bash
python3 scripts/watch_single_pipeline.py
```

### 3. 固定五条 FSX 流水线看护

适用于日常看护固定的 FSX 流水线集合。脚本会顺序处理五条流水线：

- `1073215225602`
- `656544971778`
- `410812259074`
- `1119183026434`
- `865297825538`

调用：

```bash
python3 scripts/watch_fixed_pipelines.py
```

### 4. 飞书电子表格 + 群播报

适用于“基于固定五条流水线的结果，自动生成飞书日报”的场景。

当前真实工作流是：

1. 先执行固定五条流水线看护
2. 生成三份总 CSV
3. 新建一个当天的飞书电子表格
4. 将三份 CSV 按顺序写入同一个 `Sheet1`
5. 用 `coco` 基于 `overview_all.csv` 和 `top10_jobs_all.csv` 生成中文日报
6. 将日报文本和当天电子表格链接发送到固定飞书群
7. 成功后清理本地生成的 CSV，避免磁盘膨胀

调用：

```bash
python3 scripts/daily_watch_publish.py
```

如果只想复用本地已经存在的三份总 CSV，而不重新抓取流水线，可调用：

```bash
python3 scripts/daily_watch_publish.py --skip-watch
```

## 鉴权说明

本 Skill 当前工作流主要涉及两类鉴权：

### 路径 A：Bits OpenAPI

`bits_pipeline_report.py` 默认从环境变量读取 JWT，例如：

- `AIME_USER_CLOUD_JWT`
- `AIME_USER_CODE_JWT`
- `USER_CLOUD_JWT`
- `IRIS_USER_CLOUD_JWT`

### 路径 B：固定看护脚本

`watch_single_pipeline.py` 和 `watch_fixed_pipelines.py` 会自行：

1. 用写死的 service-account secret 调 `https://cloud.bytedance.net/auth/api/v1/jwt`
2. 从响应头取 `X-Jwt-Token`
3. 用以下 header 调 Bits OpenAPI：
   - `x-jwt-token`
   - `username: sunjunhao.39`
   - `domain: pipelines_open;v1`

### 路径 C：飞书 Sheets / IM

`daily_watch_publish.py` 当前采用：

- `Sheets`：`user` 身份
- `群消息发送`：`bot` 身份

这样可以避开多维表格 OpenAPI 的字段能力限制，同时保持群播报稳定。

## 本地产物

### 单条模式

默认生成三份 CSV：

1. `overview_{pipelineId}_{runId}.csv`
2. `jobs_{pipelineId}_{runId}.csv`
3. `top10_jobs_{pipelineId}_{runId}.csv`

说明：

- `stats_{pipelineId}_{runId}.json` 默认关闭
- 如需恢复，可修改脚本中的写死开关 `DEFAULT_INCLUDE_STATS`

### 固定五条看护模式

默认不再为每条流水线分别产出三套 CSV，而是聚合成三份总表：

1. `overview_all.csv`
2. `jobs_all.csv`
3. `top10_jobs_all.csv`

其中：

- `overview_all.csv`：每条流水线一行总体概览
- `jobs_all.csv`：所有流水线的全量 Job 明细拼接
- `top10_jobs_all.csv`：每条流水线各自的 TOP10 失败 Job 拼接

### 飞书发布模式

`daily_watch_publish.py` 在运行过程中会依赖上面这三份总 CSV。

但当前真实行为是：

- 成功写入飞书电子表格并完成群消息发送后
- 会自动清理本地生成文件

也就是说，这三份总 CSV 在发布成功后默认不会长期留在本地目录中。

## 飞书输出形态

当前飞书侧的真实交付形式不是 Base，而是：

1. 每天新建一个新的飞书电子表格
2. 表格标题格式：`FSX 核心流水线每日看护-YYYY-MM-DD`
3. 只写入 `Sheet1`
4. 在同一个工作表中按以下顺序分段写入：
   - `总览`
   - `TOP10`
   - `全量`
5. 各段之间空 3 行，方便阅读
6. 最终将电子表格链接附在群消息中

这样做的原因是：

- CSV 天然适合 `Sheets`
- 不依赖多维表格的动态建字段能力
- 比单独发 3 个附件更易读
- 对值班同学更接近日报场景

## 统计口径

- **统计对象**：仅统计 `jobAtom.uniqueId == "test_framework_trigger"` 且具备有效用例数字段的 Job
- **数据兜底**：
  1. 优先读取 `jobAtom.output`
  2. 其次解析 `failReason.message` 中的 JSON
  3. 最后再调 `job_runs` 详情接口补齐
- **总通过率**：`(总成功用例数 / 总用例数) * 100%`
- **Job 失败率**：`(Job 失败用例数 / Job 总用例数) * 100%`
- **失败贡献占比**：`(Job 失败用例数 / 总失败用例数) * 100%`

## AI 播报口径

`daily_watch_publish.py` 调用 `coco` 时只给它两份输入：

- `overview_all.csv`
- `top10_jobs_all.csv`

不会让 `coco` 读取全量 `jobs_all.csv`。

目的很明确：

- 让它只做轻量文本生成
- 聚焦值班播报需要的关键信息
- 避免把任务交给它做过重的数据处理

如果 `coco` 调用失败，脚本会回退到规则模板，仍然产出一版可发送的简报。

## 参考模板

如果后续要调整飞书群播报文案或日报开头结构，可参考：

- `references/opening_template.md`

当前推荐的阅读与输出顺序是：

1. 先看 `overview_all.csv`
2. 再看 `top10_jobs_all.csv`
3. 最后看 `jobs_all.csv`
4. 飞书电子表格中也按这个顺序落地

## 本地配置约定

当前这套 skill 不再把敏感配置写死在代码里。

脚本会优先从同级目录读取：

- `scripts/local_config.json`

建议做法是：

1. 复制 `scripts/local_config.example.json`
2. 生成本机自己的 `scripts/local_config.json`
3. 在其中填写：
   - `bits_sa_secret`
   - `username`
   - `fixed_pipeline_ids`
   - `chat_id`
   - 电子表格标题前缀和身份类型等参数

其中：

- `local_config.example.json` 可提交
- `local_config.json` 属于本地私有配置，已通过 skill 目录内的 `.gitignore` 隔离，不应上传到 GitHub
