# NERO 双臂双手交付工作区

本仓库沉淀 NERO 双七自由度机械臂 + 双 LinkerHand L6 灵巧手的部署、调试、验收证据和后续操作流程。

截至 2026-07-02，S0-S14 已完成，S15 双臂双手 elbow-curl/fist 演示已按现场 operator report 跑通。当前下一 gate 是使用默认 `zero` 姿态做回零复验并关闭 S15 交付闭环。该系统仍处于 bring-up/demo 阶段，不是接触式抓取、交接或近距离协作 manipulation 原语。

English entry: [README_EN.md](README_EN.md)  
完整流程计划: [PLAN.md](PLAN.md) / [PLAN_EN.md](PLAN_EN.md)

## 必读入口

- [Agent Operating Rules](agent.md): 后续协作者必须遵守的事实源、记录和安全规则。
- [当前 Bring-Up 状态](docs/status/current_bringup_status.md): 当前配置、阶段状态、验收结果和下一步。
- [部署日志](docs/status/deployment_log.md): 每一步真实执行、证据、风险和后续动作。
- [Bring-Up Checklist](docs/status/bringup_checklist.md): 现场复验清单。
- [Setup Framework](docs/status/setup_framework.md): 工程分层、硬件事实、默认配置。
- [机器人部署与调试行动路线](docs/phases/机器人部署与调试行动路线.md): 历史阶段路线和详细记录。
- [S15 双臂双手协调计划](docs/phases/s15_dual_arm_hand_coordination_plan.md): 当前 hybrid 控制架构和 S15 gate。
- [S15 操作流程](docs/phases/s15_arm_hand_coordination_sequence_plan.md): observe/dry-run/active/execute 顺序。
- [S15 回零与 elbow-curl 设计](docs/phases/s15_return_to_initial_and_elbow_curl_design.md): 回零目标、手势定义和左右臂映射。

## 目录结构

```text
.
├── config/                 # 固定环境变量和设备映射
├── docker/                 # ROS2 Humble 容器
├── examples/               # SDK-only 示例
├── rviz/                   # RViz 配置
├── scripts/                # 已验收操作脚本，路径保持稳定
├── docs/
│   ├── status/             # 当前状态、日志、checklist、工程框架
│   ├── phases/             # S2-S15 阶段计划、设计和操作流程
│   ├── results/            # 验收结果、audit、diagnostics
│   ├── evidence/           # 图片证据和 ROS 快照入口
│   ├── assets/             # 手册、协议表、CAD/STEP/STL
│   └── upstream/           # 上游仓库分析和 review
└── upstream/               # ignored，本地上游源码证据缓存
```

ROS 只读快照已归档到 `docs/evidence/ros_snapshots`。该目录来自历史 S9/S10-S14 快照集合，后续新快照也写入同一 evidence 路径。

## 固定控制架构

| 设备 | 接口 | 控制路径 |
| --- | --- | --- |
| Arm A / 右侧 | `can_arm_a`, USB `1-3.4.1:1.0`, ROS `/arm_a` | ROS2 `agx_arm_ros` |
| Arm B / 左侧 | `can_arm_b`, USB `1-3.4.3:1.0`, ROS `/arm_b` | ROS2 `agx_arm_ros` |
| Left hand | `can1`, USB `1-3.4.4:1.0` | LinkerHand SDK wrapper |
| Right hand | `can2`, USB `1-3.4.2:1.0` | LinkerHand SDK wrapper |

不要在 ROS arm driver active 时运行 arm SDK motion。不要在项目 hand wrapper active 时运行 LinkerHand GUI/demo/gesture 脚本。

## 快速命令

```bash
source config/nero.env
bash scripts/check_environment.sh
bash scripts/s10_control_source_audit.sh
```

启动 S15 只读观察和 RViz：

```bash
NERO_CONTAINER_NAME=nero-humble-s15-observe \
  bash scripts/run_humble_container.sh --allow-xhost \
    bash /workspace/nero/scripts/launch_s15_dual_arm_hand_observe.sh --readonly
```

S15 回零 dry-run：

```bash
NERO_CONTAINER_NAME=nero-humble-s15-init \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_return_to_initial.py
```

S15 回零执行：

```bash
NERO_CONTAINER_NAME=nero-humble-s15-init \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_return_to_initial.py \
      --execute \
      --allow-wide-motion \
      --confirm-clearance \
      --confirm-rviz-visible
```

S15 双臂双手 elbow-curl/fist dry-run：

```bash
NERO_CONTAINER_NAME=nero-humble-s15-elbow-demo \
  bash scripts/run_humble_container.sh \
    python3 /workspace/nero/scripts/ros_s15_elbow_curl_demo.py \
      --side both \
      --left-j1-delta-deg -10 \
      --right-j1-delta-deg -20 \
      --left-j4-delta-deg 15 \
      --right-j4-delta-deg 15 \
      --arm-profile single-target \
      --hand-timing during-curl \
      --hand-close-fraction 0.5
```

执行前必须先停止 readonly observe，并用 `--active` 重启观察/driver session。

## 硬安全边界

- 默认状态是不运动；所有真实 motion 都必须 dry-run 先过。
- 外部供电不超过 25V，电流能力不小于 10A；末端 XT30 2+2 为 24V、2A MAX。
- 任何新控制路径、较大动作、接触式任务、MoveIt execute、Cartesian motion、raw CAN motion、MIT 控制、零点设置、固件升级、碰撞等级修改，都需要单独计划和验收。
- S15 RViz visual anchor 只用于观察，不用于控制、规划、限位、标定或语义验收。
- USB/CAN 或机械臂电源重连后等待约 20 秒，再判断 `candump` 或 ROS topic 是否正常。
- 如果 RViz 与实物姿态不一致，先运行 `scripts/s15_rviz_pose_diagnostics.sh`，不要执行 motion。

## Git 包边界

提交项目自有脚本、配置、文档、证据、图片和 CAD 资产。以下内容故意不提交：

- `upstream/`: 上游源码缓存，可按 README/PLAN 记录复现。
- `.venv/`: 本机 SDK 虚拟环境。
- `build/`, `install/`, `log/`: ROS/colcon 构建产物。
- `.agents/`, `.codex/`, `__pycache__/`: 本地运行缓存。
- `docs/vendor/`: 大体积 vendor 包和展开目录，保留 review 文档即可。

## 上游依赖复现

```bash
mkdir -p upstream

git clone https://github.com/agilexrobotics/agx_arm_ros.git upstream/agx_arm_ros
git -C upstream/agx_arm_ros checkout c73d33f2ab377447261423f1b881bd89c6663627

git clone https://github.com/agilexrobotics/pyAgxArm.git upstream/pyAgxArm
git -C upstream/pyAgxArm checkout a226840db0c3d5c5dc7f3ec78d6cef1a6800f9e6

git clone https://github.com/agilexrobotics/piper_ros.git upstream/piper_ros
git -C upstream/piper_ros checkout 2dc30fca68cbf4e04d1d0bc15c123d026380ece7
```

LinkerHand SDK 为用户提供或私有访问来源：

```bash
git clone https://github.com/LV-Robotics-Lab/linkerhand_sdk upstream/linkerhand_sdk
```
