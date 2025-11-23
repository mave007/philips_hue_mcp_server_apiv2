# How to Identify Device Types in Philips Hue API v2

## Quick Answer

Device types are identified through **multiple fields** in the device resource:

1. **`product_data.product_archetype`** - Primary device category
2. **`metadata.archetype`** - User-assigned room context
3. **`product_data.model_id`** - Specific model identifier
4. **`product_data.product_name`** - Human-readable product name
5. **`services`** - What capabilities the device has

---

## Primary Method: Product Archetype

The **`product_data.product_archetype`** field tells you what type of device it is.

### Example Device Structure

```json
{
  "id": "device-uuid",
  "type": "device",
  "product_data": {
    "model_id": "LCA007",
    "manufacturer_name": "Signify Netherlands B.V.",
    "product_name": "Hue color lamp",
    "product_archetype": "sultan_bulb",  ← PRIMARY IDENTIFIER
    "certified": true,
    "software_version": "1.116.3"
  },
  "metadata": {
    "name": "Living Room Lamp",
    "archetype": "floor_lamp"  ← USER-ASSIGNED CONTEXT
  },
  "services": [
    {"rid": "...", "rtype": "light"},
    {"rid": "...", "rtype": "zigbee_connectivity"}
  ]
}
```

---

## Device Type Categories

### Lighting Devices

**Light Bulbs:**
- `sultan_bulb` - Standard A-shape bulb
- `classic_bulb` - Traditional bulb shape
- `candle_bulb` - Candle/flame shape
- `luster_bulb` - Small decorative bulb
- `spot_bulb` - Spotlight/flood bulb

**Light Fixtures:**
- `ceiling_round` - Round ceiling light
- `ceiling_square` - Square ceiling light
- `ceiling_horizontal` - Horizontal bar light
- `pendant_round` - Round pendant/hanging light
- `pendant_long` - Long pendant light

**Specialty Lights:**
- `huelightstrip` - LED light strip
- `huebloom` - Bloom accent light
- `huecentris` - Centris ceiling fixture
- `huego` - Portable Hue Go light
- `hueplay` - Play gradient/gaming light

**Lamps:**
- `floor_lamp` - Standing floor lamp
- `table_lamp` - Table/desk lamp
- `floor_shade` - Floor lamp with shade
- `table_shade` - Table lamp with shade

**Outdoor:**
- `bollard` - Bollard/post light
- `wall_lantern` - Wall-mounted lantern
- `garden_pole` - Garden pole light

### Control Devices

**Switches & Buttons:**
- `unknown_archetype` + button service - Smart button
- `wall_switch` - Wall switch module

**Dimmers:**
- `dimmer_switch` - Wireless dimmer

### Sensor Devices

**Motion Sensors:**
- `motion_sensor` - Motion detection device

### Other Devices

**Smart Plugs:**
- `plug` - Smart plug/outlet

**Bridge:**
- `bridge_v2` - Hue Bridge itself

---

## Identification Strategy

### Method 1: Check Product Archetype (Recommended)

```python
def identify_device_type(device):
    """
    Identify device type from product archetype.
    
    Args:
        device: Device resource object
        
    Returns:
        String describing device category
    """
    archetype = device.get("product_data", {}).get("product_archetype", "unknown")
    
    # Light bulbs
    if "bulb" in archetype:
        return "Light Bulb"
    
    # Light strips
    if "strip" in archetype:
        return "Light Strip"
    
    # Ceiling lights
    if "ceiling" in archetype:
        return "Ceiling Light"
    
    # Lamps
    if "lamp" in archetype or "shade" in archetype:
        return "Lamp"
    
    # Outdoor
    if archetype in ["bollard", "wall_lantern", "garden_pole"]:
        return "Outdoor Light"
    
    # Specialty
    if archetype in ["huebloom", "huego", "hueplay"]:
        return "Accent Light"
    
    # Controls
    if archetype == "plug":
        return "Smart Plug"
    
    if archetype == "bridge_v2":
        return "Bridge"
    
    # Check services if archetype unclear
    services = [s["rtype"] for s in device.get("services", [])]
    
    if "motion" in services:
        return "Motion Sensor"
    
    if "button" in services:
        return "Button/Switch"
    
    if "light" in services:
        return "Light Device"
    
    return "Unknown Device"
```

### Method 2: Check Services

Services tell you what the device can do:

