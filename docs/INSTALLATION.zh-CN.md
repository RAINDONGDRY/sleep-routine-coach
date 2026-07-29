# 安装与 OpenClaw 集成

核查日期：2026-07-29。CLI 验证版本：OpenClaw `2026.7.1-2`。

## 从本地仓库安装

在仓库根目录运行：

```bash
openclaw skills install ./skills/sleep-routine-coach --as sleep-routine-coach
```

OpenClaw 默认安装到当前活动工作区的 `skills/`。本项目不会建议自动安装到个人 Skills 目录；只有用户明确需要所有本地 Agent 共享时才考虑官方的 `--global` 选项。

安装后重新开始/刷新会话，让 OpenClaw 重新发现 Skill，然后说：

```text
使用 $sleep-routine-coach 帮我设置作息。
```

## 从 ClawHub 安装

发布后使用发布者限定的引用，避免同名歧义：

```bash
openclaw skills install @raindongdry/sleep-routine-coach
```

可在安装后检查 ClawHub 信任信息：

```bash
openclaw skills verify @raindongdry/sleep-routine-coach
```

## 从 GitHub 获取再安装

```bash
git clone https://github.com/RAINDONGDRY/sleep-routine-coach.git
cd sleep-routine-coach
openclaw skills install ./skills/sleep-routine-coach --as sleep-routine-coach
```

本仓库采用 catalog 布局，`SKILL.md` 位于 `skills/sleep-routine-coach/`，因此本地目录安装最清晰。不要编写假设 `SKILL.md` 位于仓库根目录的 Git 安装命令。

## 主动提醒

安装 Skill 不会创建任何 Cron/Heartbeat。完成首次设置后，Agent 必须：

1. 单独征得本地保存同意。
2. 默认只预览 `wind_down` 和 `sleep_time`；其他提醒等用户需要时再添加。
3. 用 `build_reminder_schedule.py plan --reminder wind_down --reminder sleep_time` 生成不会执行的预览。
4. 把提醒类型、精确时间、时区、渠道、目标、允许时段和静默规则放在同一条消息中确认一次。
5. 明确同意后记录调度授权，重新生成并核对预览；内容一致即可提交，不要重复询问。
6. 优先使用宿主的原生 Cron API。若宿主只能启动进程，必须把脚本返回的 `executable` 与 `argv` 分开传递并关闭 shell 解析，禁止拼接或求值命令字符串。
7. 将每个成功返回的 job ID 用 `build_reminder_schedule.py register-job` 保存到本地提醒状态。

启用渐进式睡眠时间计划时，每次确认进入新阶段后都要重新运行调度预览，因为睡前准备和计划睡眠时间会变化。起床提醒保持独立且可选。先展示替换后的时间和目标任务，再通过可信调度适配器更新；本地脚本不会自行修改外部 Cron。

生成的命令采用当前官方 CLI 参数，包括 `--tz`、`--session isolated`、`--announce`、`--channel` 和 `--to`。任务创建需要 OpenClaw 的 `operator.admin` 权限。

查看与管理外部任务：

```bash
openclaw cron list --all
openclaw cron show <job-id>
openclaw cron edit <job-id> --disable
openclaw cron remove <job-id>
```

使用前请以当前 `openclaw cron --help` 为准。

## Heartbeat

Heartbeat 适合做非精确的周期性判断和自适应检查。将其 `activeHours` 限制在用户允许的主动时段，并设置明确时区。精确的睡前/起床提醒仍使用 Cron。

官方资料：

- [OpenClaw Skills](https://docs.openclaw.ai/tools/skills)
- [OpenClaw Cron CLI](https://docs.openclaw.ai/cli/cron)
- [OpenClaw Heartbeat](https://docs.openclaw.ai/gateway/heartbeat)
- [ClawHub](https://docs.openclaw.ai/clawhub)
