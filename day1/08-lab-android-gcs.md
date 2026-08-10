# Lab: Android GCS Application Analysis

**Type:** Lab
**Duration:** 60 minutes
**Section:** Day 1 – Ground Control

---

## Objectives

- Extract the GCS application APK from an Android device
- Perform static analysis to identify potential vulnerabilities
- Examine the app's permissions, hardcoded data, and network communication
- Use dynamic analysis to observe the app's runtime behavior

---

## Target Apps

| App | Platform | Drone |
|-----|----------|-------|
| **Solo** | Android | 3DR Solo |
| **Solex** | Android | 3DR Solo |
| **FlyMore** / Specta App | Android | Specta Mini |

We will use the **Solo app** for the Android static analysis lab.

We will use the **Flymore Specta app** for the Android dynamic analysis lab.

---

## The Big Picture (Read This First)

This lab has **two halves**, matching the two analysis styles from Module 07:

1. **Static (Solo app)** — you copy the app off the phone as a `.apk`, unzip/decompile it with **jadx**, and read the code looking for secrets: hardcoded passwords, API keys, drone IP addresses, and the permissions it demands. *You never run the app.*
2. **Dynamic (Specta app)** — you run the app and attack it live. Using **Frida** you dump the running app's memory to your laptop, turn that memory into a giant wordlist, and feed it to **John the Ripper** to crack the drone's root password from Lab 04.

The punchline connects the two days: the app was carrying the drone's secrets the whole time — either sitting in the code (static) or sitting in memory (dynamic).

---

## Phase 1: Enable ADB and Extract the APK


- On the Android device:
- Settings → About Phone → tap Build Number 7 times
- Settings → Developer Options → USB Debugging: ON

On many of the Nexus 6P phones, it is necessary to switch the USB mode
from `Charge this Device` to `Transfer files` 
Find this option in the messages after connecting the phone to a laptop

- Configure USB passthrough for your Kali VM

## Connect the device via USB

```bash
adb devices
# Should show your device

# You may need to allow your laptop to connect
# Check your phone for a permission popup dialog

# List installed packages
adb shell pm list packages | grep -i "solo"

# Get the APK path 
adb shell pm path com.o3dr.solo.android

# Note the unique string in the path

# Pull the APK
adb pull /data/app/com.o3dr.solo.android-<unique_string>/base.apk com.o3dr.solo.apk
```

---

## Phase 2: Static Analysis with Jadx

```bash
# Decompile with Jadx
jadx com.o3dr.solo.android.apk -d -java/
```

- Open in the Jadx GUI for easier navigation
```bash
jadx-gui 
```
- Use the File menu to import the apk by name

- Export the java source
```bash
mkdir com.o3dr.solo.android.apk.java
```
- In the JADX gui, select File > Export Project > Browse > com.o3dr.solo.android.apk.java

## 2a. Review AndroidManifest.xml

In the left panel, open Resources > AndroidManifest.xml

or
```bash
cat com.o3dr.solo.android.apk.java/resources/AndroidManifest.xml
```

Look for:
- All `<uses-permission>` entries — which permissions does the app request?
- `<activity android:exported="true">` — exported components
- `<service android:exported="true">` — exported services
- `<receiver>` elements — broadcast receivers

## 2b. Search for Hardcoded Secrets

Use the search tool on the top left to search for secrets (note the initial 50 hit limit)

or

```bash
# Grep for common secrets in Java source
grep -ri "password\|passwd\|pwd" com.o3dr.solo.android.apk.jadx/sources/ --include="*.java" 
grep -ri "secret\|api_key\|apikey\|token" com.o3dr.solo.android.apk.java/sources/ --include="*.java" 
grep -ri "http://\|https://" com.o3dr.solo.android.apk.java/sources/ --include="*.java" | grep -v "//.*http"

# Check string resources
grep -i "password\|key\|secret" com.o3dr.solo.android.apk.java/resources/res/values/strings.xml
```

## 2c. Examine Network Communication Code

In Jadx GUI, search for:
- `OkHttpClient`
- `HttpURLConnection`
- `Retrofit`
- `Socket`
- `DatagramSocket`

Look at how connections are made: is HTTPS used? Is certificate pinning implemented?

```bash
grep -r "OkHttpClient\|HttpURLConnection\|Retrofit" target-app-java/sources/ --include="*.java" -l
```

## 2d. Find MAVLink or Drone Protocol Code

```bash
grep -r "MAVLink\|mavlink\|14550\|UDP\|DatagramPacket" com.o3dr.solo.android.apk.java/sources/ --include="*.java" 
grep -r -E -o '[0-9]{1,3}(\.[0-9]{1,3}){3}' com.o3dr.solo.android.apk.java
```

---

## Phase 3: APKtool – Resources and Smali

```bash
apktool d target-app.apk -o target-app-decoded/

# Review resources
cat target-app-decoded/res/values/strings.xml
ls target-app-decoded/res/raw/    # Check for embedded files

# Check for embedded config files or certificates
find target-app-decoded/ -name "*.json" -o -name "*.xml" -o -name "*.pem" -o -name "*.cer"
```

---

## Phase 4: Dynamic Analysis with Logcat

While the app is running, observe its log output:

```bash
# Clear existing logs
adb logcat -c

# Watch logs (filter to app's tag)
adb logcat | grep -i "specta\|solex\|drone\|mavlink\|wifi"

# Start the app on the device, connect to the drone, and observe log output
```

**What to look for:**
- Credentials or tokens printed in logs
- Server URLs or endpoints
- Error messages revealing backend infrastructure
- MAVLink packet data

---

## Phase 5: Network Traffic Capture

