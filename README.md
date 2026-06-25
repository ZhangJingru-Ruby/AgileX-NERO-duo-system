# NERO Arm 部署与调试工作区

这个目录用于沉淀 NERO 七自由度双臂系统的本地部署、调试、验收与注意事项。当前 S10 双臂首次低速运动已关闭通过，下一目标是建立 S11 双臂实验坐标、TF 和日志基线。

## 必读入口

- [Agent Operating Rules](agent.md)：后续调试代理/协作者必须遵守的事实源、记录和路线更新规则。
- [机器人部署与调试行动路线](docs/机器人部署与调试行动路线.md)：主路线，包含阶段目标、执行动作、验收标准和注意事项。
- [当前 Bring-Up 状态](docs/current_bringup_status.md)：已确认配置、S0/S1 状态和图片索引。
- [部署日志](docs/deployment_log.md)：每一步实际执行、证据、选择和风险记录。
- [上游仓库分析](docs/upstream_repo_analysis.md)：本地 clone 的 AgileX ROS/SDK/URDF 仓库证据与 ROS 版本决策。
- [S2 混合部署方案](docs/s2_hybrid_host_container_plan.md)：共享 Ubuntu 20.04 主机 + Docker ROS2 Humble 的执行方案。
- [S11 双臂实验基线](docs/s11_dual_arm_experiment_baseline.md)：`lab_world`、双臂 base TF、TCP 和日志/rosbag 规则。
- [Setup Framework](docs/setup_framework.md)：工程分层、关键事实、配置边界。
- [Bring-Up Checklist](docs/bringup_checklist.md)：现场逐项检查表。
- [NERO 用户手册](docs/nero%20用户手册.md)：语雀导出的用户手册文本。
- [机械臂通信协议 V1.2.1](docs/机械臂通信协议V1.2.1.xlsx)：CAN 协议源文件。

## 本地资料状态

本地 `docs/` 已包含：

- 用户手册 Markdown：`docs/nero 用户手册.md`
- CAN 协议 Excel：`docs/机械臂通信协议V1.2.1.xlsx`
- 重复 CAN 协议副本：`docs/机械臂通信协议V1.2.1 (1).xlsx`
- 机械臂本体 STEP：`docs/nero3d.stp`
- 夹爪/灵巧手模型：`docs/nero带夹爪以及带灵巧手模型/`
- 法兰连接件模型：`docs/NERO+两指夹爪-法兰.STEP/`、`docs/NERO+强脑标准版灵巧手 法兰连接件-左右前/`
- 用户手册关键图片：`docs/pics/`
- 上游仓库证据缓存：`upstream/agx_arm_ros`、`upstream/pyAgxArm`、`upstream/piper_ros`
  可在本机存在，但不纳入 git 首次提交；复现条件见下方“上游依赖”。

## Git 包边界

本仓库提交项目自有的部署脚本、配置、现场记录、行动路线、截图、快照和本地文档证据。
以下内容故意不提交：

- `upstream/`：未修改的 AgileX 上游仓库 clone，体积约 1.3 GB，可按固定 URL 和 commit 复现。
- `.venv/`：本机 Python 虚拟环境，应由脚本重新创建。
- `build/`、`install/`、`log/`：ROS/colcon 构建产物。
- `.agents/`、`.codex/`、`__pycache__/`：本地运行缓存。

`docs/` 不在 `.gitignore` 中，属于当前部署包的一部分。

## 上游依赖

如果 `upstream/` 不存在，按以下条件恢复本地证据缓存：

```bash
mkdir -p upstream

git clone https://github.com/agilexrobotics/agx_arm_ros.git upstream/agx_arm_ros
git -C upstream/agx_arm_ros checkout c73d33f2ab377447261423f1b881bd89c6663627

git clone https://github.com/agilexrobotics/pyAgxArm.git upstream/pyAgxArm
git -C upstream/pyAgxArm checkout a226840db0c3d5c5dc7f3ec78d6cef1a6800f9e6

git clone https://github.com/agilexrobotics/piper_ros.git upstream/piper_ros
git -C upstream/piper_ros checkout 2dc30fca68cbf4e04d1d0bc15c123d026380ece7
```

当前项目实际 ROS2 工作区位于 `~/agx_arm_ws`，并由
`bash scripts/build_humble_container.sh` 和 Humble 容器内的 `colcon build`
建立；`upstream/` 是分析与复现缓存，不是运行时必须直接 source 的工作区。

## 快速开始

离线阶段先跑环境检查：

```bash
bash scripts/check_environment.sh
```

配置默认变量：

```bash
source config/nero.env
```

当前共享电脑不重装、不升级。ROS2 Humble 在 Docker 容器中运行，主机只做 SDK/CAN-only。

准备主机 SDK venv：

```bash
bash scripts/setup_host_sdk_venv.sh
```

构建并进入 ROS2 Humble 容器：

```bash
bash scripts/build_humble_container.sh
bash scripts/run_humble_container.sh
```

如果容器构建后 `~/agx_arm_ws/build`、`install`、`log` 在主机上权限异常：

```bash
bash scripts/fix_ros_ws_permissions.sh
```

上游仓库已作为证据缓存 clone 到 `upstream/`。后续正式准备 ROS2 工作区时，在 Humble
容器中执行：

```bash
mkdir -p ~/agx_arm_ws/src
cd ~/agx_arm_ws/src
git clone -b ros2 --recurse-submodules https://github.com/agilexrobotics/agx_arm_ros.git
git clone https://github.com/agilexrobotics/pyAgxArm.git
```

CAN 接入阶段，NERO 使用 CAN2.0B 标准帧、1 Mbps、Motorola/MSB 数据格式。黄色线接 CAN_H，蓝色线接 CAN_L：

```bash
bash scripts/activate_can.sh can0 1000000
candump can0
```

SDK 只读状态检查示例：

```bash
python3 examples/nero_read_state.py --connect --channel can0 --firmware v112
```

## 硬安全边界

- 供电使用 DC24V；外部供电电压不得超过 25V，电流能力不小于 10A。
- 末端 XT30 2+2 接口为 24V、2A MAX，末端 CAN 只适配松灵自有设备。
- S10 首次低速运动已通过；后续任何新控制路径或更大动作仍需按阶段闸口单独验收。
- 不在原点/奇异点附近做笛卡尔点位运动；先用低速关节运动离开奇异位形。
- MIT 控制、固件升级、零点设置、主从联动、碰撞等级修改属于高风险操作，单独审批后执行。
