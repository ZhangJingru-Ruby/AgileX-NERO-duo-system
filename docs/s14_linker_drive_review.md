# S14 Linker Drive Document Review

Date: 2026-06-30

Source:

- Google Drive folder:
  `https://drive.google.com/drive/folders/1bDQFkxWZW1SapAQazwENOSOL_vWyM9Ti`
- Local review cache:
  `docs/vendor/linker_drive_20260630/`
- The local cache is intentionally ignored by git because it contains raw PDFs,
  zip archives, extracted SDK trees, generated text, and binary libraries. To
  reproduce this review, download the Drive folder again into that path, extract
  the three zip archives, and run `pdftotext -layout` on the PDFs.

## Download Manifest

All eight Drive files were downloaded and validated locally on 2026-06-30.

| Local raw file | SHA256 |
| --- | --- |
| `Linker_Hand_L6_product_manual_20260402.pdf` | `e058fad2391862882df03fafd656c8b2036131127e88c3c0a18141c036160e6d` |
| `Linker_TA_LTA1-02_product_manual_20260402-1.pdf` | `c9ad57ce9ec95f1f6ec5ebeeff541cf6f4415913ce1c4358329e1fed3da36644` |
| `Linker_FFG_FFG1-01_product_manual_20260123-1.pdf` | `3bd515947543def00d63b0d4e5b8a02f882d961693388c5b736754b05ef172da` |
| `Teleop-gloves_1.zip` | `fb2fd95d4c72387a29348704d71308f98dbe23cfb4f78a2289d5f1931bd0ce78` |
| `linkerta_v2_1.0.3.zip` | `eca6146317a59dfd42da8f641560a9da9f629d6d7b7378b9fe349f9f2ce94cfb` |
| `api_lk73_v1.0.4_1.zip` | `dac25ebba2652d22a439facd304b7a04a69cfd0af95a95859f7e2ddc0874b38a` |
| `robot_arm_control_interface_v1.0.1_1.pdf` | `bffd5a01ee8caf53ec7140bd260dbd2d4a81f4c5487afde7b93887fd2564b198` |
| `linker_robot_control_platform_v1.0.1_1.pdf` | `771f19c997c9f9fdccb56771670fe6e21ac00a02b484a11f2ed3e90509c574fa` |

Zip validation:

- `api_lk73_v1.0.4_1.zip`: valid; extracted to
  `docs/vendor/linker_drive_20260630/extracted/api_lk73_v1.0.4/`.
- `linkerta_v2_1.0.3.zip`: valid; extracted to
  `docs/vendor/linker_drive_20260630/extracted/linkerta_v2_1.0.3/`.
- `Teleop-gloves_1.zip`: valid; extracted to
  `docs/vendor/linker_drive_20260630/extracted/Teleop-gloves/`.

## What Each Package Is

| Package | Role for our NERO deployment |
| --- | --- |
| `Linker Hand L6 产品手册` | Primary product manual for the installed LinkerHand L6 dexterous hands. |
| `api_lk73_v1.0.4` | Linker/LBOT robot controller SDK. It controls a dual-arm robot through a TCP controller, not through ROS topics or raw NERO SocketCAN directly. |
| `灵心巧手机器人控制平台v1.0.1` and bundled `机器人控制平台说明文档v1.1.0` | Web control platform documentation for the Linker/LBOT controller stack. |
| `机械臂控制接口文档v1.0.1` and bundled `机械臂控制接口文档v1.0.4` | API and network architecture documentation for the Linker/LBOT dual-arm controller. |
| `Teleop-gloves` | Teleoperation glove package. It also contains a newer LinkerHand Python SDK tree. Useful as direct hand protocol evidence. |
| `linkerta_v2_1.0.3` | Linker TA teleoperation arm ROS2 package. Not the immediate NERO hand control path. |
| `Linker TA` / `Linker FFG` manuals | Product references for teleoperation arm and glove hardware. Not immediate blockers for NERO hand bring-up. |

## L6 Hand Facts

From `Linker Hand L6 产品手册`:

- Model: `Linker hand L6`.
- Mechanical structure: `6` active joints plus `5` passive joints.
- Control interface: `CAN/RS485`.
- Working voltage: `DC24V +/- 10%`.
- Static current: `0.2 A`.
- Average no-load motion current: `0.75 A`.
- Maximum current: `1.4 A`.
- The manual lists an `XT30(2+2)` cable and a `USB 转 CAN 调试线` in the
  installation/debug accessory set.

