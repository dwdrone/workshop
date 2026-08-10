#!/bin/bash

# Exit immediately if any command exits with a non-zero status.
set -e

echo "version 20260731-1622 (Reinstall & Rerun Enabled)"

# --- Configuration Variables ---
INSTALL_USER="kali"
INSTALL_GROUP="${INSTALL_USER}"
HOME_DIR="/home/${INSTALL_USER}"
APP_DIR="${HOME_DIR}/workshop/apps"

# --- Argument Parsing & Help Setup ---
REINSTALL_ALL=false
declare -A REINSTALL_COMPONENTS

show_usage() {
    echo "Usage: $0 [--reinstall <all|component_name>]"
    echo ""
    echo "Options:"
    echo "  --reinstall all             Force clean reinstallation of all components"
    echo "  --reinstall <component>     Force clean reinstallation of a specific component"
    echo "  -h, --help                  Show this help message"
    echo ""
    echo "Available Components:"
    echo "  wireshark"
    echo "  jadx"
    echo "  qgc | qgroundcontrol"
    echo "  opendroneid | odid"
    echo "  adb"
    echo "  sdrangel"
    echo "  missionplanner | mp"
    echo "  nrfutil"
    echo "  frida"
    echo "  sikw00f"
    echo "  mavproxy"
    echo "  mono"
    exit 1
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --reinstall)
            if [[ -n "$2" && ! "$2" =~ ^-- ]]; then
                COMPONENT=$(echo "$2" | tr '[:upper:]' '[:lower:]')
                if [ "$COMPONENT" = "all" ]; then
                    REINSTALL_ALL=true
                else
                    # Normalize aliases
                    case "$COMPONENT" in
                        qgroundcontrol) COMPONENT="qgc" ;;
                        odid)           COMPONENT="opendroneid" ;;
                        mp)             COMPONENT="missionplanner" ;;
                    esac
                    REINSTALL_COMPONENTS["$COMPONENT"]=true
                fi
                shift 2
            else
                # Default to 'all' if --reinstall is used without an argument
                REINSTALL_ALL=true
                shift 1
            fi
            ;;
        -h|--help)
            show_usage
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
done

echo "Starting app installation for Dark Wolf workshop for user ${INSTALL_USER} on Kali Rolling"

# --- Helper Functions ---

# Standardized wrapper for apt installations
apt_install() {
    local cmd=("sudo" "TERM=dumb" "DEBIAN_FRONTEND=noninteractive" "apt-get" "install" "-y")
    if [ "$FORCE_REINSTALL_APT" = true ]; then
        cmd+=("--reinstall")
    fi
    echo "--- Installing packages: $* ---"
    "${cmd[@]}" "$@"
}

# Check if an apt package is currently installed
is_pkg_installed() {
    dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "ok installed"
}

# Determine if a component should be reinstalled
should_reinstall() {
    local component=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    # Map aliases
    case "$component" in
        qgroundcontrol) component="qgc" ;;
        odid)           component="opendroneid" ;;
        mp)             component="missionplanner" ;;
    esac
    if [ "$REINSTALL_ALL" = true ] || [ "${REINSTALL_COMPONENTS[$component]}" = true ]; then
        return 0 # true
    fi
    return 1 # false
}

# --- System Preparation ---
echo "--- Checking system package updates ---"
sudo apt-get update

# Install Mono development tools (reinstall if requested)
local_reinstall_mono=false
if should_reinstall "mono"; then
    local_reinstall_mono=true
fi
if [ "$local_reinstall_mono" = true ] || ! is_pkg_installed "mono-devel" || ! is_pkg_installed "mono-libraries-debug"; then
    FORCE_REINSTALL_APT=$local_reinstall_mono apt_install mono-devel mono-libraries-debug
fi

# Install essential development tools & dependencies (only if missing)
essential_pkgs=(git python3 python3-pip python3-venv openjdk-21-jdk curl unzip pipenv)
missing_essentials=()
for pkg in "${essential_pkgs[@]}"; do
    if ! is_pkg_installed "$pkg"; then
        missing_essentials+=("$pkg")
    fi