```python
def get_device_capabilities(device):
    """
    List all capabilities of a device.
    
    Args:
        device: Device resource object
        
    Returns:
        List of capability strings
    """
    capabilities = []
    
    for service in device.get("services", []):
        service_type = service["rtype"]
        
        if service_type == "light":
            capabilities.append("Lighting")
        elif service_type == "motion":
            capabilities.append("Motion Detection")
        elif service_type == "temperature":
            capabilities.append("Temperature Sensing")
        elif service_type == "light_level":
            capabilities.append("Light Level Sensing")
        elif service_type == "button":
            capabilities.append("Button Control")
        elif service_type == "relative_rotary":
            capabilities.append("Rotary Dimmer")
        elif service_type == "contact":
            capabilities.append("Contact Sensing")
        elif service_type == "device_power":
            capabilities.append("Battery Status")
        elif service_type == "entertainment":
            capabilities.append("Entertainment/Sync")
    
    return capabilities
```

### Method 3: Check Model ID

For precise identification, use the model ID:

```python
# Common model IDs
MODEL_TYPES = {
    # Color bulbs
    "LCA001": "Hue Color Bulb E26/E27",
    "LCA007": "Hue Color Bulb E26/E27 1100lm",
    "LCT001": "Hue Color Bulb Gen 1",
    "LCT007": "Hue Color Bulb Gen 2",
    
    # White ambiance
    "LTW001": "Hue White Ambiance E26/E27",
    "LTW013": "Hue White Ambiance GU10",
    
    # White only
    "LWB004": "Hue White A60 E27 840lm",
    "LWB006": "Hue White A60 E27 800lm",
    "LWB014": "Hue White A19 E26 840lm",
    
    # Light strips
    "LST002": "Hue Lightstrip Plus 2m",
    "LCL008": "Hue Lightstrip Plus V4",
    
    # Specialty
    "LLC020": "Hue Go",
    "LCT011": "Hue BR30 Color",
    "LCT026": "Hue Go Portable",
    
    # Sensors
    "SML001": "Hue Motion Sensor",
    "SML002": "Hue Motion Sensor (outdoor)",
    
    # Controls
    "RWL021": "Hue Dimmer Switch",
    "ROM001": "Hue Smart Button",
    "LOM010": "Hue Smart Plug",
    
    # Bridge
    "BSB002": "Hue Bridge v2",
}

def identify_by_model(device):
    model_id = device.get("product_data", {}).get("model_id")
    return MODEL_TYPES.get(model_id, f"Unknown Model ({model_id})")
```

---

## Complete Device Analysis Function

```python
def analyze_device(device):
    """
    Complete device type analysis.
    
    Args:
        device: Device resource from API
        
    Returns:
        Dictionary with device classification
    """
    product_data = device.get("product_data", {})
    metadata = device.get("metadata", {})
    services = device.get("services", [])
    
    # Extract key fields
    model_id = product_data.get("model_id", "unknown")
    product_name = product_data.get("product_name", "Unknown Product")
    product_archetype = product_data.get("product_archetype", "unknown")
    user_archetype = metadata.get("archetype", "unknown")
    device_name = metadata.get("name", "Unnamed Device")
    
    # Service types
    service_types = [s["rtype"] for s in services]
    
    # Determine primary category
    if "light" in service_types:
        if "strip" in product_archetype:
            category = "Light Strip"
        elif "bulb" in product_archetype:
            category = "Light Bulb"
        elif "lamp" in product_archetype or "shade" in product_archetype:
            category = "Lamp"
        elif "ceiling" in product_archetype:
            category = "Ceiling Light"
        elif "plug" in product_archetype:
            category = "Smart Plug (with light)"
        else:
            category = "Light"
    elif "motion" in service_types:
        category = "Motion Sensor"
    elif "button" in service_types:
        category = "Button/Switch"
    elif "bridge" in service_types:
        category = "Bridge"
    else:
        category = "Unknown"
    
    # Determine light type capabilities
    light_capabilities = []
    if "light" in service_types:
        # Would need to check light resource for exact capabilities
        # But we can infer from product name
        if "color" in product_name.lower():
            light_capabilities = ["On/Off", "Brightness", "Color", "Color Temperature"]
        elif "ambiance" in product_name.lower() or "white" in product_name.lower():
            light_capabilities = ["On/Off", "Brightness", "Color Temperature"]
        else:
            light_capabilities = ["On/Off", "Brightness"]
    
    return {
        "name": device_name,
        "category": category,
        "product_name": product_name,
        "model_id": model_id,
        "product_archetype": product_archetype,
        "user_archetype": user_archetype,
        "services": service_types,
        "capabilities": light_capabilities,
        "is_light": "light" in service_types,
        "is_sensor": any(s in service_types for s in ["motion", "temperature", "light_level"]),
        "is_control": any(s in service_types for s in ["button", "relative_rotary"]),
    }
```

