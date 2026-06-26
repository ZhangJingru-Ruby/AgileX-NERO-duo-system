# NERO Bring-Up Checklist

现场执行时按顺序勾选。任一阶段未通过，不进入下一阶段。

## S0 资料与配置

- [ ] 已阅读 [机器人部署与调试行动路线](机器人部署与调试行动路线.md)。
- [ ] 已确认 `docs/nero 用户手册.md` 可访问。
- [ ] 已确认 `docs/机械臂通信协议V1.2.1.xlsx` 为 CAN 协议主文件。
- [ ] 已确认 `docs/nero3d.stp` 和末端工具 STEP 文件存在。
- [ ] 已确认 `docs/pics/` 关键图片存在。
- [ ] 已执行 `source config/nero.env` 或明确覆盖默认变量。
- [ ] 已记录本次目标：只读调试、首次低速运动、末端工具接入或应用集成。

## S1 安全与机械准备

- [ ] 操作区域空旷，人员离开 NERO 工作半径。
- [ ] 已确认最大负载不超过 3 kg。
- [ ] 底座按安装图固定完成：70 mm x 70 mm 孔位，4 x Ø5.4 贯穿孔，M5 紧固件。
- [ ] 线束不会被 J6/J7 或末端工具拉扯。
- [ ] 已确认急停路径：Web 急停、必要时断电、后续 CAN `0x150`。
- [ ] 已理解失能/断电时机械臂可能下落。
- [ ] 已准备记录：照片、视频、终端日志、Web 截图。

## S2 主机环境

- [ ] 已阅读 `docs/upstream_repo_analysis.md`。
- [ ] 已阅读 `docs/s2_hybrid_host_container_plan.md`。
- [ ] `bash scripts/check_environment.sh` 已运行。
- [ ] 已确认当前路线为 S2A 主机 SDK/CAN-only + S2B Docker ROS2 Humble。
- [ ] 安装 `docker.io` 前已向操作者说明必要性和共享主机权限风险。
- [ ] 安装 `ethtool` 前已向操作者说明必要性和低风险性质。
- [ ] `docker` 可用，且本项目暂用 `sudo docker`，未默认加入 `docker` 组。
- [ ] 若执行 S2A，当前主机 `python-can` 版本满足 `>=3.3.4`。
- [ ] 若执行 S2A，`pyAgxArm` 可 import。
- [ ] `candump`、`cansend` 可用。
- [ ] `ethtool` 可用。
- [ ] 若执行 S2B，Docker image `nero-humble:local` 已构建。
- [ ] 若执行 S2B，容器内 OS/ROS 为 Ubuntu 22.04 + ROS2 Humble。
- [ ] 若执行 S2B，容器内 `ros2` 可用。
- [ ] 若执行 S2B，容器内 `colcon` 可用。
- [ ] 若执行 S2B，`~/agx_arm_ws` 已完成 `colcon build`。
- [ ] 若执行 S2B，`source ~/agx_arm_ws/install/setup.bash` 已执行。
- [ ] 未把 Conda Python 3.13 混入 ROS apt 工作区。

## S3 离线模型

- [ ] 已阅读 `docs/s3_model_validation.md`。
- [ ] Docker Humble 容器内 `xacro` 和 `check_urdf` 通过裸臂 NERO 模型。
- [ ] Docker Humble 容器内 `robot_state_publisher` 可加载 `nero_description.urdf`。
- [ ] RViz 可显示 `arm_type:=nero`；桌面会话中已确认 X11/RViz 路径可用。
- [ ] 7 个关节名称、父子链路、主要尺寸已核对。
- [ ] J2 URDF 限位与手册机械范围的零位/角度映射差异已记录，等待真机反馈确认。
- [ ] 末端工具配置选择已确认：`none`、夹爪、示教器或灵巧手。
- [ ] 安装姿态已确认：正装、侧装或倒装。
- [ ] 初始 TCP offset 已记录。

## S4 机械与电气连接

- [ ] 使用 DC24V 供电。
- [ ] 外部供电不超过 25V。
- [ ] 外部供电电流能力不小于 10A。
- [ ] 航插红点对齐，插接无硬插。
- [ ] 黄色线接 CAN_H。
- [ ] 蓝色线接 CAN_L。
- [ ] 红色 VCC、黑色 GND 确认无误。
- [ ] 电源分支和 CAN 分支已分开确认，红/黑不接入 USB-CAN。
- [ ] 航插红点对齐后插入，无硬插。
- [ ] USB-CAN 端子线芯在压片中心，轻拉不脱落。
- [ ] 末端 XT30 2+2 为 24V、2A MAX。
- [ ] 末端 XT30 2+2 图示方向已确认：上方电源 +/-，下方 CAN H/L。
- [ ] 未将第三方 CAN 设备接入末端 CAN。

