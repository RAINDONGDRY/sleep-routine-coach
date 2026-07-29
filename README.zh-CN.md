# sleep-routine-coach

[English](README.md) | **简体中文**

> 用小步调整帮你慢慢靠近理想作息，每天在合适的时间提醒你为睡眠做准备，并用“晚安/早安”完成低负担记录的隐私优先睡眠习惯 Agent。

你是否也曾不止一次想过：明天开始，我要早点睡、早点起？

你想要一段不被消息打断的清晨，慢慢吃顿早餐，读几页书，出去走走或运动一下；也想在工作和生活真正开始之前，先把一天理清楚，而不是每天睁眼就匆忙追赶时间。

于是你调早了闹钟，列好了计划，甚至认真坚持了几天。可一次加班、一场聚会、睡前多刷了一会儿手机，或者一个睡过头的周末，作息又悄悄回到了原点。下一次重新开始时，目标更狠，提醒更多，压力也更大。

这不一定是因为你“不够自律”。很多作息工具只负责在早上把你叫醒，却很少关心前一晚是怎样结束的；它们擅长催促和打卡，却不太知道什么时候应该闭嘴。

`sleep-routine-coach` 想做的事情很具体：每天根据你的作息，在合适的时间提醒你开始收尾——结束手上的事、把节奏放慢、为入睡留出过渡，而不是等到闹钟响起时才想起昨晚又睡晚了。

“晚安”和“早安”承担的是另一件事：用最少的动作收集准备入睡、醒来和主观感受等数据，再从一段时间的记录中观察作息趋势。它们不是这个 Agent 主动性的来源，也不会取代每天的睡前准备提醒。

**主动，但克制。** 睡前准备提醒每天最多发送一次，没有回应就不追着催；你说“晚安”后，它会保持安静。数据默认留在本地，提醒时间、允许时段和发送渠道都由你决定。它不是医疗诊断工具，也不声称治疗或治愈失眠。

```text
Agent：离你计划睡觉的时间还有一会儿，可以开始收尾、把节奏放慢了。
       [完成] [推迟] [跳过] [关闭此提醒]

Agent：准备睡觉时跟我说声晚安就好，我会记下时间，然后保持安静。
User：晚安
Agent：晚安 🌙 已记录 23:06，我会保持安静，明早见。

User：早安
Agent：早安 ☀️ 已记录 07:32。昨晚大概多久睡着？
```

