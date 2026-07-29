# sleep-routine-coach

> 一个会在正确时间轻轻提醒、又知道什么时候保持安静的隐私优先睡眠习惯 Agent。

**主动，但克制。** 它用一声“晚安”和“早安”完成低负担记录；数据默认只保存在本地；所有主动提醒都要先确认具体时间、允许时段和发送渠道；它不提供医疗诊断，也不声称治疗或治愈失眠。Skill 遵循通用 [Agent Skills `SKILL.md` 规范](https://agentskills.io/specification)，并针对 OpenClaw 的调度能力提供集成。

```text
Agent：准备睡觉时对我说声晚安就好。
User：晚安
Agent：晚安 🌙 已记录 23:06，我会保持安静，明早见。

User：早安
Agent：早安 ☀️ 已记录 07:32。昨晚大概多久睡着？
```

## 立即体验

在本仓库根目录安装到当前 OpenClaw 工作区：

```bash
openclaw skills install ./skills/sleep-routine-coach --as sleep-routine-coach
```

然后开始对话：

```text
使用 $sleep-routine-coach 帮我建立一个温和、隐私优先的睡眠作息。
```

安装不会创建定时任务，也不会开始保存数据。首次设置会一次只问一个问题，并在任何持久化之前明确询问本地保存同意。

发布到 ClawHub 后，一键安装：

```bash
openclaw skills install @raindongdry/sleep-routine-coach
```

安装命令和 Cron 参数已依据 [OpenClaw Skills 官方文档](https://docs.openclaw.ai/tools/skills)及本机 OpenClaw `2026.7.1-2` CLI 帮助于 2026-07-29 核查。完整步骤见 [安装说明](docs/INSTALLATION.zh-CN.md)。

## 它能做什么

- 用自然的“晚安”记录准备入睡时间，随即进入夜间静默。
- 用“早安”记录报告醒来时间，每天最多追问两个短问题。
- 处理“昨晚其实一点才睡着”“刚才不算晚安”“推迟二十分钟”等纠错与偏好。
- 在明确同意后准备睡前降速、可选饮水收尾、晚安邀请、目标起床、晨间记录和周摘要提醒。
- 每阶段最多一条未回复提醒；连续忽略后自动降频，不制造压力。
- 本地查看、修正、导出、删除单日、删除全部及停止收集。
- 正确处理跨午夜、IANA 时区、夏令时和时区变化。
- 只在信息足够时估算睡眠时长，并明确区分报告值、估算值和推导值。

## 设计边界

`goodnight_at` 只是“准备入睡”，不是实际入睡；`morning_at` 是用户报告醒来，不等于离床；两者相减只叫“报告时间窗口”，不会冒充睡眠时长。缺失数据保持为空，周摘要只给描述性趋势，不把相关性写成因果。

精确时间使用 OpenClaw Cron 或等价调度器；Heartbeat 只适合在授权活跃时段内做周期性、自适应判断。`SKILL.md` 自身不会在后台运行。调度脚本只生成预览命令，从不执行 OpenClaw。

## 隐私模型

默认数据目录：

1. `SLEEP_ROUTINE_DATA_DIR`；
2. `$XDG_DATA_HOME/sleep-routine-coach`；
3. `~/.local/share/sleep-routine-coach`。

本地文件为 `profile.json`、`sleep-records.json` 和 `reminders.json`，脚本尽力使用目录 `0700`、文件 `0600` 权限。任何记录都需要明确同意；仓库的 `.gitignore` 排除了这些运行时文件和导出。

“本地保存”只描述本 Skill 的文件存储。你配置的模型服务和消息渠道仍可能按各自政策处理对话或提醒内容。详见 [隐私说明](PRIVACY.md)。

## 数据字段

核心字段包括：

`date`、`timezone`、`goodnight_at`、`sleep_latency_minutes`、`reported_sleep_at`、`estimated_sleep_at`、`morning_at`、`out_of_bed_at`、`night_awakenings`、`nocturia_count`、`rested_score`、`notes`、`source`、`created_at`、`updated_at`。

另有 `night_awake_minutes`、`reported_window_minutes`、`estimated_sleep_duration_minutes`、`provenance` 和 `audit_history`，用于安全估算、来源区分和修正审计。完整定义见 [数据模型](skills/sleep-routine-coach/references/data-schema.md)。

## 数据控制

以下命令只操作你指定的本地数据目录：

```bash
python3 skills/sleep-routine-coach/scripts/manage_profile.py --data-dir /private/path show
python3 skills/sleep-routine-coach/scripts/manage_profile.py --data-dir /private/path export --output sleep.export.json
python3 skills/sleep-routine-coach/scripts/record_sleep_event.py --data-dir /private/path delete --date 2026-07-29
python3 skills/sleep-routine-coach/scripts/manage_profile.py --data-dir /private/path delete-all --confirm
```

停止收集会撤销调度授权，但已有外部 Cron 任务仍需在确认后单独禁用或删除；这是为了不让本地脚本暗中修改外部状态。

## 健康与饮水边界

本项目不设置统一“最后一杯水”时间，不鼓励脱水。只有经常起夜且主动启用的用户才会看到晚间大量饮水收尾提醒；口渴仍可小口饮水。孕期、剧烈运动、高温环境、肾脏/心血管疾病、糖尿病或利尿剂使用等情况不提供个体饮水建议。

若起夜持续影响睡眠，或伴随明显打鼾、呼吸暂停/喘醒、异常口渴、疼痛等情况，会建议寻求专业评估。健康文案只依据 [NIH/NHLBI、NIDDK、AASM 和 NHS 来源](skills/sleep-routine-coach/references/evidence-sources.md)。

## 开发与验证

项目只依赖 Python 标准库（Python 3.10+，需 `zoneinfo` 时区数据库）：

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skills/sleep-routine-coach
```

测试覆盖正常晚安/早安、跨午夜、DST、重复事件、补录修正、拒绝保存、静默、提醒动作/降频、缺失值、导出删除、安全边界和“未授权不创建 Cron”等场景。

## 项目结构

```text
skills/sleep-routine-coach/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
└── references/
tests/
docs/
```

更多对话见 [完整示例](docs/EXAMPLES.zh-CN.md)。欢迎阅读 [贡献指南](CONTRIBUTING.md) 和 [安全政策](SECURITY.md)。

## License

仓库代码与文档采用 [MIT License](LICENSE)，版权归项目贡献者。注意：ClawHub 当前会以 MIT-0 条款分发发布到其平台的 Skill bundle；发布者应在发布前确认接受该平台条款。