Deployment impact:

- NERO J6 accessory power was previously documented as `24 V / 2 A MAX`; L6
  maximum current `1.4 A` is within that power budget on paper.
- Power capacity alone does not prove protocol compatibility. The decisive
  question is whether the NERO J6 path exposes Linker L6 CAN/RS485 protocol, an
  AgileX/Revo2 bridge, or a separate Linker/LBOT controller stack.

## Direct LinkerHand Python SDK Evidence

The `Teleop-gloves` zip contains:

`docs/vendor/linker_drive_20260630/extracted/Teleop-gloves/linkerhand-python-sdk-main/`

Important source facts:

- `LinkerHand/linker_hand_api.py` maps right hand to CAN ID `0x27` and left
  hand to CAN ID `0x28`.
- `LinkerHand/core/can/linker_hand_l6_can.py` sends and receives standard CAN
  frames using the hand CAN ID as the arbitration ID.
- For L6, frame byte `0x01` is position/status, `0x02` is torque limit,
  `0x05` is speed, `0x33` is temperature, `0x35` is fault code, `0x36` is
  current, `0x64` / `0xC2` are version queries, and `0xC0` is serial number.
- L6 `finger_move`, speed, and torque values are lists of length `6`, each
  value in `0..255`.
- The default config file describes direct SocketCAN or RS485 use, for example
  `CAN: "can0"` and `MODBUS: "None"`.

Deployment impact:

- This confirms that the installed hand model is not naturally an AgileX Revo2
  device. Treating it as `revo2` is at best a compatibility bridge, not the
  native hand protocol.
- Because the installed hands are currently connected through NERO J6 rather
  than a direct PCAN/USB-CAN adapter, these direct-CAN scripts should not be run
  on `can_arm_a` or `can_arm_b` without a separate bus review.

## Linker/LBOT Controller SDK Evidence

The `api_lk73_v1.0.4` package is the most important new evidence.

From `机械臂控制接口文档v1.0.4` and the Python/C SDK:

- The architecture assumes a Raspberry Pi or similar intermediate controller.
- The dual arms connect to that controller through USB-CAN modules.
- The controller forwards control commands.
- Default controller IP: `192.168.10.21`.
- User-side computer should be on `192.168.10.x`, for example
  `192.168.10.100`.
- Browser platform URL: `http://192.168.10.21:8000`.
- The SDK initializes with a TCP host, e.g. `LbotRobot("192.168.10.21")` or
  `lbot_init("192.168.10.21")`.
- The SDK exposes L6 hand APIs:
  - `lbot_l6_set_position(handle, arm, uint8_t[6])`;
  - `lbot_l6_set_velocity(handle, arm, uint8_t[6])`;
  - `lbot_l6_set_effort(handle, arm, uint8_t[6])`.
- The Python binding exposes the same functions through `LbotRobot.l6_set_*`.
- Controller state monitoring is documented at about `50 Hz`; joint-follow is
  documented as `50..200 Hz`.

Deployment impact:

- These documents describe a complete controller stack that can control both
  arms and L6 hands through one TCP API.
- This is not the same as our current accepted NERO control path, where the
  Ubuntu host talks directly to two official USB-CAN adapters as
  `can_arm_a` / `can_arm_b` and the NERO Web UI is at
  `http://192.168.31.1/#/welcome`.
- Therefore the new SDK is useful, but only if our physical robot also exposes
  the Linker/LBOT controller at `192.168.10.21` or an equivalent address.

## Unsafe Demo Files

Do not run the vendor demos directly during S14:

- `Demo/demo_python/demo_hand.py` can send large L6/L10 hand position commands,
  including `[200] * 6`, `[255] * 6`, and full open/close examples.
- `Demo/demo_python/demo_setting.py` calls zero setting, enable/disable, e-stop,
  clear error, and joint-limit modification APIs.
- Motion examples in `demo_move.py` issue arm movement commands.

If the LBOT controller is reachable, write a minimal read-only probe first. Do
not reuse the demo scripts as-is.

## Corrected S14 Interpretation

The new documents materially change the S14 diagnosis:

