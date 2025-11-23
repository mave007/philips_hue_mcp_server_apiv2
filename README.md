# Philips Hue API v2 MCP Server

Model Context Protocol (MCP) server for controlling Philips Hue lights via API v2.

## Features

- **Full API v2 Support**: HTTPS with application key authentication
- **Resource-Based Architecture**: Access all bridge resources (lights, rooms, scenes, sensors)
- **Individual Light Control**: On/off, brightness, color temperature, XY color
- **Room/Zone Control**: Control multiple lights simultaneously
- **Scene Activation**: Apply saved lighting scenes
- **Device Discovery**: Auto-discover bridge on network
- **Configuration Management**: YAML-based configuration with setup wizard

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initial Authentication Setup

Run the interactive setup script to authenticate with your bridge:

```bash
python setup_hue_auth.py
```

**Process:**
1. Script discovers bridge IP (or you enter manually)
2. Press the physical link button on your bridge
3. Press Enter in the script
4. Application key is generated and saved to `hue_config.yaml`

**Security Note:** The link button press is required to ensure only authorized applications control your lights. This follows RFC 7235 authentication principles.

### 3. Run the MCP Server

```bash
python hue_mcp_server.py
```

Or add to Claude Desktop configuration:

```json
{
  "mcpServers": {
    "hue-api-v2": {
      "command": "python",
      "args": ["/path/to/hue_mcp_server.py"]
    }
  }
}
```

## Configuration

Configuration is stored in `hue_config.yaml`:

```yaml
bridge:
  ip: "192.168.1.4"                # Bridge IP address
  api_key: "oG4yy2VTHwIsr2GN5..."  # Application key (40 chars)
  
api:
  version: "v2"                    # API version
  base_path: "/clip/v2"            # API endpoint base
  use_https: true                  # Use HTTPS (required for v2)
  verify_ssl: false                # Bridge uses self-signed cert
  
timeouts:
  request: 10                      # Request timeout (seconds)
  connection: 5                    # Connection timeout (seconds)
```

## API Architecture

### Endpoints

API v2 uses resource-based endpoints via HTTPS:

```
Base URL: https://{bridge_ip}/clip/v2
Header:   hue-application-key: {api_key}
```

**Resource Structure:**
- `/resource` - All resources
- `/resource/{type}` - Resources of specific type
- `/resource/{type}/{id}` - Specific resource by UUID

**Common Operations:**
- `GET` - Retrieve resource(s)
- `PUT` - Update resource state
- `POST` - Create new resource
- `DELETE` - Remove resource

### Resource Types

**Core Resources:**
- `light` - Individual lights
- `scene` - Saved lighting scenes  
- `room` - Physical rooms
- `zone` - Custom light zones
- `grouped_light` - Group control endpoint
- `device` - Physical devices (bulbs, switches, sensors)
- `bridge` - Bridge information

**Sensors:**
- `motion` - Motion sensors
- `temperature` - Temperature sensors
- `light_level` - Ambient light sensors
- `contact` - Contact/door sensors

**Controls:**
- `button` - Button devices
- `relative_rotary` - Rotary/dimmer controls

**Entertainment:**
- `entertainment_configuration` - Entertainment areas for sync

## Available MCP Tools

### Setup Tools

#### `hue_setup_authentication`
Initial bridge authentication setup.

**Parameters:**
- `bridge_ip` (optional): Bridge IP, leave empty for auto-discovery
- `app_name` (optional): Application name (default: "hue-mcp-server")

**Process:**
1. Discovers bridge if IP not provided
2. Prompts to press link button
3. Generates application key
4. Saves to `hue_config.yaml`

**Example:**
```json
{
  "bridge_ip": "192.168.1.4",
  "app_name": "my-hue-app"
}
```

### Resource Access Tools

#### `hue_get_resources`
Get all resources or filter by type.

**Parameters:**
- `resource_type` (optional): Type to filter (light, scene, room, zone, etc)

**Returns:** `{"data": [...]}`

**Example:**
```json
{"resource_type": "light"}
```

#### `hue_get_resource_by_id`
Get specific resource by UUID.

**Parameters:**
- `resource_type` (required): Resource type
- `resource_id` (required): Resource UUID

**Returns:** `{"data": [{...}]}`

**Example:**
```json
{
  "resource_type": "light",
  "resource_id": "e706416a-8c92-46ef-8589-3453f3235b13"
}
```

### Light Control Tools

#### `hue_control_light`
Control individual light state.

**Parameters:**
- `light_id` (required): Light UUID
- `on` (optional): Turn on/off (boolean)
- `brightness` (optional): 0-100%
- `color_temperature` (optional): 153-500 mirek
- `color_xy` (optional): CIE xy coordinates `{"x": 0.3, "y": 0.3}`
- `transition_time` (optional): Duration in milliseconds

**Color Temperature Values:**
- 153 mirek = 6500K (cool white)
- 250 mirek = 4000K (neutral)
- 500 mirek = 2000K (warm white)

**Example:**
```json
{
  "light_id": "e706416a-8c92-46ef-8589-3453f3235b13",
  "on": true,
  "brightness": 75,
  "color_temperature": 300,
  "transition_time": 1000
}
```

**Color Example:**
```json
{
  "light_id": "e706416a-8c92-46ef-8589-3453f3235b13",
  "on": true,
  "color_xy": {"x": 0.3, "y": 0.6}
}
```

#### `hue_control_room`
Control all lights in room/zone.

**Parameters:**
- `room_id` (required): Room/zone UUID
- `on` (optional): Turn on/off
- `brightness` (optional): 0-100%
- `color_temperature` (optional): 153-500 mirek

**Process:**
1. Retrieves room's `grouped_light` service
2. Applies changes to all lights in group

