# Divera 24/7 Integration for Home Assistant 🏠

[![GitHub Release](https://img.shields.io/github/v/release/fwmarcel/home-assistant-divera?sort=semver&style=for-the-badge&color=green)](https://github.com/fwmarcel/home-assistant-divera/releases/)
[![GitHub Release Date](https://img.shields.io/github/release-date/fwmarcel/home-assistant-divera?style=for-the-badge&color=green)](https://github.com/fwmarcel/home-assistant-divera/releases/)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/fwmarcel/home-assistant-divera/latest/total?style=for-the-badge&label=Downloads%20latest%20Release)
![HA Analytics](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fanalytics.home-assistant.io%2Fcustom_integrations.json&query=%24.divera.total&style=for-the-badge&label=Active%20Installations&color=red)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/fwmarcel/home-assistant-divera?style=for-the-badge)
[![hacs](https://img.shields.io/badge/HACS-Integration-blue.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![BuyMeCoffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge)](https://www.buymeacoffee.com/fwmarcel)

## Overview

The Divera 24/7 Home Assistant Custom Integration allows you to integrate your Divera 24/7
system with your Home Assistant setup. With this integration, you can monitor and control your Divera 24/7
devices directly from your Home Assistant dashboard, enabling seamless automation and enhanced security for your home or office.

## Installation

### HACS (recommended)

This integration is available in HACS (Home Assistant Community Store).

1. Install HACS if you don't have it already
2. Open HACS in Home Assistant
3. Go to any of the sections (integrations, frontend, automation).
4. Click on the 3 dots in the top right corner.
5. Select "Custom repositories"
6. Add following URL to the repository `https://github.com/fwmarcel/home-assistant-divera`.
7. Select Integration as category.
8. Click the "ADD" button
9. Search for "Divera"
10. Click the "Download" button

### Manual

To install this integration manually you have to download [_divera.zip_](https://github.com/fwmarcel/home-assistant-divera/releases/latest/download/divera.zip) and extract its contents to `config/custom_components/divera` directory:

```bash
mkdir -p custom_components/divera
cd custom_components/divera
wget https://github.com/fwmarcel/home-assistant-divera/releases/latest/download/divera.zip
unzip divera.zip
rm divera.zip
```

## Configuration

### Using UI

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=divera)

From the Home Assistant front page go to `Configuration` and then select `Devices & Services` from the list.
Use the `Add Integration` button in the bottom right to add a new integration called `Divera 24/7`.

A dialog appears in which your access key must be entered.
You can also change the server address if you are hosting Divera Server in your own.
In the next step, you can select the units you are a member of.

### How do you get your required access key?

1. Open the settings [website](https://app.divera247.com/account/einstellungen.html) of divera.
2. Change to the debug tab.
3. Copy your accesskey

![image](https://user-images.githubusercontent.com/59510296/177019399-29de6824-c149-4949-8421-d0edc69a7126.png)

## Usage

Once the integration is set up and configured, you can use it to monitor and manage your own availability in Home Assistant.
Access the Divera 24/7 entities from your Home Assistant dashboard to view availability status, receive alerts, and trigger actions as needed.

The entities are updated every minute by default.
If a more frequent update is required, this must be implemented using the `homeassistant.update_entity` service itself. However, I do not recommend this.

### Entities

This integration provides entities for the following information from Divera 24/7:

- the last visible alarm.
- the current status of the user.

## Automation Blueprint

You can add a basic automation blueprint here:

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Ffwmarcel%2Fhome-assistant-divera%2Fblob%2Fmain%2Fdivera-blueprint.yaml)

## Help and Contribution

If you find a problem, feel free to report it and I will do my best to help you.
If you have something to contribute, your help is greatly appreciated!
If you want to add a new feature, add a pull request first so we can discuss the details.

## Disclaimer

This custom integration is not officially endorsed or supported by Divera 24/7.
Use it at your own risk and ensure that you comply with all relevant terms of service and privacy policies.

## Star History

<a href="https://star-history.com/#fwmarcel/home-assistant-divera">
  <img src="https://api.star-history.com/svg?repos=fwmarcel/home-assistant-divera&type=Date" alt="Star History Chart" width="100%" />
</a>