它遵循通用 [Agent Skills `SKILL.md` 规范](https://agentskills.io/specification)，并可通过 OpenClaw Cron 在获得授权后主动提醒。

## 立即体验

在本仓库根目录安装到当前 OpenClaw 工作区：

```bash
openclaw skills install ./skills/sleep-routine-coach --as sleep-routine-coach
```

然后开始对话：

```text
使用 $sleep-routine-coach 帮我建立一个温和、隐私优先的睡眠作息。
```

安装不会创建定时任务，也不会开始保存数据。快速设置一次只问一个问题，但只收集尚缺的时区、大致计划睡眠时间和本地保存同意。

从 ClawHub 一键安装：

```bash
openclaw skills install @raindongdry/sleep-routine-coach
```

安装命令和 Cron 参数已依据 [OpenClaw Skills 官方文档](https://docs.openclaw.ai/tools/skills)及本机 OpenClaw `2026.7.1-2` CLI 帮助于 2026-07-29 核查。完整步骤见 [安装说明](docs/INSTALLATION.zh-CN.md)。

## 它会怎么陪你

- **把很晚的睡眠时间一点点往前移。** 如果你经常 03:00 左右才开始睡，它会先给出可以逐段确认的 15 分钟调整计划，而不是要求你一夜之间改到 23:00。
- **不要求每天睡够固定时长。** 起床时间和睡眠长短可以变化，只作为可选观察，不作为推进计划的条件。
- **每天提醒开始准备。** 以你的睡眠窗口为基准，在经过你确认的时间提醒收尾和降速；工作日、周末可以不同。
- **睡前不轰炸。** 每个阶段最多轻轻提醒一次；没有回应就不继续催，连续忽略后还会自动降频。
- **晚安是记录，不是催促。** 它记录的是“准备睡觉时间”，不是假装知道你真正几点睡着；记录后立即进入夜间静默。
- **早安是晨间数据入口。** 一句早安完成报告醒来时间，再问最多两个很短的问题，为后续趋势分析补充必要信息。
- **生活有变化，记录也能改。** “昨晚其实一点才睡着”“刚才不算晚安”“早上七点就醒了”都可以自然修正，并保留必要的修正记录。
- **提醒会看你的反应。** 可以完成、推迟、跳过或关闭；连续几次没有回应后，它会主动降低频率。
- **数据由你掌握。** 查看、修正、导出、删除某一天、删除全部或彻底停止收集，都在本地完成。
- **不编造漂亮数字。** 跨午夜、时区和夏令时交给脚本计算；不知道实际入睡时间时，就让数据保持空白。

## 不靠“一夜重置”，循序渐进调整睡眠时间

假设你平时大约 03:00 开始睡，希望逐步调整到 23:00。默认计划每次提前 15 分钟，每个阶段先保持两个晚上：

| 阶段 | 开始降速 | 计划睡眠时间 |
| --- | ---: | ---: |
| 1 | 01:45 | 02:45 |
| 2 | 01:30 | 02:30 |
| … | … | … |
| 16 | 22:00 | 23:00 |

计划只调整“计划睡眠时间”这个提醒锚点。起床提醒独立且可选，Skill 不要求每天睡眠时长相同。到了复盘日期，它只会询问你要继续、保持、退回一步、暂停还是取消，不会因为日期到了就自动推进，也不会把缺失记录当作已经完成。

15–30 分钟的调整步长来自本项目记录的公共睡眠习惯建议，详见[证据来源](skills/sleep-routine-coach/references/evidence-sources.md)；“每阶段两个晚上”是项目采用的保守默认值，不是医疗处方。这个功能只帮助建立习惯：它不诊断昼夜节律障碍，不给出褪黑素剂量、个体化光照治疗或睡眠限制方案。

## 设置更短，只做一次有意义的确认

普通设置不再逐项追问所有可选偏好，只询问时区、大致计划睡眠时间和本地保存同意。起床提醒、周末差异、饮水、提醒强度和每周摘要，都等你真正需要时再设置。

主动提醒会先显示一份不会执行的预览，把精确时间、时区、渠道、接收目标、允许时段和静默规则放在同一条消息里确认。明确同意后重新生成并核对一致即可创建，不再重复询问同一件事。

可以这样开始：

```text
使用 $sleep-routine-coach。我平时 03:00 睡、12:00 起，想慢慢调整到 23:00。请先给我看完整计划，不要直接保存或创建提醒。
```

## 为什么不是又一个打卡工具

睡眠习惯不是一条每天都能完美执行的直线。旅行、工作、照顾家人、情绪和身体状态都会让计划发生变化。这个项目不计算“断签”，不展示红色失败提示，也不会把偶尔晚睡解释成意志力问题。

它更关心的是：睡前准备提醒有没有帮助你更早开始收尾？你的作息是否正在慢慢变得稳定？什么时间的提醒真正有用？哪些提醒经常被忽略，应该减少或关闭？“晚安/早安”收集到的数据会用于回答这些问题。每周摘要只描述已经记录到的趋势，不给你打分，也不把相关性说成原因。

## 设计边界

`goodnight_at` 只是“准备入睡”，不是实际入睡；`morning_at` 是用户报告醒来，不等于离床；两者相减只叫“报告时间窗口”，不会冒充睡眠时长。缺失数据保持为空，周摘要只给描述性趋势，不把相关性写成因果。

精确时间使用 OpenClaw Cron 或等价调度器；Heartbeat 只适合在授权活跃时段内做周期性、自适应判断。`SKILL.md` 自身不会在后台运行。调度脚本只生成结构化 `executable` + `argv` 预览，从不执行 OpenClaw，也不生成供 shell 求值的命令字符串。

## 隐私模型

默认数据目录：

1. `SLEEP_ROUTINE_DATA_DIR`；
2. `$XDG_DATA_HOME/sleep-routine-coach`；
3. `~/.local/share/sleep-routine-coach`。

本地文件为 `profile.json`、`sleep-records.json`、`reminders.json`，以及仅在明确确认渐进计划后创建的 `sleep-shift-plan.json`。脚本尽力使用目录 `0700`、文件 `0600` 权限。任何记录都需要明确同意；仓库的 `.gitignore` 排除了这些运行时文件和导出。

“本地保存”只描述本 Skill 的文件存储。你配置的模型服务和消息渠道仍可能按各自政策处理对话或提醒内容。详见 [隐私说明](PRIVACY.md)。

## 数据字段

核心字段包括：

`date`、`timezone`、`goodnight_at`、`sleep_latency_minutes`、`reported_sleep_at`、`estimated_sleep_at`、`morning_at`、`out_of_bed_at`、`night_awakenings`、`nocturia_count`、`rested_score`、`notes`、`source`、`created_at`、`updated_at`。

另有 `night_awake_minutes`、`reported_window_minutes`、`estimated_sleep_duration_minutes`、`provenance` 和 `audit_history`，用于安全估算、来源区分和修正审计。完整定义见 [数据模型](skills/sleep-routine-coach/references/data-schema.md)。

## 数据控制

以下命令只操作你指定的本地数据目录：

```bash
python3 skills/sleep-routine-coach/scripts/manage_profile.py --data-dir /private/path show
python3 skills/sleep-routine-coach/scripts/manage_sleep_shift.py --data-dir /private/path show
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

测试覆盖正常晚安/早安、跨午夜、DST、重复事件、补录修正、拒绝保存、渐进阶段计算与控制、随阶段变化的提醒、静默、提醒降频、缺失值、导出删除、安全边界和“未授权不创建 Cron”等场景。

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

## 许可证

仓库代码与文档采用 [MIT License](LICENSE)，版权归项目贡献者。注意：ClawHub 当前会以 MIT-0 条款分发发布到其平台的 Skill bundle；发布者应在发布前确认接受该平台条款。
