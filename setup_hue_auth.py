#!/usr/bin/env python3
"""
Philips Hue Bridge Authentication Setup

This script helps you authenticate with your Hue Bridge and generates
the application key needed for API access.

Process:
1. Discover bridge IP address (or use provided IP)
2. Prompt user to press link button on bridge
3. Authenticate and retrieve application key
4. Save configuration to hue_config.yaml

Requirements:
- Hue Bridge on same network
- Physical access to press link button
- Network connectivity
"""

import httpx
import yaml
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Configuration file path
CONFIG_FILE = Path(__file__).parent / "hue_config.yaml"


def discover_bridge() -> Optional[str]:
    """
    Discover Hue Bridge IP address using Philips discovery service.
    
    Uses: GET https://discovery.meethue.com/
    
    Returns:
        Bridge IP address or None if not found
        
    Note: Bridge must have connected to Hue cloud at least once
    """
    print("Discovering Hue Bridge...")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://discovery.meethue.com/")
            response.raise_for_status()
            bridges = response.json()
            
            if bridges and len(bridges) > 0:
                ip = bridges[0]["internalipaddress"]
                bridge_id = bridges[0].get("id", "unknown")
                print(f"✓ Found bridge at {ip} (ID: {bridge_id})")
                return ip
            else:
                print("✗ No bridges found via discovery service")
                return None
                
    except Exception as e:
        print(f"✗ Discovery failed: {e}")
        return None


def authenticate_bridge(bridge_ip: str, app_name: str = "hue-mcp-server") -> Optional[Dict[str, str]]:
    """
    Authenticate with Hue Bridge to generate application key.
    
    API: POST https://{bridge_ip}/api
    Payload: {"devicetype": "app#instance", "generateclientkey": true}
    
    Args:
        bridge_ip: Bridge IP address
        app_name: Application identifier
        
    Returns:
        Dict with 'username' (app key) and 'clientkey' if successful
        None if authentication failed
        
    Note: Link button must be pressed within 30 seconds before calling
    """
    url = f"https://{bridge_ip}/api"
    
    payload = {
        "devicetype": f"{app_name}#python-mcp",
        "generateclientkey": True
    }
    
    print(f"Authenticating with bridge at {bridge_ip}...")
    
    try:
        with httpx.Client(verify=False, timeout=10.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Parse response
            if isinstance(result, list) and len(result) > 0:
                if "success" in result[0]:
                    print("✓ Authentication successful!")
                    return result[0]["success"]
                elif "error" in result[0]:
                    error = result[0]["error"]
                    error_type = error.get("type")
                    error_desc = error.get("description", "Unknown error")
                    
                    print(f"✗ Error: {error_desc}")
                    
                    if error_type == 101:
                        print("\n⚠️  Link button was not pressed!")
                        print("   Press the button on your bridge and try again.")
                    
                    return None
            
            print("✗ Unexpected response format")
            return None
            
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return None


def load_or_create_config() -> Dict[str, Any]:
    """
    Load existing config or create default structure.
    
    Returns:
        Configuration dictionary
    """
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    
    # Default configuration structure
    return {
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


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary to save
    """
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Configuration saved to {CONFIG_FILE}")


def main():
    """
    Main authentication setup flow.
    
    Steps:
    1. Get bridge IP (discover or manual entry)
    2. Prompt for link button press
    3. Authenticate
    4. Save configuration
    """
    print("=" * 70)
    print("PHILIPS HUE BRIDGE AUTHENTICATION SETUP")
    print("=" * 70)
    print()
    
    # Step 1: Get bridge IP
    print("Step 1: Locate Hue Bridge")
    print("-" * 70)
    
    bridge_ip = discover_bridge()
    
    if not bridge_ip:
        print("\nCould not auto-discover bridge.")
        bridge_ip = input("Enter bridge IP address manually: ").strip()
        
        if not bridge_ip:
            print("✗ No IP address provided. Exiting.")
            sys.exit(1)
    
    print()
    
    # Step 2: Prompt for link button
    print("Step 2: Press Link Button")
    print("-" * 70)
    print("⚠️  IMPORTANT: Press the large button on top of your Hue Bridge NOW")
    print("   You have 30 seconds after pressing to complete authentication")
    print()
    
    input("Press Enter after you have pressed the link button...")
    print()
    
    # Step 3: Authenticate
    print("Step 3: Authenticate")
    print("-" * 70)
    
    auth_result = authenticate_bridge(bridge_ip)
    
    if not auth_result or "username" not in auth_result:
        print("\n✗ Authentication failed!")
        print("\nTroubleshooting:")
        print("  1. Make sure you pressed the link button")
        print("  2. Ensure bridge is connected to network")
        print("  3. Check bridge IP address is correct")
        print(f"  4. Try accessing https://{bridge_ip} in browser")
        sys.exit(1)
    
    print()
    
    # Step 4: Save configuration
    print("Step 4: Save Configuration")
    print("-" * 70)
    
    config = load_or_create_config()
    
    # Update with authentication credentials
    config['bridge']['ip'] = bridge_ip
    config['bridge']['api_key'] = auth_result['username']
    
    if 'clientkey' in auth_result:
        config['bridge']['client_key'] = auth_result['clientkey']
    
    save_config(config)
    
    print()
    print("=" * 70)
    print("✓ SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("Configuration Details:")
    print(f"  Bridge IP:       {bridge_ip}")
    print(f"  Application Key: {auth_result['username']}")
    print(f"  Config File:     {CONFIG_FILE}")
    print()
    print("Next Steps:")
    print("  1. Run: python hue_mcp_server.py")
    print("  2. Test with MCP tools or use test_hue_api.sh")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
