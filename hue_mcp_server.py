#!/usr/bin/env python3
"""
Philips Hue API v2 MCP Server
Provides tools to interact with Philips Hue Bridge API v2

This server implements the Philips Hue API v2 specification which uses:
- HTTPS with self-signed certificates
- Application key in request headers (not URL)
- Resource-based architecture via /clip/v2 endpoints
- UUID-based resource identification

For more information see:
- https://developers.meethue.com/develop/hue-api-v2/getting-started/
- https://developers.meethue.com/develop/hue-api-v2/core-concepts/
"""

import json
import urllib3
import yaml
import sys
from pathlib import Path
from typing import Any, Optional, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
import httpx

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration file path
CONFIG_FILE = Path(__file__).parent / "hue_config.yaml"

# Global configuration storage
config: Dict[str, Any] = {}

# MCP Server
app = Server("hue-api-v2")

def load_config() -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Returns:
        Dict containing bridge configuration with keys:
        - ip: Bridge IP address
        - api_key: Application key for authentication (if configured)
        - use_https: Whether to use HTTPS (default: True)
        - verify_ssl: Whether to verify SSL certificates (default: False)
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    if not CONFIG_FILE.exists():
        # Create default config if it doesn't exist
        default_config = {
            'bridge': {
                'ip': '',
                'api_key': ''
            },
            'api': {
                'version': 'v2',
                'base_path': '/clip/v2',
                'use_https': True,
                'verify_ssl': False
            },
            'timeouts': {
                'request': 10,
                'connection': 5
            }
        }
        
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"Created default config at {CONFIG_FILE}")
        print("Please configure bridge IP and run authentication setup.")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)