done
if [ ${#missing_essentials[@]} -gt 0 ]; then
    apt_install "${missing_essentials[@]}"
fi

# Install additional WiFi tools (only if missing)
if ! is_pkg_installed "hcxdumptool" || ! is_pkg_installed "hcxtools"; then
    apt_install hcxdumptool hcxtools
fi

# Install and enable snapd (only if missing)
if ! is_pkg_installed "snapd"; then
    apt_install snapd
    sudo systemctl enable --now snapd
fi

# Install flatpak (only if missing)
if ! is_pkg_installed "flatpak"; then
    apt_install flatpak
    sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
fi

# Ensure the apps directory exists
mkdir -p "${APP_DIR}"
echo "Local apps directory: ${APP_DIR}"

# --- Setup Python applications in individual virtual environments ---

# Helper function to setup a Python application in its own virtual environment
setup_python_app_venv() {
    local app_name=$1
    local pip_packages=$2
    local venv_path="${APP_DIR}/${app_name}/${app_name}_venv"
    local bin_dir="${venv_path}/bin"

    if should_reinstall "${app_name}"; then
        echo "Forcing reinstall of Python virtual env for ${app_name}..."
        sudo rm -rf "${APP_DIR}/${app_name}"
    fi

    if [ ! -d "${venv_path}" ]; then
        mkdir -p "${APP_DIR}/${app_name}"
        python3 -m venv "${venv_path}"
        
        # Install packages within an isolated subshell
        (
            source "${bin_dir}/activate"
            echo "Installing ${pip_packages} into ${app_name}_venv..."
            pip install --no-cache-dir ${pip_packages}
        )

        # Add the venv's bin directory to the user's PATH in .bashrc idempotently
        echo "Adding ${bin_dir} to user's PATH in .bashrc"
        if ! grep -q "${bin_dir}" "${HOME_DIR}/.bashrc" 2>/dev/null; then
            echo "export PATH=\"${bin_dir}:\$PATH\"" | sudo tee -a "${HOME_DIR}/.bashrc" > /dev/null
        fi
        sudo chown "${INSTALL_USER}:${INSTALL_GROUP}" "${HOME_DIR}/.bashrc"

        echo "${app_name} installed in virtual environment."
    else
        echo "${app_name} virtual environment already exists, skipping creation."
    fi
}

# --- Specific Application Installation Functions ---

install_wireshark() {
    echo "--- Installing Wireshark ---"
    local FORCE_REINSTALL_APT=false
    if should_reinstall "wireshark"; then
        FORCE_REINSTALL_APT=true
    fi
    
    if [ "$FORCE_REINSTALL_APT" = true ] || ! is_pkg_installed "wireshark"; then
        echo "wireshark-common wireshark-common/install-setuid boolean true" | sudo debconf-set-selections
        apt_install wireshark
        sudo usermod -aG wireshark "${INSTALL_USER}"
    fi
    
    # Setup plugins directory
    local plugin_dir="${HOME_DIR}/.local/lib/wireshark/plugins"
    mkdir -p "${plugin_dir}"
    
    # Copy Lua plugins if available
    if [ -f "../files/bit32.lua" ]; then
        cp ../files/bit32.lua "${plugin_dir}/"
    fi
    if [ -f "../files/mavlink_2_common.lua" ]; then
        cp ../files/mavlink_2_common.lua "${plugin_dir}/"
    fi
}

install_jadx() {
    echo "--- Installing JADX-GUI ---"
    local FORCE_REINSTALL_APT=false
    if should_reinstall "jadx"; then
        FORCE_REINSTALL_APT=true
    fi
    
    if [ "$FORCE_REINSTALL_APT" = true ] || ! is_pkg_installed "jadx"; then
        apt_install jadx
        echo "JADX-GUI installed. Run 'jadx-gui' from the terminal."
    fi
}

install_qgroundcontrol() {
    echo "--- Installing QGroundControl ---"
    local qgc_version="v4.0.1"
    local qgc_app="QGroundControl.AppImage"
    local qgc_url="https://github.com/mavlink/qgroundcontrol/releases/download/${qgc_version}/${qgc_app}"
    local qgc_dir="${APP_DIR}/QGroundControl"
    
    mkdir -p "${qgc_dir}"
    
    # Move utility scripts into the app directory if they are in current work dir
    [ -f runQGC.sh ] && mv runQGC.sh "${qgc_dir}/"
    [ -f libfuse2.sh ] && mv libfuse2.sh "${qgc_dir}/"
    chmod +x "${qgc_dir}/runQGC.sh" "${qgc_dir}/libfuse2.sh"
    
    # Install dependencies
    if should_reinstall "qgc" || ! is_pkg_installed "gstreamer1.0-plugins-bad" || ! is_pkg_installed "libfuse3-4"; then
        apt_install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl \
                    python3-gi python3-gst-1.0 libfuse3-4 \
                    libxcb-xinerama0 libxkbcommon-x11-0 libxcb-cursor-dev
    fi

    if should_reinstall "qgc"; then
        echo "Forcing reinstall of QGroundControl: removing existing AppImage..."
        sudo rm -f "${qgc_dir}/QGroundControl.AppImage"
    fi

    if [ ! -f "${qgc_dir}/QGroundControl.AppImage" ]; then
        (
            cd "${qgc_dir}"
            sudo ./libfuse2.sh
            
            echo "Downloading ${qgc_app} ${qgc_version} from ${qgc_url}..."
            sudo curl -LO "${qgc_url}"
            if [ ! -f QGroundControl.AppImage ]; then
                sudo mv "${qgc_app}" QGroundControl.AppImage
            fi
            sudo chmod +x QGroundControl.AppImage runQGC.sh
        )
    else
        echo "QGroundControl is already installed, skipping."
    fi
}

install_opendroneid() {
    echo "--- Installing OpenDroneID ---"
    local odid_dir="${APP_DIR}/OpenDroneID"
    
    if should_reinstall "opendroneid"; then
        echo "Forcing reinstall of OpenDroneID..."
        sudo rm -rf "${odid_dir}"
    fi
    
    if [ ! -d "${odid_dir}" ]; then
        mkdir -p "${odid_dir}"
        sudo git clone https://github.com/opendroneid/wireshark-dissector "${odid_dir}"
    else
        echo "OpenDroneID is already installed, skipping."
    fi
}

install_adb() {
    echo "--- Installing adb ---"
    local FORCE_REINSTALL_APT=false
    if should_reinstall "adb"; then
        FORCE_REINSTALL_APT=true
    fi
    if [ "$FORCE_REINSTALL_APT" = true ] || ! is_pkg_installed "adb"; then
        apt_install adb
    fi
}

install_sdrangel() {
    echo "--- Installing sdrangel ---"
    if should_reinstall "sdrangel"; then
        echo "Forcing reinstall of SDRangel..."
        sudo snap remove sdrangel || true
    fi
    
    if ! snap list | grep -q sdrangel; then
        sudo snap install sdrangel
        sudo snap connect sdrangel:raw-usb
        sudo snap connect sdrangel:audio-record
        sudo systemctl enable --now snapd.socket
        sudo systemctl enable --now snapd.apparmor
        sudo snap refresh
    else
        echo "SDRangel is already installed, skipping."
    fi
}

install_missionplanner() {
    echo "--- Installing MissionPlanner ---"
    local mp_dir="${APP_DIR}/MissionPlanner"
    local mp_url="https://firmware.ardupilot.org/Tools/MissionPlanner/MissionPlanner-latest.zip"
    
    if should_reinstall "missionplanner"; then
        echo "Forcing reinstall of MissionPlanner..."
        sudo rm -rf "${mp_dir}"
    fi
    
    if [ ! -d "${mp_dir}" ]; then
        mkdir -p "${mp_dir}"
        (
            cd "${mp_dir}"
            sudo TERM=dumb certmgr -ssl https://autotest.ardupilot.org/LogMessages/Copter/LogMessages.xml.xz
            wget http://ftp.us.debian.org/debian/pool/main/m/mono/ca-certificates-mono_6.12.0.199+dfsg-6_all.deb
            sudo dpkg -i ca-certificates-mono_6.12.0.199+dfsg-6_all.deb
            wget "${mp_url}"
            unzip MissionPlanner-latest.zip
        )
    else
        echo "MissionPlanner is already installed, skipping."
    fi
}

install_nrfutil() {
    echo "--- Installing NRFUtil ---"
    local nrf_dir="${APP_DIR}/nrfutil"
    local nrf_url="https://files.nordicsemi.com/ui/api/v1/download?repoKey=swtools&path=external/nrfutil/executables/x86_64-unknown-linux-gnu/nrfutil&isNativeBrowsing=false"
    local nrf_udev="https://raw.githubusercontent.com/NordicSemiconductor/nrf-udev/refs/heads/main/nrf-udev_1.0.1-all/lib/udev/rules.d/71-nrf.rules"
    
    if should_reinstall "nrfutil"; then
        echo "Forcing reinstall of NRFUtil..."
        sudo rm -rf "${nrf_dir}"
        sudo rm -f "${HOME_DIR}/.local/bin/nrfutil"
    fi
    
    if [ ! -d "${nrf_dir}" ]; then
        mkdir -p "${nrf_dir}"
        (
            cd "${nrf_dir}"
            wget "${nrf_url}" -O nrfutil
            local local_bin_dir="${HOME_DIR}/.local/bin"
            mkdir -p "${local_bin_dir}"
            cp nrfutil "${local_bin_dir}/"
            chown "${INSTALL_USER}:${INSTALL_GROUP}" "${local_bin_dir}" "${local_bin_dir}/nrfutil"
            chmod +x "${local_bin_dir}/nrfutil"
            wget "${nrf_udev}" -O 71-nrf.rules
            sudo cp 71-nrf.rules /etc/udev/rules.d/
            sudo udevadm trigger
        )
    else
        echo "NRFUtil is already installed, skipping."
    fi
}

install_frida() {
    echo "--- Installing Frida ---"
    setup_python_app_venv "frida" "frida-tools==14.8.1"
    (
        cd "${APP_DIR}/frida"
        if [ ! -d "fridump3" ]; then
            git clone https://github.com/rootbsd/fridump3
        fi
    )
}

install_sikw00f() {
    echo "--- Installing Sikw00f ---"
    local needs_clone=false
    if [ ! -d "${APP_DIR}/sikw00f/sikw00f" ]; then
        needs_clone=true
    fi

    setup_python_app_venv "sikw00f" "pymavlink==2.4.42"
    
    if [ "$needs_clone" = true ] || should_reinstall "sikw00f"; then
        (
            cd "${APP_DIR}/sikw00f"
            if [ ! -d "sikw00f" ]; then
                git clone https://github.com/nicholasaleks/sikw00f
            fi
            cd "sikw00f"
            source "../sikw00f_venv/bin/activate"
            pipenv requirements > requirements.txt
            python3 -m pip install -r requirements.txt
            chmod +x sikw00f.py
        )
    fi
}

install_mavproxy() {
    echo "--- Installing MAVProxy ---"
    setup_python_app_venv "mavproxy" "MAVProxy"
    cd "mavproxy"
    source "mavproxy_venv/bin/activate"
    python3 -m pip install setuptools
    python3 -m pip install future pymavlink pyserial
    cd -
}

# --- Execution ---

# Pre-install ownership setup
sudo chown -R "${INSTALL_USER}:${INSTALL_GROUP}" "${APP_DIR}"

# Run installation stages
install_wireshark
install_jadx
install_qgroundcontrol
install_opendroneid
install_adb
install_sdrangel
install_missionplanner
install_nrfutil
install_frida
install_sikw00f
install_mavproxy

# Post-install cleanup
echo "--- Performing final cleanup ---"
sudo apt-get autoremove -y
sudo apt-get clean

# Final ownership reset
sudo chown -R "${INSTALL_USER}:${INSTALL_GROUP}" "${APP_DIR}"

echo "Installation complete!"
echo "---------------------------------------------------------"