- The installed hands should be treated as LinkerHand L6 devices.
- The current NERO Web hand page shows `revo2`, but the new L6 documents do not
  identify Revo2 as the native LinkerHand L6 control protocol.
- The absence of Revo2 `0x1B*` / `0x1C*` frames in the first external
  `can_arm_a` sample is still useful, but Revo2 is no longer the only expected
  protocol.
- The highest-value next diagnostic is now to determine whether this machine
  has the Linker/LBOT controller path described by the new documents.

## Recommended Next Gate

Replace the immediate Revo2-first diagnosis with `S14.3K Linker/LBOT read-only
controller probe`.

Read-only network checks, while connected to the relevant robot network:

```bash
ip -br addr
ping -c 2 192.168.10.21
curl -I --max-time 3 http://192.168.10.21:8000
```

Acceptance:

- `192.168.10.21` is reachable, and `http://192.168.10.21:8000` responds; or
- the controller is unreachable and this fact is recorded, meaning the new
  LBOT SDK probably describes a controller stack not present on the current
  NERO installation.

If the controller is reachable:

1. Write and run a custom read-only Python probe that imports `LbotRobot`,
   connects to `192.168.10.21`, prints API version, prints controller info, and
   reads current state.
2. Do not call `l6_set_position`, `l6_set_velocity`, `l6_set_effort`,
   `move_*`, `set_zero`, `enable_arm`, `emergency_stop`, `clear_errors`, or
   `set_joint_limit`.
3. Only after read-only controller identity and state are accepted should we
   design a very small L6 hand motion gate.

If the controller is not reachable:

1. Keep the existing NERO arm control path unchanged.
2. Treat `api_lk73_v1.0.4` as vendor evidence for a different or additional
   controller stack.
3. Ask the vendor whether AgileX NERO firmware supports LinkerHand L6 through
   J6, whether a Linker/LBOT controller is required, and which Web/firmware
   option should be selected for L6.
4. Only then continue Revo2-frame filtering or J6 power/communication checks.

No finger motion is authorized by this review.

## 2026-06-30 Photo Evidence: Hand Connection Kit

Operator-provided photos:

- `docs/pics/灵巧手连接设备/灵巧手连接设备01.jpeg`
- `docs/pics/灵巧手连接设备/灵巧手连接设备02.jpeg`
- `docs/pics/灵巧手连接设备/灵巧手连接设备03.jpeg`

Visible hardware:

- A WANPTEK bench DC power supply.
- Two blue USB modules with screw terminals.
- The USB module terminal silk screen includes `120R`, `GND`, `CANL`, and
  `CANH`.
- Yellow/green signal wires are connected at the CAN terminal side.
- Red/black power leads and hand-side plug harnesses are visible.
- No Ethernet/RJ45 port, router, Raspberry Pi, or other network controller is
  visible in these photos.

Interpretation:

- This photo set matches the LinkerHand direct bench-test/debug topology:
  independent `24 V` power plus USB-CAN communication.
- It does not match the `api_lk73_v1.0.4` Linker/LBOT network-controller
  topology at `192.168.10.21`.
- Therefore the failed `ping 192.168.10.21` and
  `curl http://192.168.10.21:8000` result is consistent with the observed
  equipment: no Linker/LBOT network controller is currently evident.

Deployment decision:

- Do not reconnect the installed hands just because this kit exists.
- The current installed robot state remains NERO J6-integrated.
- This kit is useful if we intentionally switch one hand into a bench-test
  setup, but that is a different wiring topology and should be treated as a
  separate S14 branch.

If bench-test becomes necessary, the first accepted form should be one hand at a
time, with the robot hand cable disconnected from NERO J6, bench supply set to
manual-confirmed `24 V`, polarity and XT30(2+2) pinout verified against the L6
manual, one USB-CAN adapter connected to the hand CAN pair at `1 Mbps`, and only
read-only LinkerHand identity/status checks run before any finger motion.

Additional wiring risk from `灵巧手连接设备03.jpeg`:

- A red/orange conductor with exposed stranded/shield-like metal is visible near
  the bench supply and loose harness area.
- The photo does not prove whether this is V+, GND, shield/drain, or an unused
  conductor.
- Treat it as an unsafe live conductor until proven otherwise.
- The bench-test kit must not be energized or connected to a hand while any
  conductor remains bare, frayed, unidentified, or able to touch the power
  binding posts, CAN terminals, chassis, or another wire.