## S5 Web 验机

- [ ] 当前操作对象已贴物理标签：Arm A 或 Arm B。
- [ ] Wi-Fi `agx-7ax-xx` 可连接，或以太网同网段配置完成。
- [ ] Web 地址 `http://192.168.31.1/` 或 `http://10.90.0.150/` 可访问。
- [ ] 可用账号 `admin`、密码 `123456` 登录。
- [ ] 状态灯绿色；若红色，已记录 Web 状态页错误。
- [ ] 已记录软件版本和关节固件版本。
- [ ] `关节1` 到 `关节7` 的电压、温度、错误和失能/使能状态已逐项记录。
- [ ] 已确认 Web 显示的 `7ax` 是当前这一条 NERO 7 轴臂。
- [ ] 双臂现场已逐台完成 S5；热点名为 `agx-7ax-armA` 和 `agx-7ax-armB`。
- [ ] 若需要有线同时接入，两条臂已有唯一有线 IP。
- [ ] 已单独记录每条臂的控制器/IP/供电/CAN 接入计划。
- [ ] 已确认当前模式。
- [ ] 未执行运动命令。

## S6 CAN 只读

- [ ] 双臂现场未把两条臂接到同一个 CAN 总线上。
- [ ] 当前操作对象已确认：Arm A 或 Arm B。
- [ ] 已用 `bash scripts/find_can_ports.sh` 记录两个 USB-CAN 模块的 bus-info。
- [ ] `bash scripts/activate_can.sh can_arm_a 1000000 "<Arm A USB bus-info>"` 成功。
- [ ] `bash scripts/activate_can.sh can_arm_b 1000000 "<Arm B USB bus-info>"` 成功。
- [ ] `ip -details link show can_arm_a` 显示 CAN UP 且 bitrate `1000000`。
- [ ] `ip -details link show can_arm_b` 显示 CAN UP 且 bitrate `1000000`。
- [ ] `can_arm_a` 和 `can_arm_b` 均为 `ERROR-ACTIVE`。
- [ ] 已记录物理 USB 口：Arm A 竖向 USB 口，Arm B 横向 USB 口。
- [ ] Web 端 CAN 通讯开关状态已确认。
- [ ] `candump can_arm_a` 能收到帧。
- [ ] `candump can_arm_b` 能收到帧。
- [ ] 两条链路均收到 `0x2A1` 状态反馈。
- [ ] 两条链路均收到 `0x2A5-0x2A7` 和 `0x2A9` 关节角反馈。
- [ ] 拔掉 Arm A CAN 时只停止 `can_arm_a` 反馈。
- [ ] 拔掉 Arm B CAN 时只停止 `can_arm_b` 反馈。
- [ ] 状态无急停、无解、奇异、超限、通信异常、碰撞、过温。
- [ ] 此阶段未发送 `cansend` 控制帧。

## S7 SDK 只读

- [ ] 已根据 Web 版本选择 `--firmware default/v111/v112/v120`。
- [ ] `python3 examples/nero_read_state.py --firmware <selector>` dry run 成功。
- [ ] `python3 examples/nero_read_state.py --connect --channel can_arm_a --firmware <selector>` 成功。
- [ ] `python3 examples/nero_read_state.py --connect --channel can_arm_b --firmware <selector>` 成功。
- [ ] SDK 关节角反馈连续。
- [ ] SDK TCP 位姿反馈连续。
- [ ] SDK 状态与 Web/CAN 一致。
- [ ] 无通信错误。

## S8 ROS 只读

- [x] 驱动 launch 成功。
- [x] 启动时显式设置 `auto_enable:=false control_enabled:=false`。
- [x] `/arm_a/feedback/joint_states` 连续。
- [x] `/arm_a/feedback/tcp_pose` 连续。
- [x] `/arm_a/feedback/arm_status` 连续。
- [x] `/arm_b/feedback/joint_states` 连续。
- [x] `/arm_b/feedback/tcp_pose` 连续。
- [x] `/arm_b/feedback/arm_status` 连续。
- [x] RViz 使用 `follow:=true control:=false`。
- [x] RViz 姿态与实物一致。
- [x] 未使用 MoveIt execute。
- [x] 未向 `/control/*` 下发运动。

## S9 标定与配置

- [x] 安装姿态已在 Web 设置并记录。
- [x] 末端执行器当前为 `默认（无加载）` 并已记录。
- [x] TCP offset 当前 ROS 默认值已记录。
- [x] 负载级别与实际一致。
- [x] 关节限位不超过手册范围。
- [x] 速度/加速度已记录。
- [x] 碰撞保护等级已记录，未设为常规 0 检测。
- [x] 零点页面已只读记录；未执行零点设置。
- [x] S9 ROS 只读快照已保存。
- [x] S9.2 三项决策已记录。
- [x] A/B 负载模式已从 `满载` 改为当前裸臂对应的空载/无负载选项。
- [x] 负载模式变更后 ROS 只读快照正常。

