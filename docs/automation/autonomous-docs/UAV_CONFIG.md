# 無人機編隊配置

## 編隊角色

| 角色 | 功能 |
|------|------|
| Leader | 任務規劃、路徑廣播 |
| Relay | 通訊中繼、訊號增益 |
| Sensor | 高解析感測器載具 |
| Responder | 緊急處置、收容 |

## 配置樣板

```yaml
fleet:
  mission_id: uav-ops-001
  leader:
    id: drone-a1
    autopilot: auto_pilot_v2
  members:
    - id: drone-b1
      role: relay
    - id: drone-c1
      role: sensor
    - id: drone-d1
      role: responder
network:
  mesh: synergymesh
  telemetry: island-link
safety:
  geofence: enabled
  max_wind: 25kmh
  fallback_mode: hover
```

## 操作

```bash
# 發佈任務
python automation/drone-coordinator.py --mission plan.yaml

# 在线監控
npm run drones:dash
```
