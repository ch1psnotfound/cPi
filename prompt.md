## 背景风格
将Agent工程论从fprime参考移植到cFS上，要确保准确，需要根据代码/参考资料等核实所产出描述。

## 任务描述：
需要实现一个针对星务软件开发（使用NASA cFS 框架）的Coding Agent，能够生成高质量的cFS代码。

## 项目文件与资料
cFE应用开发指南
```
/Users/ch1ps/proj/cPi/material/cFE Application Developers Guide.md
```
cfs
```
/Users/ch1ps/proj/cPi/cfs
```
fprime
```
/Users/ch1ps/proj/cPi/fprime
```
pi
```
/Users/ch1ps/proj/cPi/pi
```

## 项目规划：
底层Coding Agent 采用开源项目 Pi。
```
/Users/ch1ps/proj/cPi/pi
```
Agent工程论参考fprime已经实现的思路，按照它在 fprime 仓库中的职责，分别映射到 Pi 的项目指令、Skills、TypeScript Extension 和 Subagents。
```
/Users/ch1ps/proj/cPi/fprime/AGENTS.md
```


## Fprime与Pi机制映射

|F Prime 中的内容|在 Pi 中的落点|作用|
|---|---|---|
|根目录 `AGENTS.md`|项目级 `AGENTS.md`|全局工程规则、仓库导航、任务路由|
|`.github/skills/`|Pi Skills|具体任务的操作流程和专业知识|
|`.github/agents/`|Pi Subagents / Agent 配置|专门角色、任务委派、审查流程|
|工程命令和构建流程|Extension Tools|让 Agent 实际执行构建、测试等操作|
|`tool_call` 等 Hooks|TypeScript Extension|工具门禁、流程约束、状态管理|
|FPP 导航、代码生成等能力|Skills + Extension Tools|Skill 指导如何做，Tool 负责确定性执行|

## 当前进度
根据
```
/Users/ch1ps/proj/cPi/fprime/AGENTS.md
```
已经完成了第一部分 Repository map 和  Anatomy of a component  的撰写，现在要进行

最终版文件位于（目前还不完整，在内容上追加即可，要求是英文版）。

```
/Users/ch1ps/proj/cPi/cfs/AGENTS.md
```