---

## Using in Your MCP Server

### Add Device Type Tool

```python
Tool(
    name="hue_identify_device_types",
    description="Identify and categorize all devices by type (lights, sensors, switches, etc)",
    inputSchema={
        "type": "object",
        "properties": {},
    },
)
```

### Implementation

```python
elif name == "hue_identify_device_types":
    """
    Categorize all devices by type.
    
    Returns:
        Dictionary with devices grouped by category
    """
    devices_result = make_request("GET", "/resource/device")
    
    categorized = {
        "light_bulbs": [],
        "light_strips": [],
        "lamps": [],
        "ceiling_lights": [],
        "outdoor_lights": [],
        "accent_lights": [],
        "smart_plugs": [],
        "motion_sensors": [],
        "buttons_switches": [],
        "bridge": [],
        "other": []
    }
    
    if "data" in devices_result:
        for device in devices_result["data"]:
            analysis = analyze_device(device)
            
            category_map = {
                "Light Bulb": "light_bulbs",
                "Light Strip": "light_strips",
                "Lamp": "lamps",
                "Ceiling Light": "ceiling_lights",
                "Outdoor Light": "outdoor_lights",
                "Accent Light": "accent_lights",
                "Smart Plug": "smart_plugs",
                "Motion Sensor": "motion_sensors",
                "Button/Switch": "buttons_switches",
                "Bridge": "bridge",
            }
            
            category_key = category_map.get(analysis["category"], "other")
            
            categorized[category_key].append({
                "id": device["id"],
                "name": analysis["name"],
                "model": analysis["model_id"],
                "product": analysis["product_name"],
                "services": analysis["services"]
            })
    
    return [TextContent(
        type="text",
        text=json.dumps(categorized, indent=2)
    )]
```

---

## Light Capability Detection

To determine what a light can do, check the light resource:

```python
def get_light_capabilities(light_resource):
    """
    Determine light capabilities from light resource.
    
    Args:
        light_resource: Light resource object
        
    Returns:
        Dictionary of capabilities
    """
    capabilities = {
        "on_off": "on" in light_resource,
        "dimmable": "dimming" in light_resource,
        "color_temperature": "color_temperature" in light_resource,
        "color": "color" in light_resource,
        "effects": "effects" in light_resource,
        "gradient": "gradient" in light_resource,
    }
    
    # Get ranges
    if capabilities["dimmable"]:
        capabilities["min_dim_level"] = light_resource["dimming"].get("min_dim_level", 0.2)
    
    if capabilities["color_temperature"]:
        ct_schema = light_resource["color_temperature"].get("mirek_schema", {})
        capabilities["ct_min"] = ct_schema.get("mirek_minimum", 153)
        capabilities["ct_max"] = ct_schema.get("mirek_maximum", 500)
    
    if capabilities["color"]:
        capabilities["color_gamut_type"] = light_resource.get("color", {}).get("gamut_type", "C")
    
    return capabilities
```

---

## Common Device Archetypes by Category

### Lights
```
Light Bulbs:
  - sultan_bulb (standard)
  - classic_bulb
  - candle_bulb
  - luster_bulb
  - spot_bulb

Ceiling:
  - ceiling_round
  - ceiling_square
  - ceiling_horizontal

Lamps:
  - floor_lamp
  - table_lamp
  - floor_shade
  - table_shade

Strips:
  - huelightstrip

Accent:
  - huebloom
  - huego
  - hueplay
```

### Sensors
```
Motion:
  - motion_sensor
  - (check services for "motion")

Multi-sensor:
  - Device with motion + temperature + light_level services
```

### Controls
```
Buttons:
  - (check services for "button")
  - Usually has "unknown_archetype"

Switches:
  - wall_switch
  - dimmer_switch
```

### Power
```
Plugs:
  - plug
```

---

## Summary

**Primary identification methods:**
1. ✅ **`product_archetype`** - Best for general category
2. ✅ **`services` array** - Best for capabilities
3. ✅ **`model_id`** - Best for exact product
4. ✅ **`product_name`** - Best for human display

**Recommended approach:**
```python
# 1. Check product_archetype for category
archetype = device["product_data"]["product_archetype"]

# 2. Check services for capabilities
services = [s["rtype"] for s in device["services"]]

# 3. Use model_id for precise identification
model = device["product_data"]["model_id"]

# 4. Display product_name to user
name = device["product_data"]["product_name"]
```

This multi-field approach ensures accurate device classification across all Hue products.
