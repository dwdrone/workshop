### apt prereqs

General
```
apt -y install build-essential git cmake
```

Specific
```
apt -y install libsdl1.2-dev gr-hackrf gr-osmosdr
```

### Start GNURadio in an Ubuntu 18 VM

- VirtualBox > u18 > Start
- Login to VM as vbox:vbox
- Open the terminal application for the left hand menu
- Type the following command

```
gnuradio-companion
```

### Attach the HackRF One SDR to the VM

- Connect the HackRF One SDR to the laptop with the MicroUSB cable
- In the top menu of the VM display, select Devices > USB > Great Scott Gadgets HackRF One

!img(VirtualBox-USB-HackRF.png)

### Open the GRC Flow Graph NTSC_Video_5GHz_RX.grx

- File > Open > /opt/gits/gr-ntsc-rx/examples > NTSC_Video_5GHz_RX.grx > Open

!img(NTSC-File-Open.png)

### Modify the GRC Flow Graph NTSC_Video_5GHz_RX.grx

- In the main panel, Right click the "UHD: USRP Source" block and select "Disable"
- In the main panel, Right click the "Null Sink" block and select "Disable"
- from the top menu bar, Select the Magnifying Glass 
- In the right hand menu, Select: (no module specified) > Sources > osmocom Source
- Right click the "osmocom Source" menu entry and drag it to the main panel under the UHD: USRP Source block

- Select File > Save As > Name > NTSC_Video_5GHz_RX_HackRF.grc > Save
!img(NTSC-SaveAs-HackRF.png)

### Connect the osmocom Source block to the data flow

- Right click the small blue box on the right side of the "osmocom Source" block and then click on the blue box on the left hand of the "Quadrature Demod" block. A line should connect the two.

!img(NTSC-Connect-Osmocom.png)

### Modify the osmocom Source block

- Double click "osmocom Source"
- modify "Ch0: Frequency (Hz)" to "frequency_carrier"
- modify "Ch0: RF Gain (dB)" to "20"
- modify "Ch0: IF Gain (dB)" to "40"
- modify "Ch0: BB Gain (dB)" to "40"
- modify "Ch0: Bandwidth (Hz)" to "bandwidth"

!img(NTSC-Osmocom-Values.png)

### Modify the Frequency Carrier Variable block

- Double click the "Frequency Carrier" block
- Modify the "frequency_carrier" to "5865e6"

!img(NTSC-Freq-Values.png)

### Run the NTSC Video Flow Graph

- On the top menu bar, Press the Green Arrow to run the flow graph
- The Camera display should pop up in a new window
- When ready, Press the Red X button to stop the flow graph

!img(NTSC-Run.png)