**Example:**
```json
{
  "room_id": "3f4ac4e9-d67a-4dbd-8a16-5ea7e373f281",
  "on": true,
  "brightness": 50
}
```

#### `hue_activate_scene`
Activate saved scene.

**Parameters:**
- `scene_id` (required): Scene UUID

**Example:**
```json
{"scene_id": "9de116fc-5fd2-4b74-8414-0f30cb2cbe04"}
```

### Information Tools

#### `hue_list_lights_detailed`
Get comprehensive light information.

**Returns:** Array of lights with:
- `id` - Light UUID
- `name` - Device name
- `type` - Light type
- `on` - Current state
- `brightness` - Current brightness
- `color_temp_mirek` - Current color temperature
- `color_xy` - Current color coordinates
- `reachable` - Connection status
- `rooms` - Assigned rooms
- `model` - Product model

**Example:**
```json
{}
```

#### `hue_search_by_name`
Search resources by name.

**Parameters:**
- `name` (required): Search term (case-insensitive)
- `resource_type` (optional): Filter by type

**Returns:** Array of matching resources

**Example:**
```json
{
  "name": "living",
  "resource_type": "light"
}
```

## Testing

### Test Script

Run the bash test script to verify connectivity:

```bash
./test_hue_api.sh
```

Tests:
- Get all lights
- Get all rooms
- Get all scenes
- Get bridge info
- Get devices

### Manual Testing

```bash
# Get all lights
curl --insecure \
  -H "hue-application-key: YOUR_KEY" \
  https://192.168.1.4/clip/v2/resource/light

# Turn on a light
curl --insecure -X PUT \
  -H "hue-application-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"on":{"on":true},"dimming":{"brightness":75}}' \
  https://192.168.1.4/clip/v2/resource/light/LIGHT_ID
```

## API v2 Key Concepts

### Authentication

**Initial Setup:**
1. Press physical link button on bridge
2. POST to `https://{bridge_ip}/api` with device type
3. Receive application key (40-character hex string)
4. Use key in `hue-application-key` header for all requests

**Security:** Application key authenticates all API requests. Keep it secure.

### Resource Model

API v2 uses a resource-based model where:
- Everything is a resource with a UUID
- Resources have types and properties
- Resources can reference other resources
- Changes propagate through resource relationships

**Example Resource:**
```json
{
  "id": "e706416a-8c92-46ef-8589-3453f3235b13",
  "type": "light",
  "on": {"on": true},
  "dimming": {"brightness": 75.0},
  "color_temperature": {"mirek": 300},
  "owner": {
    "rid": "3f4ac4e9-d67a-4dbd-8a16-5ea7e373f281",
    "rtype": "device"
  }
}
```

### State Updates

**Payload Structure:**
```json
{
  "on": {"on": true},                        // Power state
  "dimming": {"brightness": 75.0},           // Brightness (0-100%)
  "color_temperature": {"mirek": 300},       // Color temp
  "color": {"xy": {"x": 0.3, "y": 0.3}},    // Color
  "dynamics": {"duration": 1000}             // Transition time (ms)
}
```

**Multiple Properties:** You can update multiple properties in one request.

### Room vs Grouped Light

- **Room**: Logical grouping with metadata and services
- **Grouped Light**: Control endpoint for lights in room/zone

**Access Pattern:**
1. Get room resource
2. Find `grouped_light` service in room's services array
3. Use grouped_light UUID for control operations

## Code Documentation

### Function Reference

**Configuration Functions:**
- `load_config()` - Load YAML configuration
- `save_config(config)` - Save YAML configuration
- `get_base_url()` - Construct API base URL

**Authentication Functions:**
- `discover_bridge()` - Auto-discover bridge IP
- `authenticate_bridge(ip, app_name)` - Generate application key

**API Functions:**
- `make_request(method, endpoint, data)` - Execute HTTP request with auth

### Error Handling

**Common Errors:**
- `101` - Link button not pressed
- `403` - Unauthorized (invalid application key)
- `404` - Resource not found
- `500` - Bridge error

**Connection Issues:**
- Verify bridge IP address
- Check network connectivity
- Ensure HTTPS is used (API v2 requirement)
- Bridge may need firmware update for API v2

## References

- [Philips Hue API v2 Documentation](https://developers.meethue.com/develop/hue-api-v2/)
- [API v2 Getting Started](https://developers.meethue.com/develop/hue-api-v2/getting-started/)
- [API v2 Core Concepts](https://developers.meethue.com/develop/hue-api-v2/core-concepts/)
- [RFC 7235 - HTTP Authentication](https://tools.ietf.org/html/rfc7235)
- [CIE 1931 Color Space](https://en.wikipedia.org/wiki/CIE_1931_color_space)

## Troubleshooting

**Bridge not discovered:**
- Ensure bridge is connected to network
- Bridge must have internet access initially
- Try manual IP entry

**Authentication fails:**
- Press link button immediately before authenticating
- Link button has 30-second timeout
- Only one authentication attempt per button press

**SSL certificate errors:**
- Bridge uses self-signed certificate
- `verify_ssl: false` is required in config
- This is normal and expected

**Light control not working:**
- Verify light UUID is correct
- Check light is reachable (not powered off)
- Ensure color/brightness values are in valid ranges
- Some properties only work on certain light types

## License

This project is licensed under CC BY-NC-SA 4.0 - see [LICENSE.md](LICENSE.md)

### Commercial Use
For commercial licensing inquiries, please contact: [mave at cero32 dot cl]

Commercial use includes:
- Using this in a paid product or service
- Offering this as part of a SaaS platform
- Including this in proprietary software
- Using this to generate revenue