## S10 首次低速运动

- [x] Web/SDK/ROS/CAN 反馈均已通过。
- [x] 只有一个控制源启用。
- [x] 已阅读 `docs/s10_first_motion_plan.md`。
- [x] 已选择单条机械臂：Arm A。
- [x] ROS 只读驱动已停止，Web 是唯一控制源。
- [x] Web 已切换到 `WEB` 模式。
- [x] Web 速度百分比已设为最低可用值，优先 `5%` 或更低。
- [x] 工作空间无人。
- [x] 急停路径已确认。
- [x] 已确认 J6/J7 周围无线缆张力。
- [x] Arm A Web 使能成功。
- [x] Arm A Web 关节控制成功。
- [x] Arm A 7 个自由度均运动成功。
- [x] 停止后状态正常。
- [x] Web 动作后 ROS 只读快照已保存：`docs/s9_ros_snapshots/20260625_060810/`。
- [x] Web 动作后 A/B `err_status: 0`，关节限位和通信异常均为 `false`。
- [ ] 急停后恢复流程实际触发测试通过。
- [ ] 已阅读 `docs/s10_2_sdk_motion_plan.md`。
- [x] SDK J7 dry-run 已通过且未运动。
- [x] SDK J1 `+1 deg` dry-run 已通过且未运动。
- [x] J1 小角度扫掠区域已确认空旷。
- [x] SDK J1 `+2 deg` 目标确认为 Arm A J1-only `+2 deg`。
- [x] SDK 低速单关节运动通过。
- [x] SDK 动作后 ROS 只读快照已保存：`docs/s9_ros_snapshots/20260625_062910/`。
- [x] SDK 动作后 A/B `err_status: 0`，关节限位和通信异常均为 `false`。
- [x] 已阅读 `docs/s10_3_ros_motion_plan.md`。
- [x] ROS Arm A control driver 已以 `auto_enable:=true control_enabled:=true speed_percent:=5` 启动。
- [x] ROS dry-run 目标确认为 Arm A `joint1`-only `+2 deg`。
- [x] ROS 低速单关节运动通过。
- [x] ROS 动作后 ROS 只读快照已保存：`docs/s9_ros_snapshots/20260625_064243/`。
- [x] ROS 动作后 A/B `err_status: 0`，关节限位和通信异常均为 `false`。
- [x] 已阅读 `docs/s10_4_stop_recovery_closure.md`。
- [x] `scripts/s10_control_source_audit.sh` 语法检查通过。
- [x] Arm A ROS control driver 已停止或确认未运行。
- [x] 已在真实桌面终端运行 `bash scripts/s10_control_source_audit.sh`。
- [x] 已确认无 SDK/ROS motion 脚本运行。
- [x] 已确认 Web 无主动运动命令。
- [x] 已记录交接状态，推荐为 `handoff_to_arm_b`。
- [x] S10.4 停止/恢复/安全收束流程通过。

## S10.5 Arm B 首次 Web 运动复刻

- [x] 已阅读 `docs/s10_5_arm_b_first_motion_plan.md`。
- [x] 已确认当前操作对象为 Arm B。
- [x] 已连接 Arm B Web：`agx-7ax-armB` / `http://192.168.31.1/`。
- [x] 已运行 `bash scripts/s10_control_source_audit.sh` 并确认无 NERO 控制进程。
- [x] `can_arm_b` 为 UP、ERROR-ACTIVE、bitrate `1000000`。
- [x] Arm B J1 扫掠区域空旷。
- [ ] Arm A 未被命令。
- [x] Web 是唯一运动控制源。
- [x] Web 速度已设为最低可用值，优先 `5%` 或更低。
- [x] Arm B Web 使能成功。
- [x] Arm B J1 `+2 deg` 小角度运动成功。
- [x] Arm B J1 已回到原角度。
- [x] Web 停止后无主动运动命令。
- [x] Arm B Web 动作后 ROS 只读快照已保存：`docs/s9_ros_snapshots/20260625_072129/`。
- [x] 动作后 A/B `err_status: 0`，关节限位和通信异常均为 `false`。

## S10.6/S10.7 Arm B SDK/ROS 复刻

