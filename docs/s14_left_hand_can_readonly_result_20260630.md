# S14 Left LinkerHand L6 CAN Read-Only Result

Date: 2026-06-30

## Setup

- Hand: left LinkerHand L6.
- Hand connection: independent bench setup, disconnected from NERO arm/J6.
- Power: WANPTEK bench supply, previously observed at about `24.00 V` and
  `0.122 A`.
- CAN adapter: PEAK-System `XCAN-USB`.
- Driver: `peak_usb`.
- SocketCAN interface: `can1`.
- USB bus-info: `1-3.4.4:1.0`.
- CAN bitrate: `1000000`.
- CAN state after activation: `ERROR-ACTIVE`.

## Commands Run

```bash
sudo ip link set can1 up type can bitrate 1000000
ip -details link show can1
bash scripts/s14_linkerhand_l6_can_readonly_probe.sh can1 left
```

## Observed Result

The operator reported that the hand physically opened immediately after running
the probe command.

Although the original probe was intended as read-only, the live device behavior
means frame type `0x01` must be treated as motion-capable or motion-risk until
vendor documentation confirms otherwise. The project probe script has therefore
been revised to exclude `0x01` state query and `0x02` torque/status query from
the default identity/health-only probe.

## CAN Evidence

Raw capture showed expected left-hand arbitration ID `0x028`.

Serial-number response:

```text
028 [8] C0 00 4C 48 4C 36 2D 30
028 [8] C0 01 33 2D 32 35 33 2D
028 [8] C0 02 4C 2D 42 2D 31 2D
028 [3] C0 03 43
```

Decoded serial:

```text
LHL6-03-253-L-B-1-C
```

This matches the previously expected left-hand serial.

State response captured after `028#01`:

```text
028 [7] 01 0B 8E 00 00 00 00
```

Because physical opening occurred during the probe, this frame is not accepted
as a safe read-only command in the current process.

Temperature response:

```text
028 [7] 33 21 23 23 23 23 23
```

Interpreted as plausible raw Celsius-like values:

```text
[33, 35, 35, 35, 35, 35]
```

Fault response:

```text
028 [7] 35 00 00 00 00 00 00
```

Fault result:

```text
[0, 0, 0, 0, 0, 0]
```

Current response:

```text
028 [7] 36 2D 13 02 06 05 07
```

Raw current-like values:

```text
[45, 19, 2, 6, 5, 7]
```

Torque/status response after `028#02`:

```text
028 [7] 02 FF FF FF FF FF FF
```

This frame is also excluded from the default safe probe until the command
semantics are reviewed.

## Acceptance Judgment

Accepted:

- S14.5C CAN interface baseline passed:
  - `can1` exists;
  - driver is `peak_usb`;
  - bus-info is `1-3.4.4:1.0`;
  - interface is UP and `ERROR-ACTIVE` at `1000000`.
- Left-hand identity is confirmed by serial
  `LHL6-03-253-L-B-1-C`.
- Temperature values are plausible.
- Fault values are all zero.

Not accepted as read-only:

- The original probe's `0x01` state query caused or coincided with physical hand
  opening.
- Do not rerun the old probe revision.
- Do not run GUI, `test_hand.py`, `gestures.py`, SDK demos, or any motion
  command until S14.8C is replanned with this evidence.

## Next Gate

Immediate next step:

1. Do not send further commands.
2. Observe supply current, temperature, sound, and mechanical state.
3. If stable, capture a passive CAN log only:

```bash
timeout 5s candump -tz can1
```

4. After passive stability is recorded, rerun only the revised identity/health
   probe if needed.
5. Redesign first motion around the fact that `0x01` can move the hand.
