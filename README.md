# Divera 24/7 Integration for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/fwmarcel/home-assistant-divera?sort=semver&style=for-the-badge&color=green)](https://github.com/fwmarcel/home-assistant-divera/releases/)
[![GitHub Release Date](https://img.shields.io/github/release-date/fwmarcel/home-assistant-divera?style=for-the-badge&color=green)](https://github.com/fwmarcel/home-assistant-divera/releases/)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/fwmarcel/home-assistant-divera/latest/total?style=for-the-badge&label=Downloads)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/fwmarcel/home-assistant-divera?style=for-the-badge)
[![hacs](https://img.shields.io/badge/HACS-Integration-blue.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![BuyMeCoffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge)](https://www.buymeacoffee.com/fwmarcel)

_DISCLAIMER: This project is a private open source project and doesn't have any connection with Divera 24/7_

This integration uses the Divera 24/7 [REST API](https://api.divera247.com/) to retrieve information and display it in
Home Assitant.

## Installation

1. Add this repository to your custom repositories.
2. Install integration via HACS.
3. In the HA UI go to "Configuration" &rarr; "Integrations" click "+" and search for "Divera 24/7".
   _You can repeat this for as many accesskeys of different users as you like._
4. Follow the setup instructions.

## Configuration

The configuration is done via UI.
If you insert your accesskey in the setup dialog.

### How do you get your required access key?

1. Open the settings [website](https://app.divera247.com/account/einstellungen.html) of divera.
2. Change to the debug tab
3. Copy your accesskey

![image](https://user-images.githubusercontent.com/59510296/177019399-29de6824-c149-4949-8421-d0edc69a7126.png)

### Sensor values

This integration allows you to read different values.
For example:

- state
  - id
  - timestamp
- alarm
  - id
  - text
  - date
  - address
  - lat
  - lng
  - groups
  - priority
  - closed
  - new

Some sensor sensors are disabled per default, as they contain a lot of data.

You can enable the ones you like in HA UI under "Configuration" &rarr; "Entities" &rarr; click on the filter icon on the
right &rarr; Check "Show diabled entities" &rarr; Check the ones you like to enable &rarr; Click "ENABLE SELECTED" at
the top &rarr; Confirm the next dialog

The sensor values will be set when the next update is scheduled by Home Assistant.
This is done every minute.

## Automation blueprint

You can add a basic automation blueprint here:

[![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Ffwmarcel%2Fhome-assistant-divera%2Fblob%2Fmain%2Fdivera-blueprint.yaml)

## Help and Contribution

If you find a problem, feel free to report it and I will do my best to help you.
If you have something to contribute, your help is greatly appreciated!
If you want to add a new feature, add a pull request first so we can discuss the details.

## Star History

<a href="https://star-history.com/#fwmarcel/home-assistant-divera">
  <img src="https://api.star-history.com/svg?repos=fwmarcel/home-assistant-divera&type=Date" alt="Star History Chart" width="100%" />
</a>