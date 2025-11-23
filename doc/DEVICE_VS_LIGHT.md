# Understanding Device vs Light Resources in Hue API v2

## Quick Answer

**`/resource/device`** and **`/resource/light`** are **DIFFERENT resources** with **DIFFERENT IDs**.

- **Device** = The physical hardware (bulb, switch, sensor, etc.)
- **Light** = The lighting capability of that device

**One device can contain multiple services** (light, button, motion sensor, etc.)

---

## Detailed Explanation

### Device Resource (`/resource/device`)

**What it is:**
- Represents the **physical hardware** connected to your Hue Bridge
- Contains metadata about the product (name, model, manufacturer)
- Lists all **services** provided by this physical device

**What it contains:**
```json
{
  "id": "3f4ac4e9-d67a-4dbd-8a16-5ea7e373f281",  // Device UUID
  "type": "device",
  "metadata": {
    "name": "Living Room Lamp",
    "archetype": "floor_lamp"
  },
  "product_data": {
    "model_id": "LCA007",
    "manufacturer_name": "Signify Netherlands B.V.",
    "product_name": "Hue color lamp",
    "product_archetype": "floor_lamp"
  },
  "services": [
    {
      "rid": "e706416a-8c92-46ef-8589-3453f3235b13",  // Light service ID
      "rtype": "light"
    },
    {
      "rid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",  // Zigbee connectivity
      "rtype": "zigbee_connectivity"
    },
    {
      "rid": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",  // Device power
      "rtype": "device_power"
    }
  ]
}
```

### Light Resource (`/resource/light`)

**What it is:**
- Represents the **lighting capability** of a device
- Contains the **controllable state** (on/off, brightness, color)
- Is a **service** provided by a device

**What it contains:**
```json
{
  "id": "e706416a-8c92-46ef-8589-3453f3235b13",  // Light UUID (different from device!)
  "type": "light",
  "owner": {
    "rid": "3f4ac4e9-d67a-4dbd-8a16-5ea7e373f281",  // Points to device ID
    "rtype": "device"
  },
  "on": {
    "on": true
  },
  "dimming": {
    "brightness": 75.0,
    "min_dim_level": 0.2
  },
  "color_temperature": {
    "mirek": 300,
    "mirek_valid": true,
    "mirek_schema": {
      "mirek_minimum": 153,
      "mirek_maximum": 500
    }
  },
  "color": {
    "xy": {
      "x": 0.3,
      "y": 0.3
    }
  }
}
```

---

## Key Relationship: Owner Pattern

```
┌──────────────────────────────────┐
│         DEVICE                   │  ID: 3f4ac4e9-...
│  (Physical bulb/hardware)        │
│                                  │
│  services: [                     │
│    { rid: e706416a-..., ←────────┼──┐
│      rtype: "light" }            │  │
│    { rid: a1b2c3d4-...,          │  │
│      rtype: "zigbee" }           │  │
│  ]                               │  │
└──────────────────────────────────┘  │
                                      │
                                      │ References
                                      │
┌──────────────────────────────────┐  │
│         LIGHT                    │  │  ID: e706416a-...
│  (Lighting capability)           │  │
│                                  │  │
│  owner: {                        │  │
│    rid: 3f4ac4e9-..., ───────────┼──┘ Points back to device
│    rtype: "device"               │
│  }                               │
│                                  │
│  on: { on: true }                │
│  dimming: { brightness: 75 }     │
│  color_temperature: {...}        │
└──────────────────────────────────┘
```

---

## Examples from Your System

Based on your lights.json (API v1 data), here's how it maps to v2:

### Example 1: Single Bulb

**API v1:**
```json
{
  "2": {
    "name": "Office 2 color bulb",
    "modelid": "LCT001",
    "state": {
      "on": true,
      "bri": 254
    }
  }
}
```

**API v2:**
```
Device:
  id: device-uuid-xxx
  name: "Office 2 color bulb"
  services: [
    {rid: light-uuid-yyy, rtype: "light"}
  ]

Light:
  id: light-uuid-yyy
  owner: {rid: device-uuid-xxx, rtype: "device"}
  on: {on: true}
  dimming: {brightness: 100}
```

### Example 2: Motion Sensor (Multiple Services)

A motion sensor device provides **multiple services**:

```
Device:
  id: sensor-device-uuid
  name: "Hallway Motion Sensor"
  services: [
    {rid: motion-uuid,      rtype: "motion"},
    {rid: temperature-uuid, rtype: "temperature"},
    {rid: light-level-uuid, rtype: "light_level"},
    {rid: battery-uuid,     rtype: "device_power"}
  ]

Motion Service:
  id: motion-uuid
  owner: {rid: sensor-device-uuid}
  motion: {motion: false}

Temperature Service:
  id: temperature-uuid
  owner: {rid: sensor-device-uuid}
  temperature: {celsius: 22.5}
```

