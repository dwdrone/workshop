# Lab: 802.11 Narrow Channel Bandwidth

**Type:** Lab
**Duration:** 60 minutes
**Section:** Day 2 – RF Communications

---

## Objectives

- Observe the 5MHz channel bandwidth in spectrum waterfall with HackRF One
- Observe the failure for wifi tools to see the 5MHz SSID
- Observe the failure to airodump-ng to detect the SSID
- Inspect the OpenWRT configuration for 5MHz
- Run the `iwinfo wlan0 scan` command to detect the SSID

---

## Prerequisites

- Any laptop with a SSH client
- GL.iNet GL-AR300M16-ext
- Target: OpenWRT-DC34 (5 MHz chanbw, channel 1)

---

## The Big Picture (Read This First)

802.11 WiFi is typically found on 2.4 GHz and 5 GHz frequencies. And more recent versions can be found at 6 GHz as well. But it is possible to build WiFi channels with center frequencies far from this common ranges. This makes the WiFi practically unobservable with standard tools.

Another unusual WiFi implmentation of channel bandwidths less than 20MHz wide. While no longer common, 5MHz and 10MHz channel bandwidths were mentioned in some early 802.11 protocol definitions. We can use special wifi chips that enable this feature such as the Atheros chips found in the gl.iNet routers. Once again, using non-standard, but 802.11 compliant configurations, we can effectively 'hide' wifi communications.

---

## Background: WiFi Channel Bandwidth

802.11 channel bandwidth refers to the frequency range that a Wi-Fi channel occupies, with common widths being 20 MHz, 40 MHz, 80 MHz, and 160 MHz. Wider channel widths allow for higher data throughput but can also increase interference in crowded environment. Conversely, narrow channel bandwidths can decrease interface and increase range. This is useful for UAS operations.


---

## Phase 1: Test Setup

The lab instructor will start a pair of gl.inet GL-AR300M16-ext travel routers configured 5MHz channel bandwidth. One is a Access Point and the other is client of that Access Point. A ping should be triggered between the two routers.

```bash
ssh root@192.168.2.1
ping -s 1204 192.168.1.1
```

---
## Phase 2: Search for the Access Point OpenWRT-DC34

### Integrated Wireless Clients

- Use a laptop to search for the OpenWRT-DC34
- Use a phone to search for the OpenWRT-DC34

### Aircrack-ng Scan Tools

```bash
# Scan for available networks
sudo airodump-ng wlan1

# Look for your target:
# BSSID: 94:83:C4:xx:xx:xx
# ESSID: OpenWRT-DC34
# CH: 1
# ENC: WPA2

# Note that the Access Point is not found by airodump-ng.
```

---

## Phase 3: Observe it with Spectrum Scanner


- hackrf one sdr + wifi antenna

- gqrx, or
  - `apt install gqrx-sdr`
- sdrangel

- Select the receiver
- Set the bandwidth 20MHz
- Set the sample rate at 20 sps
- Set the center frequency at 2.412 MHz

--- 

## Phase 4: Observer it with Atheros Chip and iw tools

Use a preconfigured gl.inet travel router

Login to the router. Each router has a unique IP address

```bash
ssh root@192.168.xx.1
```

Examine the `wireless` config file

```bash
cat /etc/config/wireless
```

Examine the `network` config file

```bash
cat /etc/config/network
```

Scan for SSIDs on the 5MHz channel

```bash
iwinfo wlan0 scan
```
---

## Discussion Questions

- Security or Performance
- Is security through obscurity a valid security approach
