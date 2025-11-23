# Philips Hue Device Database

Complete reference database of Philips Hue products with model IDs, specifications, and capabilities.

## Database Overview

**File:** `philips_hue_devices_database.csv`
**Total Devices:** 148 products
**Format:** CSV (Comma-Separated Values)

## Column Definitions

| Column | Description | Example Values |
|--------|-------------|----------------|
| `model_id` | Official Philips model identifier used in API | LCA007, LST002, SML001 |
| `product_name` | Human-readable product name | Hue Color Bulb A19/E26 |
| `product_archetype` | Device archetype for categorization | sultan_bulb, huelightstrip, motion_sensor |
| `device_category` | High-level category | Light Bulb, Light Strip, Sensor, Control |
| `light_type` | Lighting capability type | Color, White Ambiance, White Only, N/A |
| `max_lumens` | Maximum light output in lumens | 800, 1600, N/A |
| `color_temperature_range` | Mirek range for white ambiance | 153-500 mirek |
| `notes` | Additional information | Generation, special features |
| `generation` | Product generation number | 1, 2, 3, 3.1, 4 |

## Device Categories

### Light Bulbs (45 models)
Standard screw-base bulbs in various sizes and capabilities:
- **Color:** Full RGB + white (LCA/LCT series)
- **White Ambiance:** Tunable white 153-500 mirek (LTA/LTW series)
- **White Only:** Dimmable white (LWA/LWB series)

**Brightness Ranges:**
- 600 lumens (Gen 1)
- 750-840 lumens (Standard)
- 1100 lumens (High brightness)
- 1600 lumens (Maximum brightness)

### Light Strips (18 models)
Flexible LED strips for accent and ambient lighting:
- **Indoor:** 1600 lumens standard (LCL/LST series)
- **Outdoor:** IP67 rated, 780-1950 lumens (LST003/004)
- **Gradient:** Multi-zone color effects (LCX/LCL007)
- **TV Sync:** 55", 65", 75" gradient strips

### Flood & Spot Lights (15 models)
Directional lighting for recessed and track fixtures:
- **BR30 Floods:** 650 lumens
- **GU10 Spots:** 250-400 lumens
- **PAR38 Outdoor:** 1350 lumens

### Candle Bulbs (8 models)
Small decorative bulbs for chandeliers:
- **E14 (European):** 470 lumens
- **E12 (US Candelabra):** 470 lumens
- Color and White Ambiance options

### Filament Bulbs (8 models)
Vintage Edison-style smart bulbs:
- **Output:** 550 lumens
- **Styles:** A60, ST64/ST72, G93 globe
- White only or White Ambiance

### Ceiling Lights (15 models)
Integrated ceiling fixtures:
- **Round/Square:** 2400-3200 lumens
- **White Ambiance or Color**
- Bathroom-rated options (LWE series)

### Portable Lights (4 models)
Battery-powered accent lights:
- **Hue Go:** 300-400 lumens, rechargeable
- **Hue Go Portable:** Table lamp version

### Accent Lights (10 models)
Specialty lighting for ambiance:
- **Bloom:** 120-250 lumens spot
- **Iris:** 210-570 lumens diffused
- **Play Bar:** 530 lumens compact
- **Signe:** 2000 lumens gradient tube

### Outdoor Lights (14 models)
Weather-resistant outdoor products:
- **Lily Spots:** 640 lumens ground/wall spots
- **Calla Bollards:** 600 lumens posts
- **Wall Lanterns:** 930-1350 lumens
- **Floodlights:** 2300 lumens with security

### String Lights (2 models)
Decorative outdoor string lighting:
- **Festavia:** 250 lumens, 20m or 40m length

### Table & Floor Lamps (8 models)
Complete lamp fixtures:
- **Table Lamps:** 420-2000 lumens
- **Floor Lamps:** 2000 lumens
- **Wellness:** Wake-up light features
- **Twilight:** Sleep-optimized

### Pendant Lights (3 models)
Hanging/suspended fixtures:
- **Ensis:** 3000 lumens long pendant
- **Phoenix:** 600 lumens round pendant

### Track Lighting (4 models)
Modular track-mounted systems:
- **Centris:** Modular spots
- **Runner:** Bar with multiple spots
- **Perifo:** Complete track system

### Sensors (5 models)
Environmental sensing devices:
- **Motion Sensors:** Indoor/outdoor (SML series)
- **Contact Sensors:** Door/window detection
- Temperature and light level sensing included

### Controls (9 models)
Wireless control devices:
- **Dimmer Switch:** 4-button wireless (RWL series)
- **Smart Button:** Single button (ROM series)
- **Tap Dial:** Rotary dimmer (RDM001)
- **Tap:** Battery-free 4-button (RDM002)
- **Wall Switch Module:** Behind-switch control

### Smart Plugs (5 models)
Outlet control devices:
- EU, US, UK variants
- On/off control only (no dimming)
- Some models have status LED

### Bridges (3 models)
Central control hubs:
- **Bridge v1 (BSB001):** Round, discontinued
- **Bridge v2 (BSB002):** Square, current standard
- **Bridge Pro (LCF003):** Professional features

### Accessories (3 models)
Additional equipment:
- **Play HDMI Sync Box:** Standard HDMI
- **Sync Box 8K:** 8K HDMI support
- **Security Cameras:** Integration with lighting

## Light Type Details