def save_config(config_data: Dict[str, Any]) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config_data: Configuration dictionary to save
        
    Returns:
        None
    """
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)
    
    print(f"Configuration saved to {CONFIG_FILE}")


def authenticate_bridge(bridge_ip: str, app_name: str = "hue-mcp-server") -> Optional[Dict[str, str]]:
    """
    Authenticate with Hue Bridge to generate application key.
    
    This function requires the physical link button on the bridge to be pressed
    within 30 seconds of calling this function. This is a security measure to
    ensure only authorized applications can control the lights.
    
    API Endpoint: POST https://{bridge_ip}/api
    Payload: {"devicetype": "app_name#instance_name", "generateclientkey": true}
    
    Args:
        bridge_ip: IP address of the Hue Bridge
        app_name: Name of the application (default: "hue-mcp-server")
    
    Returns:
        Dictionary with 'username' (application key) and 'clientkey' if successful
        None if authentication failed
        
    Response format:
        Success: [{"success": {"username": "...", "clientkey": "..."}}]
        Error: [{"error": {"type": 101, "address": "", "description": "link button not pressed"}}]
    """
    url = f"https://{bridge_ip}/api"
    
    payload = {
        "devicetype": f"{app_name}#mcp-instance",
        "generateclientkey": True
    }
    
    try:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Check if successful
            if isinstance(result, list) and len(result) > 0:
                if "success" in result[0]:
                    return result[0]["success"]
                elif "error" in result[0]:
                    error = result[0]["error"]
                    print(f"Error: {error.get('description', 'Unknown error')}")
                    if error.get("type") == 101:
                        print("\nPlease press the link button on your Hue Bridge and try again.")
                    return None
            
            return None
            
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return None


def discover_bridge() -> Optional[str]:
    """
    Discover Hue Bridge IP address using Philips discovery service.
    
    Uses the official Philips Hue discovery endpoint which maintains
    a list of bridges that have connected to the Hue cloud service.
    
    API Endpoint: GET https://discovery.meethue.com/
    
    Returns:
        IP address of the first discovered bridge, or None if not found
        
    Response format:
        [{"id": "...", "internalipaddress": "192.168.1.4", ...}]
    """
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://discovery.meethue.com/")
            response.raise_for_status()
            bridges = response.json()
            
            if bridges and len(bridges) > 0:
                return bridges[0]["internalipaddress"]
            
            return None
            
    except Exception as e:
        print(f"Bridge discovery failed: {str(e)}")
        return None


def get_base_url() -> str:
    """
    Construct base URL for API requests from configuration.
    
    Returns:
        Full base URL including protocol, IP, and base path
        Example: "https://192.168.1.4/clip/v2"
    """
    protocol = "https" if config['api']['use_https'] else "http"
    ip = config['bridge']['ip']
    base_path = config['api']['base_path']
    return f"{protocol}://{ip}{base_path}"


def make_request(
    method: str,
    endpoint: str,
    data: Optional[dict] = None
) -> dict:
    """
    Make authenticated HTTPS request to Hue Bridge API v2.
    
    All API v2 requests require the application key in the header
    and use HTTPS with self-signed certificates.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path starting with / (e.g., "/resource/light")
        data: Optional JSON payload for POST/PUT requests
    
    Returns:
        JSON response as dictionary, or error dictionary on failure
        
    Response formats:
        Success: {"data": [...]} or {"errors": [], "data": [...]}
        Error: {"error": "error message"}
        
    Headers:
        hue-application-key: {api_key} - Required for authentication
        Content-Type: application/json - For requests with body
    """
    headers = {
        "hue-application-key": config['bridge']['api_key'],
        "Content-Type": "application/json"
    }
    
    url = f"{get_base_url()}{endpoint}"
    timeout = config['timeouts']['request']
    
    try:
        with httpx.Client(verify=False, timeout=timeout) as client:
            if method.upper() == "GET":
                response = client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = client.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = client.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = client.delete(url, headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available Hue API tools.
    
    Returns:
        List of Tool objects describing available MCP tools
        
    Tools are organized into categories:
    1. Setup: Authentication and bridge discovery
    2. Resource Access: Get resources and resource details
    3. Light Control: Control individual lights
    4. Room/Zone Control: Control groups of lights
    5. Scene Control: Activate scenes
    6. Search: Find resources by name
    """
    return [
        Tool(
            name="hue_setup_authentication",
            description="Initial setup: discover bridge and create application key. Press the link button on your Hue Bridge before calling this tool. This will save the configuration to hue_config.yaml",
            inputSchema={
                "type": "object",
                "properties": {
                    "bridge_ip": {
                        "type": "string",
                        "description": "Bridge IP address. Leave empty to auto-discover",
                    },
                    "app_name": {
                        "type": "string",
                        "description": "Application name (default: hue-mcp-server)",
                    }
                },
            },
        ),
        Tool(
            name="hue_get_resources",
            description="Get all resources or filter by specific resource type. Returns data array with resource objects. Common types: light, scene, room, zone, grouped_light, device, bridge, motion, temperature, button, entertainment_configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "Resource type to filter (optional). Leave empty for all resources. Examples: light, scene, room, zone, device, motion, temperature",
                    }
                },
            },
        ),
        Tool(
            name="hue_get_resource_by_id",
            description="Get specific resource by its UUID. Returns single resource object with full details",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_type": {
                        "type": "string",
                        "description": "Resource type (light, scene, room, zone, device, etc)",
                    },
                    "resource_id": {
                        "type": "string",
                        "description": "Resource UUID (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)",
                    }
                },
                "required": ["resource_type", "resource_id"],
            },
        ),
        Tool(
            name="hue_control_light",
            description="Control individual light state. Can set on/off, brightness (0-100%), color temperature (153-500 mirek), or XY color coordinates. Multiple properties can be set in one call",
            inputSchema={
                "type": "object",
                "properties": {
                    "light_id": {
                        "type": "string",
                        "description": "Light resource UUID",
                    },
                    "on": {
                        "type": "boolean",
                        "description": "Turn light on (true) or off (false)",
                    },
                    "brightness": {
                        "type": "number",
                        "description": "Brightness percentage (0-100). 0 is minimum dimming, 100 is maximum brightness",
                        "minimum": 0,
                        "maximum": 100,
                    },
                    "color_temperature": {
                        "type": "integer",
                        "description": "Color temperature in mirek (153=cool/6500K, 500=warm/2000K). Only for white ambiance and color lights",
                        "minimum": 153,
                        "maximum": 500,
                    },
                    "color_xy": {
                        "type": "object",
                        "description": "Color in CIE 1931 xy color space (0.0-1.0 for both x and y). Only for color lights",
                        "properties": {
                            "x": {"type": "number", "minimum": 0, "maximum": 1},
                            "y": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    },
                    "transition_time": {
                        "type": "integer",
                        "description": "Transition duration in milliseconds (default: 400ms). Time for light to reach target state",
                    }
                },
                "required": ["light_id"],
            },
        ),
        Tool(
            name="hue_control_room",
            description="Control all lights in a room or zone simultaneously. Uses the grouped_light service associated with the room. Changes apply to all lights in the group",
            inputSchema={
                "type": "object",
                "properties": {
                    "room_id": {
                        "type": "string",
                        "description": "Room or zone resource UUID",
                    },
                    "on": {
                        "type": "boolean",
                        "description": "Turn all lights on (true) or off (false)",
                    },
                    "brightness": {
                        "type": "number",
                        "description": "Brightness percentage for all lights (0-100)",
                        "minimum": 0,
                        "maximum": 100,
                    },
                    "color_temperature": {
                        "type": "integer",
                        "description": "Color temperature in mirek for all lights (153-500)",
                        "minimum": 153,
                        "maximum": 500,
                    }
                },
                "required": ["room_id"],
            },
        ),
        Tool(
            name="hue_activate_scene",
            description="Activate a saved scene. Applies the scene's light states to all associated lights. Scene must be in 'active' or 'static' state",
            inputSchema={
                "type": "object",
                "properties": {
                    "scene_id": {
                        "type": "string",
                        "description": "Scene resource UUID to activate",
                    }
                },
                "required": ["scene_id"],
            },
        ),
        Tool(
            name="hue_list_lights_detailed",
            description="Get comprehensive information about all lights including name, current state, brightness, color, capabilities, room assignments, and reachability status",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="hue_search_by_name",
            description="Search for resources by name (case-insensitive partial match). Can search across all resource types or filter by specific type. Returns array of matching resources with full details",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name or partial name to search for (case-insensitive)",
                    },
                    "resource_type": {
                        "type": "string",
                        "description": "Resource type to filter (light, room, scene, zone). Leave empty to search all types",
                    }
                },
                "required": ["name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle MCP tool calls and execute corresponding API operations.
    
    Args:
        name: Name of the tool to execute
        arguments: Dictionary of arguments for the tool
        
    Returns:
        List containing a single TextContent object with JSON response
        
    Tool execution flow:
        1. Parse and validate arguments
        2. Make API request(s) to Hue Bridge
        3. Process and format response
        4. Return as JSON text content
    """
    
    # ============================================================================
    # SETUP: Authentication and Bridge Discovery
    # ============================================================================
    
    if name == "hue_setup_authentication":
        """
        Setup tool: Discover bridge and create application key.
        
        Process:
        1. Discover bridge IP (if not provided)
        2. Prompt user to press link button
        3. Authenticate and get application key
        4. Save configuration to YAML file
        
        Args:
            bridge_ip (optional): Bridge IP address
            app_name (optional): Application name
            
        Returns:
            Success message with saved configuration
            or error message if setup failed
        """
        bridge_ip = arguments.get("bridge_ip", "")
        app_name = arguments.get("app_name", "hue-mcp-server")
        
        # Discover bridge if IP not provided
        if not bridge_ip:
            print("Discovering Hue Bridge...")
            bridge_ip = discover_bridge()
            if not bridge_ip:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Could not discover bridge. Please provide bridge_ip manually."}, indent=2)
                )]
            print(f"Found bridge at: {bridge_ip}")
        
        print("\n" + "="*60)
        print("PRESS THE LINK BUTTON ON YOUR HUE BRIDGE NOW")
        print("You have 30 seconds after pressing the button")
        print("="*60 + "\n")
        
        input("Press Enter after pressing the link button...")
        
        # Authenticate
        auth_result = authenticate_bridge(bridge_ip, app_name)
        
        if auth_result and "username" in auth_result:
            # Load current config or create new
            try:
                cfg = load_config()
            except:
                cfg = {
                    'bridge': {},
                    'api': {
                        'version': 'v2',
                        'base_path': '/clip/v2',
                        'use_https': True,
                        'verify_ssl': False
                    },
                    'timeouts': {
                        'request': 10,
                        'connection': 5
                    }
                }
            
            # Update with new credentials
            cfg['bridge']['ip'] = bridge_ip
            cfg['bridge']['api_key'] = auth_result['username']
            if 'clientkey' in auth_result:
                cfg['bridge']['client_key'] = auth_result['clientkey']
            
            # Save configuration
            save_config(cfg)
            
            # Reload global config
            global config
            config = cfg
            
            result = {
                "success": True,
                "message": "Authentication successful!",
                "bridge_ip": bridge_ip,
                "application_key": auth_result['username'],
                "config_file": str(CONFIG_FILE)
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Authentication failed. Make sure you pressed the link button.",
                    "bridge_ip": bridge_ip
                }, indent=2)
            )]
    
    # ============================================================================
    # RESOURCE ACCESS: Get Resources and Details
    # ============================================================================
    
    elif name == "hue_get_resources":
        """
        Get all resources or filter by resource type.
        
        API: GET /resource/{type} or GET /resource
        
        Args:
            resource_type (optional): Type to filter
            
        Returns:
            {"data": [array of resource objects]}
            or {"error": "..."} if request failed
        """
        resource_type = arguments.get("resource_type", "")
        endpoint = f"/resource/{resource_type}" if resource_type else "/resource"
        result = make_request("GET", endpoint)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "hue_get_resource_by_id":
        """
        Get specific resource by UUID and type.
        
        API: GET /resource/{type}/{id}
        
        Args:
            resource_type: Resource type (light, scene, etc)
            resource_id: Resource UUID
            
        Returns:
            {"data": [single resource object]}
            or {"error": "..."} if not found
        """
        resource_type = arguments["resource_type"]
        resource_id = arguments["resource_id"]
        endpoint = f"/resource/{resource_type}/{resource_id}"
        result = make_request("GET", endpoint)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    # ============================================================================
    # LIGHT CONTROL: Individual Light Control
    # ============================================================================
    
    elif name == "hue_control_light":
        """
        Control individual light state.
        
        API: PUT /resource/light/{id}
        
        Payload structure:
            {"on": {"on": true/false}}
            {"dimming": {"brightness": 0-100}}
            {"color_temperature": {"mirek": 153-500}}
            {"color": {"xy": {"x": 0-1, "y": 0-1}}}
            {"dynamics": {"duration": milliseconds}}
        
        Args:
            light_id: Light UUID
            on (optional): Turn on/off
            brightness (optional): Brightness 0-100%
            color_temperature (optional): Mirek 153-500
            color_xy (optional): XY coordinates
            transition_time (optional): Duration in ms
            
        Returns:
            {"data": [{"rid": "...", "rtype": "light"}]}
            or {"errors": [...]} if invalid
        """
        light_id = arguments["light_id"]
        endpoint = f"/resource/light/{light_id}"
        
        # Build payload according to API v2 structure
        payload = {}
        
        if "on" in arguments:
            payload["on"] = {"on": arguments["on"]}
        
        if "brightness" in arguments:
            # API expects brightness as percentage (0-100)
            payload["dimming"] = {"brightness": float(arguments["brightness"])}
        
        if "color_temperature" in arguments:
            payload["color_temperature"] = {"mirek": arguments["color_temperature"]}
        
        if "color_xy" in arguments:
            payload["color"] = {"xy": arguments["color_xy"]}
        
        if "transition_time" in arguments:
            payload["dynamics"] = {"duration": arguments["transition_time"]}
        
        result = make_request("PUT", endpoint, payload)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    # ============================================================================
    # ROOM/ZONE CONTROL: Group Light Control
    # ============================================================================
    
    elif name == "hue_control_room":
        """
        Control all lights in a room or zone.
        
        Process:
        1. Get room/zone resource to find grouped_light service
        2. Use grouped_light ID to control all lights
        
        API: GET /resource/room/{id} then PUT /resource/grouped_light/{id}
        
        Args:
            room_id: Room/zone UUID
            on (optional): Turn all lights on/off
            brightness (optional): Brightness for all lights
            color_temperature (optional): Color temp for all lights
            
        Returns:
            Response from grouped_light update
        """
        room_id = arguments["room_id"]
        
        # First get the grouped_light ID for this room
        room_data = make_request("GET", f"/resource/room/{room_id}")
        
        if "errors" in room_data:
            return [TextContent(type="text", text=json.dumps(room_data, indent=2))]
        
        # Find grouped_light service in room
        grouped_light_id = None
        if "data" in room_data and len(room_data["data"]) > 0:
            services = room_data["data"][0].get("services", [])
            for service in services:
                if service.get("rtype") == "grouped_light":
                    grouped_light_id = service.get("rid")
                    break
        
        if not grouped_light_id:
            return [TextContent(
                type="text",
                text=json.dumps({"error": "No grouped_light found for this room"}, indent=2)
            )]
        
        endpoint = f"/resource/grouped_light/{grouped_light_id}"
        
        # Build payload
        payload = {}
        if "on" in arguments:
            payload["on"] = {"on": arguments["on"]}
        if "brightness" in arguments:
            payload["dimming"] = {"brightness": float(arguments["brightness"])}
        if "color_temperature" in arguments:
            payload["color_temperature"] = {"mirek": arguments["color_temperature"]}
        
        result = make_request("PUT", endpoint, payload)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    # ============================================================================
    # SCENE CONTROL: Activate Scenes
    # ============================================================================
    
    elif name == "hue_activate_scene":
        """
        Activate a scene.
        
        API: PUT /resource/scene/{id}
        Payload: {"recall": {"action": "active"}}
        
        Args:
            scene_id: Scene UUID
            
        Returns:
            Response confirming scene activation
        """
        scene_id = arguments["scene_id"]
        endpoint = f"/resource/scene/{scene_id}"
        payload = {"recall": {"action": "active"}}
        
        result = make_request("PUT", endpoint, payload)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    # ============================================================================
    # DETAILED INFORMATION: List Lights with Full Details
    # ============================================================================
    
    elif name == "hue_list_lights_detailed":
        """
        Get comprehensive light information.
        
        Process:
        1. Get all lights
        2. Get all devices (to map light IDs to names)
        3. Get all rooms (to show room assignments)
        4. Combine data into detailed light list
        
        Returns:
            Array of light objects with:
            - id: Light UUID
            - name: Device name
            - type: Light type
            - on: Current on/off state
            - brightness: Current brightness
            - color_temp_mirek: Current color temperature
            - color_xy: Current color coordinates
            - reachable: Connection status
            - rooms: Array of room names
            - model: Product model name
        """
        # Get all lights
        lights_result = make_request("GET", "/resource/light")
        
        # Get all devices to map lights to metadata
        devices_result = make_request("GET", "/resource/device")
        
        # Get all rooms to show room assignment
        rooms_result = make_request("GET", "/resource/room")
        
        # Build device map
        device_map = {}
        if "data" in devices_result:
            for device in devices_result["data"]:
                device_map[device["id"]] = device
        
        # Build room map
        room_map = {}
        if "data" in rooms_result:
            for room in rooms_result["data"]:
                for service in room.get("services", []):
                    if service.get("rtype") == "device":
                        device_id = service.get("rid")
                        if device_id not in room_map:
                            room_map[device_id] = []
                        room_map[device_id].append(room.get("metadata", {}).get("name", "Unknown"))
        
        # Build detailed light list
        detailed_lights = []
        if "data" in lights_result:
            for light in lights_result["data"]:
                # Find device info
                owner_id = light.get("owner", {}).get("rid")
                device_info = device_map.get(owner_id, {})
                device_name = device_info.get("metadata", {}).get("name", "Unknown")
                
                rooms = room_map.get(owner_id, ["Unassigned"])
                
                detailed_lights.append({
                    "id": light["id"],
                    "name": device_name,
                    "type": light["type"],
                    "on": light.get("on", {}).get("on", False),
                    "brightness": light.get("dimming", {}).get("brightness"),
                    "color_temp_mirek": light.get("color_temperature", {}).get("mirek"),
                    "color_xy": light.get("color", {}).get("xy"),
                    "reachable": light.get("status") != "connectivity_issue",
                    "rooms": rooms,
                    "model": device_info.get("product_data", {}).get("product_name"),
                })
        
        return [TextContent(
            type="text",
            text=json.dumps(detailed_lights, indent=2)
        )]
    
    # ============================================================================
    # SEARCH: Find Resources by Name
    # ============================================================================
    
    elif name == "hue_search_by_name":
        """
        Search for resources by name across types.
        
        Process:
        1. Determine which resource types to search
        2. Get resources of each type
        3. Filter by name match (case-insensitive)
        4. For lights, look up device name
        
        Args:
            name: Search term (partial match)
            resource_type (optional): Filter to specific type
            
        Returns:
            Array of matching resources with:
            - type: Resource type
            - id: Resource UUID
            - name: Resource name
            - data: Full resource object
        """
        search_name = arguments["name"].lower()
        resource_type = arguments.get("resource_type", "")
        
        results = []
        
        # Determine which resource types to search
        types_to_search = [resource_type] if resource_type else ["light", "room", "scene", "zone"]
        
        for rtype in types_to_search:
            endpoint = f"/resource/{rtype}"
            response = make_request("GET", endpoint)
            
            if "data" in response:
                for item in response["data"]:
                    name = item.get("metadata", {}).get("name", "")
                    
                    # For lights, we need to look up the device name
                    if rtype == "light":
                        owner_id = item.get("owner", {}).get("rid")
                        device_response = make_request("GET", f"/resource/device/{owner_id}")
                        if "data" in device_response and len(device_response["data"]) > 0:
                            name = device_response["data"][0].get("metadata", {}).get("name", "")
                    
                    if search_name in name.lower():
                        results.append({
                            "type": rtype,
                            "id": item["id"],
                            "name": name,
                            "data": item
                        })
        
        return [TextContent(
            type="text",
            text=json.dumps(results, indent=2)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]


async def main():
    """
    Main entry point for MCP server.
    
    Process:
    1. Load configuration from YAML file
    2. Validate configuration
    3. Start MCP server with stdio transport
    
    Configuration requirements:
    - bridge.ip must be set
    - bridge.api_key must be set (use hue_setup_authentication first)
    
    The server runs indefinitely, handling tool calls via stdio.
    """
    global config
    
    try:
        config = load_config()
        
        # Validate configuration
        if not config.get('bridge', {}).get('ip'):
            print("ERROR: Bridge IP not configured.")
            print("Please edit hue_config.yaml or run the authentication setup tool.")
            sys.exit(1)
        
        if not config.get('bridge', {}).get('api_key'):
            print("ERROR: API key not configured.")
            print("Please run the hue_setup_authentication tool first.")
            sys.exit(1)
        
        print(f"Hue MCP Server starting...")
        print(f"Bridge: {config['bridge']['ip']}")
        print(f"Config: {CONFIG_FILE}")
        print()
        
    except Exception as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