- [x] S10.5 Web 复刻已通过。
- [x] Arm B SDK J1 `+2 deg` dry-run 已通过且未运动。
- [x] SDK dry-run 后 ROS 只读快照已保存：`docs/s9_ros_snapshots/20260625_072742/`。
- [x] Arm B SDK J1 `+2 deg` 低速运动通过并回原角。
- [x] SDK 动作后 ROS 只读快照已保存且正常：`docs/s9_ros_snapshots/20260625_074048/`。
- [x] 已阅读 `docs/s10_7_arm_b_ros_motion_plan.md`。
- [x] 双臂只读 driver 已停止。
- [x] Arm B ROS control driver 已以 `auto_enable:=true control_enabled:=true speed_percent:=5` 启动。
- [x] Arm B ROS `joint1 +2 deg` dry-run 已通过且未运动。
- [x] Arm B ROS `joint1 +2 deg` 低速运动通过并回原角。
- [x] ROS 动作后 ROS 只读快照已保存且正常：`docs/s9_ros_snapshots/20260625_074953/`。

## S10.8 双臂首次运动收束

- [x] Arm B ROS control driver 已停止或确认未运行。
- [x] 已运行 `bash scripts/s10_control_source_audit.sh`。
- [x] 已确认无 Web/SDK/ROS motion 脚本运行。
- [x] 已记录下一阶段选择：S11 双臂实验基线与坐标闭环。

## S11 双臂实验基线与坐标闭环

- [x] 已定义 `lab_world` 坐标系。
- [x] 已验收 `lab_world -> arm_a/world`：`x=0, y=0, z=0, roll=0, pitch=-1.5707963, yaw=0`。
- [x] 已验收 `lab_world -> arm_b/world`：`x=0.260 m, y=0, z=0, roll=3.1415926, pitch=-1.5707963, yaw=0`。
- [x] 已记录测量方法、工具、误差估计和照片；工具/误差未定量报告，已作为 S11 第一工程基线限制记录。
- [x] 已建立并验证静态 TF 发布方案。
- [x] RViz 中双臂相对位置与实物一致，且分别移动两臂时 RViz 会跟随。
- [x] 成功版 RViz 截图已保存：`docs/pics/S11_RViz_accepted_dual_arm_layout.png`。
- [x] post-TF ROS 只读快照已通过：`docs/s9_ros_snapshots/20260626_055339/`。
- [x] 当前 TCP 定义已记录，裸臂阶段保持默认 TCP。
- [x] rosbag / snapshot / 实验日志命名规范已确定。

## S12 控制隔离与日志闭环

- [x] S12 控制隔离计划已建立：`docs/s12_control_isolation_plan.md`。
- [x] S12 目标动作已定义为可见 J1 `30 deg`，仍然单臂轮流执行。
- [x] Arm A `joint1 +30 deg` dry-run 目标正确。
- [x] Arm A `joint1 +30 deg` 执行时 Arm B 不动，最大被动偏差 `0.005 deg`。
- [x] Arm A `joint1 +30 deg` post-motion 双臂只读快照通过：`docs/s9_ros_snapshots/20260626_080809/`。
- [ ] Arm B `joint1 -30 deg` dry-run 目标正确。
- [ ] Arm B `joint1 -30 deg` 执行时 Arm A 不动。
- [ ] 同时启动两个控制 driver 时 namespace、CAN、日志互不混淆。
- [ ] 每次实验均记录命令、反馈、状态、rosbag、快照和 git commit。
- [ ] 异常停止和恢复记录格式已确定。

## S13 低风险双臂协同原语

- [ ] 双臂同时只读运行稳定。
- [ ] 双臂同时 enable / hold，无位移。
- [ ] A 小动、B 保持通过。
- [ ] B 小动、A 保持通过。
- [ ] A/B 同时小幅、互不接近 joint-space 动作通过。
- [ ] 未进入笛卡尔、MoveIt 或 manipulation primitive 之前已完成快照验收。

## S14 末端执行器

- [ ] 末端工具机械固定完成。
- [ ] 末端工具供电和通讯线无干涉。
- [ ] 夹爪/示教器/灵巧手类型与 Web/ROS 配置一致。
- [ ] 如使用旧 Piper 夹爪，已完成 ID 更改确认。
- [ ] 灵巧手安装前已复核 `docs/pics/4 灵巧手示意图.png` 和 `docs/pics/5 灵巧手法兰安装示意图.png`。
- [ ] 夹爪 `0x2A8` 或上层反馈正常。
- [ ] 低速小行程动作正常。
- [ ] 无过流、过温、传感器异常。

## S15 应用集成

- [ ] MoveIt 先规划不执行，轨迹可达且不越限。
- [ ] 应用节点有速度、加速度、限位保护。
- [ ] rosbag 或日志记录已配置。
- [ ] 异常状态会停止任务。
- [ ] 版本、启动命令、参数文件已归档。
- [ ] 连续运行验收时长达标。
