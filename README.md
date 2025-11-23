# TRMNL E-Ink Display Integration

Home Assistant integration for controlling TRMNL e-ink display devices. Send images and update display variables directly from Home Assistant automations.

## Features

- **Multiple TRMNL Implementations**: Support for Standard TRMNL, Terminus BYOS, and Generic BYOS devices
- **Image Delivery**: Send images to TRMNL devices via simple service calls
- **Variable Updates**: Send and merge display variables for dynamic content
- **Rate Limiting**: Built-in per-device rate limiting to respect API quotas
- **Webhook Support**: Automatic webhook registration for Standard TRMNL devices
- **Easy Configuration**: Simple UI-based config flow for device setup

## Installation

### Via HACS (Recommended)

1. Open Home Assistant and go to **Settings → Devices & Services → Integrations**
2. Click **+ Create Integration**
3. Search for "TRMNL"
4. Follow the configuration wizard

### Manual Installation

1. Clone this repository to your Home Assistant config:
   ```bash
   git clone https://github.com/yourusername/ha-trmnl-integration.git \
     /home/homeassistant/.homeassistant/custom_components/trmnl
   ```

2. Restart Home Assistant

3. Add the integration via **Settings → Devices & Services → Integrations**

## Configuration

### Initial Setup

When you add the integration, you'll be prompted to select your device type:

#### Standard TRMNL (Cloud)
- Connects to devices on usetrmnl.com
- Requires: Device ID and API Key
- Gets plugin_uuid automatically during setup

**To find your credentials:**
1. Log in to [usetrmnl.com](https://usetrmnl.com)
2. Go to your account settings
3. Find your API Key and Device ID

#### Terminus BYOS
- Self-hosted TRMNL implementation
- Requires: Device ID and API endpoint URL

#### Generic BYOS
- Custom BYOS implementation
- Requires: API endpoint URL and authentication key

### Service Configuration

The integration exposes two main services:

#### `trmnl.send_image`
Send an image to your TRMNL device.

```yaml
service: trmnl.send_image
data:
  device_id: "XX:XX:XX:XX:XX:XX"
  image_url: "https://example.com/image.png"
  refresh_rate: 300  # Optional: seconds between refreshes
```

**Parameters:**
- `device_id` (required): MAC address of your TRMNL device
- `image_url` (required): Full URL to PNG/JPG image
- `refresh_rate` (optional): Display refresh interval in seconds

#### `trmnl.send_merge_variables`
Update display variables (for dynamic content).

```yaml
service: trmnl.send_merge_variables
data:
  device_id: "XX:XX:XX:XX:XX:XX"
  variables:
    temperature: 72
    humidity: 45
  merge_strategy: "deep_merge"  # Or "stream"
```

**Parameters:**
- `device_id` (required): MAC address of your TRMNL device
- `variables` (required): Dictionary of key-value pairs
- `merge_strategy` (optional): "deep_merge" (default) or "stream"

## Usage Examples

### Update Display Every 30 Minutes

```yaml
automation:
  - alias: "Update TRMNL Display"
    trigger:
      platform: time_pattern
      minutes: "/30"
    action:
      service: trmnl.send_image
      data:
        device_id: "XX:XX:XX:XX:XX:XX"
        image_url: "https://example.com/dashboard.png"
```

### Show Weather on Demand

```yaml
automation:
  - alias: "TRMNL Weather Update"
    trigger:
      platform: state
      entity_id: weather.home
    action:
      service: trmnl.send_image
      data:
        device_id: "XX:XX:XX:XX:XX:XX"
        image_url: "https://example.com/weather.png"
```

### Update Display Variables

```yaml
automation:
  - alias: "TRMNL Show Sensor Data"
    trigger:
      platform: time_pattern
      minutes: "/10"
    action:
      service: trmnl.send_merge_variables
      data:
        device_id: "XX:XX:XX:XX:XX:XX"
        variables:
          temperature: "{{ states('sensor.temperature') }}"
          humidity: "{{ states('sensor.humidity') }}"
          last_update: "{{ now().strftime('%H:%M') }}"
```

## Rate Limiting

The integration includes per-device rate limiting to respect API quotas:

- **Default limit**: 12 requests per hour per device
- **Customizable**: Adjust via integration options
- **Automatic tracking**: Tracks requests and wait times
- **Disable if needed**: Turn off in integration options (not recommended)

## Troubleshooting

### "Plugin UUID not configured"
**Standard TRMNL only.** The integration failed to register your webhook with TRMNL.

**Solution:**
1. Go to integration options
2. Click "Reconfigure"
3. The integration will attempt to register again

### Images Not Displaying
1. Verify the image URL is publicly accessible
2. Check image dimensions match device (typically 800x480)
3. Try a simple test image: `https://via.placeholder.com/800x480`
4. Check Home Assistant logs for error messages

### Rate Limit Exceeded
If you're hitting rate limits:
1. Increase the time between updates
2. Combine multiple updates into one service call
3. Contact TRMNL support about your quota

## Architecture

### Client System

The integration uses an abstract client pattern for flexibility:

- **`StandardTRMNLClient`**: Cloud-based via usetrmnl.com
- **`TerminusClient`**: Terminus self-hosted BYOS
- **`GenericBYOSClient`**: Custom BYOS implementations

All clients implement a common interface for image and variable sending.

### Services Architecture

- **Rate Limiter**: Per-device request limiting with timestamp tracking
- **Service Handlers**: Async handlers for image and variable sending
- **Client Factory**: Dynamic client instantiation based on config

## Requirements

- Home Assistant 2024.1.0 or later
- TRMNL device (Standard or BYOS)
- TRMNL API key (for Standard TRMNL)
- Network access from Home Assistant to TRMNL API

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Ask questions on GitHub Discussions
- **TRMNL Support**: Visit [usetrmnl.com](https://usetrmnl.com) for device support

## Disclaimer

This integration is not officially affiliated with TRMNL. Use at your own risk.
