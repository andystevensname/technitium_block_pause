# Technitium AdBlock Toggle

A Home Assistant custom integration to monitor and control ad blocking on a [Technitium DNS Server](https://technitium.com/dns/).

## Features

- **Switch entity** - Toggle ad blocking on/off directly from Home Assistant
- **Sensor entity** - Shows blocking status (`enabled`, `paused`, or `disabled`) with attributes
- **Services** - Pause, enable, or disable ad blocking via automations
- **Device grouping** - Entities grouped under a Technitium device in the UI
- **Connection validation** - Tests connection during setup

## Compatibility

| Software | Tested Version |
|----------|----------------|
| Home Assistant | 2026.2.2 |
| Technitium DNS Server | v14.3 |

*Other versions may work but have not been tested.*

## Installation

### Manual Installation
1. Copy the `technitium_adblock_toggle` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for "Technitium Block Pause"
5. Enter your Technitium DNS server URL and API token

### HACS (Coming Soon)
This integration may be added to HACS in the future.

## Configuration

| Field | Description | Example |
|-------|-------------|----------|
| Host URL | URL to your Technitium DNS server | `http://192.168.1.100:5380` |
| API Token | Your Technitium API token | Get from Technitium web UI |

### Getting Your API Token
1. Open the Technitium DNS web console
2. Go to **Administration → Sessions**
3. Create a new API token or use an existing session token

## Entities

### Switch: Ad Blocking
- **Entity ID**: `switch.technitium_adblock_toggle_ad_blocking`
- **ON**: Ad blocking is enabled
- **OFF**: Ad blocking is disabled

### Sensor: Blocking Status
- **Entity ID**: `sensor.technitium_adblock_toggle_blocking_status`
- **States**: `enabled`, `paused`, `disabled`, `unknown`
- **Attributes**:
  - `enable_blocking`: Whether blocking is enabled in settings
  - `temporary_disable_until`: Timestamp when temporary pause ends (if paused)

## Services

### `technitium_adblock_toggle.pause_ad_blocking`
Temporarily pause ad blocking for a specified duration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| duration | int | Yes | Seconds to pause (converted to minutes for Technitium) |

### `technitium_adblock_toggle.enable_ad_blocking`
Enable ad blocking (cancels any temporary pause).

### `technitium_adblock_toggle.disable_ad_blocking`
Disable ad blocking indefinitely.

## Options

After setup, you can configure these options:

| Option | Default | Description |
|--------|---------|-------------|
| Update interval | 30 | Seconds between status polls |
| Pause min | 60 | Minimum pause duration (seconds) |
| Pause max | 86400 | Maximum pause duration (seconds) |
| API timeout | 10 | API request timeout (seconds) |

## Example Dashboard Card - Basic

![Screenshot description](docs/images/demo-basic.png)

```yaml
type: horizontal-stack
cards:
  - type: button
    name: Enable
    icon: mdi:shield-check
    tap_action:
      action: call-service
      service: technitium_adblock_toggle.enable_ad_blocking
  - type: button
    name: 5 min
    icon: mdi:shield-off
    tap_action:
      action: call-service
      service: technitium_adblock_toggle.pause_ad_blocking
      data:
        duration: 300
  - type: button
    name: Disable
    icon: mdi:shield-off-outline
    tap_action:
      action: call-service
      service: technitium_adblock_toggle.disable_ad_blocking
```

## Example Dashboard Card - Bubble Card

![Screenshot description](docs/images/demo-bubblecard.png)

```yaml
button_type: switch
sub_button:
  main:
    - name: Pause Blocking
      buttons_layout: inline
      group:
        - name: "5"
          tap_action:
            action: perform-action
            perform_action: technitium_adblock_toggle.pause_ad_blocking
            target: {}
            data:
              duration: 300
          show_name: true
          visibility:
            - condition: state
              entity: switch.technitium_adblock_toggle_ad_blocking
              state: "on"
          hide_when_parent_unavailable: false
        - name: "15"
          tap_action:
            action: perform-action
            perform_action: technitium_adblock_toggle.pause_ad_blocking
            target: {}
            data:
              duration: 900
          show_name: true
          visibility:
            - condition: state
              entity: switch.technitium_adblock_toggle_ad_blocking
              state: "on"
        - name: "30"
          show_name: true
          visibility:
            - condition: state
              entity: switch.technitium_adblock_toggle_ad_blocking
              state: "on"
          tap_action:
            action: perform-action
            perform_action: technitium_adblock_toggle.pause_ad_blocking
            target: {}
            data:
              duration: 1800
        - name: Stop
          show_state: false
          show_name: true
          tap_action:
            action: perform-action
            perform_action: technitium_adblock_toggle.disable_ad_blocking
            target: {}
          visibility:
            - condition: state
              entity: switch.technitium_adblock_toggle_ad_blocking
              state: "on"
    - name: Start
      buttons_layout: inline
      group:
        - name: Start
          show_name: true
          tap_action:
            action: perform-action
            perform_action: technitium_adblock_toggle.enable_ad_blocking
            target: {}
          visibility:
            - condition: state
              entity: switch.technitium_adblock_toggle_ad_blocking
              state: "off"
          hide_when_parent_unavailable: false
  bottom: []
slider_fill_orientation: left
slider_value_position: right
grid_options:
  columns: full
name: Pause Ad Block
icon: mdi:block-helper
show_icon: true
force_icon: true
scrolling_effect: false
show_state: true
entity: switch.technitium_adblock_toggle_ad_blocking
```

## Links

- [Technitium DNS Server](https://technitium.com/dns/)
- [Technitium API Documentation](https://github.com/TechnitiumSoftware/DnsServer/blob/master/APIDOCS.md)
- [Report Issues](https://github.com/andystevensname/technitium_adblock_toggle/issues)
