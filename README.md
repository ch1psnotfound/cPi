# cPi

面向 NASA cFS 星务软件开发的 Coding Agent 项目。底层 Agent 采用 Pi，工程方法参考 F Prime，逐步建立 cFS 项目指令、Skills、工具扩展和专门角色。

## 获取项目

```bash
git clone --recurse-submodules https://github.com/ch1psnotfound/cPi.git
cd cPi
python3 scripts/apply-overlays.py
```

已经克隆但尚未初始化子模块时：

```bash
git submodule update --init --recursive
python3 scripts/apply-overlays.py
```

## 仓库组织

- `cfs/`：NASA cFS 子模块，固定在 Bundle v7.0.1。
- `fprime/`：F Prime 子模块，作为工程方法参考。
- `pi/`：Pi 子模块，作为 Agent 实现基础。
- `overlays/cfs/`：cPi 编写的 cFS 项目指令与源码导览，保留相对于 cFS 根目录的路径。
- `scripts/apply-overlays.py`：将覆盖文件放入上游工作区；遇到不同内容的已有文件会停止，避免覆盖本地修改。使用 `--check` 检查是否一致。
- `cfs-env/`：Docker 开发环境脚本、版本记录和验证说明。
- `material/`：参考指南和介绍材料。
- `assets/`：设计图及生成脚本。
- `idea.md`、`Pi解析.md`、`prompt.md`、`开发进度.md`：设计思路、背景与进度。

子模块版本由本仓库提交固定；克隆时不会自动跟随上游最新分支。不要直接在子模块中提交到上游远端。

## 编辑 cFS 项目文档

当前需要版本控制的自编文档是 `overlays/cfs/AGENTS.md` 和 `overlays/cfs/docs/user-manual/overview/source-tree.md`。应用后分别位于 `cfs/AGENTS.md` 和 `cfs/docs/user-manual/overview/source-tree.md`。

可以在覆盖目录编辑后同步到 cFS 工作副本，也可以先编辑工作副本再同步回覆盖目录；提交前执行：

```bash
python3 scripts/apply-overlays.py --check
```

脚本不自动覆盖内容不同的文件。发生冲突时，先人工核对并同步两份内容。仅修改子模块中的未跟踪文件不会将这些内容保存进 cPi 提交，必须更新对应覆盖文件。

## cFS 验证环境

开发容器、构建、测试和启动检查见 [cfs-env/README.md](cfs-env/README.md)。本仓库不包含构建产物或本地运行日志；现有验证基线包含已知失败，详见环境说明。