Bench-test wiring repair requirements:

1. Power supply unplugged and output disabled.
2. Identify every conductor by continuity test, not by color alone.
3. Map the harness to the L6 manual XT30(2+2) pinout: V+, GND, CAN_H, CAN_L.
4. Confirm no short between V+/GND, CAN_H/CAN_L, CAN to V+, or CAN to GND.
5. If the exposed conductor is shield/drain and the manual does not require a
   termination point, insulate it individually with heat-shrink or equivalent.
6. If the conductor is functional, terminate it with a proper crimp/ferrule or
   connector; no loose strands are acceptable in screw terminals.
7. Add strain relief so hand/cable motion cannot pull bare wire back out.
8. Verify polarity at the hand-side plug with the hand disconnected before any
   hand is powered.

## 2026-06-30 Wiring Decision

There are two valid-looking but mutually exclusive topologies. They must not be
mixed.

### A. Current Installed NERO J6 Topology

Use this topology when the hand remains mechanically installed on the NERO arm
and connected through the J6 end-effector cable.

Document facts:

- NERO manual section `2.1.2` defines the J6 end connector as XT30(2+2), `24 V`,
  `2 A MAX`.
- With the saved NERO drawing orientation, side key on the left:
  - large upper contact: power `+`;
  - large lower contact: power `-`;
  - lower small left contact: CAN `H`;
  - lower small right contact: CAN `L`.
- The same manual warns that the J6 end CAN is only adapted for AgileX/松灵 own
  devices and must not be privately connected to other CAN devices.

Wiring action:

- Keep only the supplied NERO end-effector power/communication cable between J6
  and the installed hand.
- Do not connect the WANPTEK bench supply, blue USB-CAN adapter, or LinkerHand
  direct-CAN harness to the same hand while this J6 cable is connected.
- Do not splice an external USB-CAN adapter into J6. If LinkerHand L6 is not
  working through J6, request vendor confirmation for the correct NERO firmware,
  Web option, and J6 compatibility path before rewiring.

### B. LinkerHand Direct Bench-Test Topology

Use this topology only if we deliberately remove one hand from the NERO J6 path
for isolated LinkerHand debugging.

Document facts:

- The L6 manual section `4.3` defines the hand connector as XT30(2+2).
- In the L6 manual drawing orientation:
  - power contacts: `VCC` and `GND`;
  - small upper contact: `CAN_L`;
  - small lower contact: `CAN_H`.
- L6 electrical limits in the manual: `DC24V +/- 10%`, static current `0.2 A`,
  average no-load current `0.75 A`, maximum current `1.4 A`.
- The photo set shows a WANPTEK bench DC supply plus blue USB-CAN adapters with
  screw-terminal labels `120R`, `GND`, `CANL`, `CANH`.

Bench-test wiring map:

| LinkerHand L6 side | Connect to | Requirement |
| --- | --- | --- |
| `VCC` | WANPTEK positive output | Set and verify `24 V` before connecting the hand. |
| `GND` | WANPTEK negative output | Confirm polarity at the hand-side connector first. |
| `CAN_H` | blue USB-CAN `CANH` | Verify by terminal label and continuity, not wire color. |
| `CAN_L` | blue USB-CAN `CANL` | Verify by terminal label and continuity, not wire color. |
| shield/drain or exposed conductor | no connection unless identified and required | Insulate individually or terminate per vendor guidance. |
| blue USB-CAN `120R` | no signal wire | Treat as termination feature, not CAN_H/CAN_L/GND. |
| blue USB-CAN `GND` | CAN reference only if the original harness/vendor confirms it | Do not improvise a ground bridge. |

Bench-test gate:

1. Disconnect the selected hand from NERO J6.
2. Use one hand, one bench supply, and one USB-CAN adapter at first.
3. Repair the exposed conductor seen in `灵巧手连接设备03.jpeg`.
4. With power off, use a multimeter to verify conductor identity and absence of
   shorts.
5. Set the bench supply to `24 V` with a conservative current limit for the first
   read-only identity/status check; increase only within the L6 manual current
   limits if motion is later authorized.
6. Run only read-only LinkerHand identity/status checks first. No vendor motion
   demo is authorized at this gate.