### Color (Full RGB + White)
- **Models:** LCA, LCT, LCE, LCL, LCX, LLC series
- **Capabilities:** 
  - 16 million colors
  - Full white spectrum (153-500 mirek)
  - Scenes and color effects
  - Entertainment sync
- **Color Gamut Types:**
  - Gamut A: Gen 1 (limited)
  - Gamut B: Gen 2
  - Gamut C: Gen 3+ (best colors)

### White Ambiance (Tunable White)
- **Models:** LTA, LTW, LTC, LTD, LDF series
- **Range:** 153-500 mirek
  - 153 mirek = 6500K (cool white)
  - 500 mirek = 2000K (warm white)
- **Use Cases:** 
  - Task lighting
  - Circadian rhythm support
  - Wake-up/sleep routines

### White Only (Dimmable)
- **Models:** LWA, LWB, LWO, LDF (some) series
- **Capabilities:**
  - On/off control
  - Brightness: 0-100%
  - Single color temperature (typically ~2700K)
- **Advantages:** Lower cost, simple control

## Lumen Ranges by Category

| Lumens | Equivalent Wattage | Typical Products | Use Case |
|--------|-------------------|------------------|----------|
| 120-300 | 15-25W | Accent lights, Bloom, Go | Mood/ambient |
| 400-550 | 40-50W | Candles, GU10, Filament | Decorative |
| 600-840 | 60W | Standard bulbs Gen 1-4 | General lighting |
| 1100 | 75W | High-output bulbs | Task lighting |
| 1600 | 100W | Maximum bulbs, strips | High-output spaces |
| 2000-3200 | 150-200W | Ceiling fixtures, lamps | Large rooms |

## Generation Guide

### Generation 1 (2012-2015)
- Model IDs: LCT001-003, LLC006-007, LST001, BSB001
- Lumens: 600 (bulbs)
- Color gamut: Limited (Gamut A/B)
- Notable: Original round bridge

### Generation 2 (2015-2016)
- Model IDs: LCA001, LCT007/010/011/014, LTW001/004
- Lumens: 800-806
- Color gamut: Improved (Gamut B)
- Notable: Square bridge (BSB002), HomeKit support

### Generation 3 (2016-2019)
- Model IDs: LCA002, LCT015, LTW010
- Lumens: 800-806
- Color gamut: Rich colors (Gamut C)
- Notable: "Richer colors" branding, improved blues/greens

### Generation 3.1 (2019-2020)
- Model IDs: LCA003, LCT016
- Lumens: 800-806
- Improvements: Power efficiency, minor hardware changes
- Notable: Bluetooth added to some models

### Generation 4 (2020-Present)
- Model IDs: LCA004-007, LTA series, LCL008
- Lumens: 1100-1600 options
- Notable: Highest brightness, Bluetooth standard, Zigbee 3.0

## Archetype Reference

**Light Bulbs:**
- `sultan_bulb` - Standard A-shape
- `classic_bulb` - Classic/vintage shape
- `candle_bulb` - Candle shape
- `spot_bulb` - Flood/spot shape

**Fixtures:**
- `ceiling_round` - Round ceiling
- `ceiling_square` - Square ceiling
- `ceiling_horizontal` - Bar ceiling
- `pendant_round` - Round pendant
- `pendant_long` - Long pendant

**Specialty:**
- `huelightstrip` - Flexible strip
- `hueplay` - Play bar
- `huego` - Portable Go
- `huebloom` - Bloom/Iris
- `gradient_tube` - Signe gradient

**Outdoor:**
- `bollard` - Post/bollard
- `wall_lantern` - Wall mount

**Controls:**
- `dimmer_switch` - Dimmer
- `motion_sensor` - Motion detector
- `plug` - Smart plug
- `bridge_v2` - Bridge hub

## Usage Examples

### Query by Model ID
```bash
grep "LCA007" philips_hue_devices_database.csv
```
Output: `LCA007,Hue Color Bulb A19/E26,sultan_bulb,Light Bulb,Color,1100,,Gen 4,4`

### Find All Color Bulbs
```bash
grep ",Color," philips_hue_devices_database.csv | grep "Light Bulb"
```

### List All 1600 Lumen Products
```bash
grep ",1600," philips_hue_devices_database.csv
```

### Find Sensors
```bash
grep "Sensor" philips_hue_devices_database.csv
```

### Python Usage
```python
import csv

with open('philips_hue_devices_database.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['light_type'] == 'Color' and int(row['max_lumens']) >= 1100:
            print(f"{row['model_id']}: {row['product_name']} - {row['max_lumens']} lumens")
```

## Notes

### Data Accuracy
- Information compiled from official Philips Hue documentation
- Model IDs verified against API responses
- Specifications current as of November 2024
- Some older/regional models may not be included

### Not Included
- Third-party Hue-compatible devices
- Discontinued models without model IDs
- Region-specific SKU variations
- Beta/unreleased products

### Lumens Caveat
- Maximum lumens achieved at specific white temperatures
- Color modes typically produce less light output
- Actual brightness depends on settings and age

## Related Files

- `DEVICE_VS_LIGHT.md` - Explanation of device vs light resources
- `DEVICE_TYPE_IDENTIFICATION.md` - How to identify device types in API
- `hue_mcp_server.py` - MCP server using this data
- `lights.json` - Your personal Hue system data

## Updates

To add new products:
1. Get model_id from API or documentation
2. Determine product_archetype from device resource
3. Add row with all specifications
4. Maintain CSV format

## License

This reference database is compiled from publicly available Philips Hue documentation for development purposes.