```bash
# Option A: Route Android traffic through your laptop (proxy)
# Set HTTP proxy on Android: Settings → WiFi → Proxy → Manual
# Host: your laptop IP, Port: 8080
# Start Burp Suite on your laptop on port 8080

# Option B: Capture directly on the drone WiFi
sudo tcpdump -i wlan0 -w gcs-app-traffic.pcap

# Filter to app traffic in Wireshark
wireshark gcs-app-traffic.pcap
```

Look for:
- Unencrypted HTTP requests
- Authentication tokens in headers
- MAVLink UDP packets

---

## Findings Documentation

Fill in this table as you discover items:

| Finding | Location | Evidence | Severity |
|---------|----------|----------|----------|
| | | | |

**Severity guide:**
- **Critical** – remote code execution, authentication bypass
- **High** – credential exposure, unencrypted sensitive data
- **Medium** – information disclosure, excessive permissions
- **Low** – verbose logging, non-sensitive hardcoded strings

---

## Discussion Questions

1. Did the app store any sensitive data in SharedPreferences? Is it encrypted?
2. Does the app enforce HTTPS? Does it validate server certificates?
3. Could you inject a command to the drone by intercepting and modifying the app's network traffic?
4. What would you recommend to the app developer to fix the most critical findings?


## Dynamic Analysis of the Android Specta App
---
*Start the Specta App*
* Connect Phone to Internet WiFi Hot Spot
* Start Solex App
    * Allow permissions
    * You may need to reboot

---
## Start the Frida Server on the Android Device
```bash
# login to the Android device
adb shell
# elevate to super user
su -
# change directories
cd /data/local/tmp
# verify frida-server is present
ls
# start the frida-server
./frida-server &
# verify the server is running
ps -ef | grep -i frida
```

---
## Dump Memory from running Solex app to Laptop

Start the Solex app on the Android device

Then run the following commands

```bash
cd /home/kali/frida
source frida_venv/bin/activate
frida-ps -U | grep -i solex 
# not the Process ID (PID)
cd fridump3
mkdir solex
python3 fridump3.py -r -o solex -u Solex
```
---

## Create a wordlist from the memory dump

**The idea:** when the app runs, the drone's password sits somewhere in its memory as plain text. We just dumped all of that memory to disk. We don't know *which* piece of text is the password — so we treat **every unique string in the dump as a password guess.** `sort -u` collapses the dump to a list of unique strings; that becomes our custom wordlist. Then `john` tries each one against the `shadow` hash we recovered in Lab 04. If the password is anywhere in memory, John will find it.

Save the file to the same directory we saved the passwd file earlier

```bash
cd solex
# look for strings with minimum length of 8 to reduce noise
strings -n 8 *data >> strings.txt
sort -u strings.txt > solex-strings-uniq.txt
cp solex-strings-uniq.txt /home/kali/workshop/apps/john
```
---
## Brute force the root password crack

```bash
cd ~/workshops/apps/john
unshadow passwd shadow > unshadow.txt
john --wordlist=/home/kali/workshop/apps/frida/fridump3/solex/strings.uniq unshadow.txt
```

*Congratulations! You just brute forced the root password*

---

## VSCode
```bash
echo "code code/add-microsoft-repo boolean true" | sudo debconf-set-selections
wget https://update.code.visualstudio.com/1.108.1/linux-deb-x64/stable
mv stable vscode.deb
sudo apt install ./vscode.deb
```


Open apk in jadx, export project into a new directory

```
scan this android code which is being analyzed for a security audit for hardcoded passwords, keys, tokens, and other credentials
```

```copilot
I scanned the Android sources and found multiple likely hardcoded credentials.

Findings:

Hardcoded SSH/password material

SoloApp.java
SoloComp.java
Hardcoded SoloLink/vehicle passwords

DroneKitManager.java
BackgroundRunnerService.java
Hardcoded service/API tokens and keys

BuildConfig.java:
Mapbox access token
Mixpanel token
Parse client key
Takeoff server key
NetworkUtils.java
BackgroundRunnerService.java
Hardcoded SDK developer token

AbstractSpiCall.java
BuildConfig.java
```

```
enumerate the passwords, keys, and tokens explicity in this panel
```

```
Here are the explicit credentials I found in the scanned code:

Passwords

TjSDBkAu in:
SoloApp.java
SoloComp.java

sololink in:
DroneKitManager.java
BackgroundRunnerService.java
API / service tokens and keys

bd02efe84c11b41d11c4644e9b04ad4673deb6df in:
BackgroundRunnerService.java

431055c7bf461cf689453dfca6101d143914c494 in:
NetworkUtils.java
BackgroundRunnerService.java
BuildConfig.java (TAKE_OFF_SERVER_KEY)

470fa2b4ae81cd56ecbcda9735803434cec591fa in:
AbstractSpiCall.java
BuildConfig.java

pk.eyJ1IjoiM2Ryb2JvdGljcyIsImEiOiJkeGcxZ2FJIn0.V5HDBvRkxgYBBJjWweOI1g in:
BuildConfig.java (MAPBOX_ACCESS_TOKEN)

92bc0c9a2c005cfc6fe7d9ca9d6b78d0 in:
BuildConfig.java (MIXPANEL_TOKEN)

l9jVycsLbwfzpU1VaVyieCnsMNRJZGEMFzfMKP7I in:
BuildConfig.java (PARSE_APP_ID)

yuoTdCR6wLnFKejv4DX76KkbepLRUHXp0TUSBOtB in:
BuildConfig.java (PARSE_CLIENT_KEY)
Other notable hardcoded values

10.1.1.1 and 10.1.1.10 are hardcoded IPs, though not credentials
root is a hardcoded username, not a secret but relevant to access control
If you want, I can also format this as a compact audit table with columns for type, value, file, and severity.

MAI-Code-1-Flash • 1x
```