---

## Why Two Separate Resources?

### Design Philosophy

**API v2 uses a service-oriented architecture:**

1. **Physical devices** are represented once
2. **Capabilities** are represented as separate services
3. This allows devices with **multiple functions**

### Benefits

**Flexibility:**
- One device can provide multiple services
- Services can be controlled independently
- Clear separation of concerns

**Example - Hue Play HDMI Sync Box:**
```
Device: Sync Box
Services:
  - entertainment (sync control)
  - hdmi_input (input selection)
  - light (status LED)
```

**Consistency:**
- All controllable things are resources
- All resources follow same pattern
- Uniform API structure

---

## How to Navigate the Relationship

### Finding Light from Device

```python
# 1. Get device
device = get_resource("device", device_id)

# 2. Find light service
light_id = None
for service in device["services"]:
    if service["rtype"] == "light":
        light_id = service["rid"]
        break

# 3. Get/control light
light = get_resource("light", light_id)
```

### Finding Device from Light

```python
# 1. Get light
light = get_resource("light", light_id)

# 2. Get device from owner
device_id = light["owner"]["rid"]
device = get_resource("device", device_id)
```

### Implementation in Your MCP Server

```python
# In hue_list_lights_detailed():

# Get all lights
lights = make_request("GET", "/resource/light")

# Get all devices to map names
devices = make_request("GET", "/resource/device")

# Build mapping
device_map = {}
for device in devices["data"]:
    device_map[device["id"]] = device

# For each light, find its device
for light in lights["data"]:
    device_id = light["owner"]["rid"]
    device = device_map.get(device_id)
    
    # Device has the name!
    name = device["metadata"]["name"]
    model = device["product_data"]["product_name"]
```

---

## Common Patterns

### Pattern 1: Control Light by Name

```
1. Search devices by name
2. Find light service in device
3. Control light using service UUID
```

### Pattern 2: List All Capabilities

```
1. Get device
2. Loop through services
3. Get each service resource
4. Display capabilities
```

### Pattern 3: Room Assignment

Rooms reference **devices**, not lights:

```json
{
  "type": "room",
  "services": [
    {"rid": "device-uuid-1", "rtype": "device"},
    {"rid": "device-uuid-2", "rtype": "device"}
  ]
}
```

To control room lights:
1. Room → device IDs
2. Device → light service IDs
3. Or use room's `grouped_light` service directly

---

## Comparison Table

| Aspect | Device | Light |
|--------|--------|-------|
| **Represents** | Physical hardware | Lighting capability |
| **ID Type** | Device UUID | Light UUID |
| **Contains** | Metadata, services list | State, color, brightness |
| **Name stored in** | Device metadata | (Name comes from device) |
| **Controllable** | No | Yes (PUT to change state) |
| **Services** | Lists what it provides | Is itself a service |
| **Owner** | No owner | Points to device |

---

## API v1 vs v2 Comparison

### API v1 (Legacy)
```
GET /api/{username}/lights
{
  "1": {
    "name": "Living Room",
    "state": {...}
  }
}
```
- Light number = Device identifier
- Name stored in light
- Flat structure

### API v2 (Current)
```
GET /clip/v2/resource/device  → Get devices with names
GET /clip/v2/resource/light   → Get lights with state
```
- Separate resources with UUIDs
- Name in device, state in light
- Service-oriented structure

---

## Practical Examples

### Get Light Name
```python
# ✗ WRONG - light doesn't have name
light = get("/resource/light/light-uuid")
name = light["metadata"]["name"]  # KeyError!

# ✓ CORRECT - get name from device
light = get("/resource/light/light-uuid")
device_id = light["owner"]["rid"]
device = get(f"/resource/device/{device_id}")
name = device["metadata"]["name"]
```

### Control Light
```python
# ✓ Use light UUID for control
put("/resource/light/light-uuid", {
    "on": {"on": true},
    "dimming": {"brightness": 75}
})
```

### List All Lights with Names
```python
# This is what hue_list_lights_detailed() does:
devices = get("/resource/device")
lights = get("/resource/light")

# Map device IDs to names
device_names = {}
for d in devices["data"]:
    device_names[d["id"]] = d["metadata"]["name"]

# Combine
for light in lights["data"]:
    device_id = light["owner"]["rid"]
    print(f"{device_names[device_id]}: {light['on']['on']}")
```

---

## Summary

✅ **Device ID ≠ Light ID** (always different UUIDs)  
✅ **Device** = physical hardware with metadata  
✅ **Light** = controllable lighting capability  
✅ **Relationship**: Device owns Light (via services)  
✅ **Light name** comes from owning device  
✅ **Control operations** use light UUID  
✅ **One device** can have multiple services  

This service-oriented architecture provides flexibility for complex devices like motion sensors, switches, and entertainment areas that provide multiple capabilities beyond just lighting.
