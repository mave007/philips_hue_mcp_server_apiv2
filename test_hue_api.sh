#!/bin/bash
# Test Philips Hue API v2 connectivity and basic operations

HUE_IP=""  # NEED TO ADD
HUE_KEY="" # NEED TO ADD
BASE_URL="https://${HUE_IP}/clip/v2"

echo "=== Testing Philips Hue API v2 ==="
echo "Bridge: ${HUE_IP}"
echo

# Test 1: Get all lights
echo "1. Getting all lights..."
curl --insecure -s \
  -H "hue-application-key: ${HUE_KEY}" \
  "${BASE_URL}/resource/light" | jq '.data[] | {id, type, on: .on.on, brightness: .dimming.brightness}'
echo

# Test 2: Get all rooms
echo "2. Getting all rooms..."
curl --insecure -s \
  -H "hue-application-key: ${HUE_KEY}" \
  "${BASE_URL}/resource/room" | jq '.data[] | {id, name: .metadata.name, type}'
echo

# Test 3: Get all scenes
echo "3. Getting all scenes..."
curl --insecure -s \
  -H "hue-application-key: ${HUE_KEY}" \
  "${BASE_URL}/resource/scene" | jq '.data[] | {id, name: .metadata.name, group: .group.rtype}'
echo

# Test 4: Get bridge info
echo "4. Getting bridge information..."
curl --insecure -s \
  -H "hue-application-key: ${HUE_KEY}" \
  "${BASE_URL}/resource/bridge" | jq '.data[] | {id, bridge_id, model: .product_data.model_id}'
echo

# Test 5: Get devices
echo "5. Getting devices..."
curl --insecure -s \
  -H "hue-application-key: ${HUE_KEY}" \
  "${BASE_URL}/resource/device" | jq '.data[] | {id, name: .metadata.name, product: .product_data.product_name}'
echo

echo "=== Test Complete ==="
