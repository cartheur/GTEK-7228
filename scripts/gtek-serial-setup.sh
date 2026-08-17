#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  gtek-serial-setup.sh [--hwflow] DEVICE

Examples:
  gtek-serial-setup.sh /dev/ttyUSB0
  gtek-serial-setup.sh --hwflow /dev/serial/by-id/usb-FTDI_...

Default mode:
  - 19200 baud
  - 8n1
  - raw mode
  - XON/XOFF enabled
  - hardware flow control disabled
EOF
}

hwflow=0

if [[ $# -eq 0 ]]; then
    usage
    exit 1
fi

if [[ "${1:-}" == "--hwflow" ]]; then
    hwflow=1
    shift
fi

if [[ $# -ne 1 ]]; then
    usage
    exit 1
fi

device=$1

if [[ ! -e "$device" ]]; then
    echo "Device not found: $device" >&2
    exit 1
fi

stty -F "$device" 19200 cs8 -cstopb -parenb raw -echo

if [[ $hwflow -eq 1 ]]; then
    stty -F "$device" -ixon -ixoff crtscts
    echo "Configured $device for 19200 8n1 raw with hardware flow control."
else
    stty -F "$device" ixon ixoff -crtscts
    echo "Configured $device for 19200 8n1 raw with XON/XOFF."
fi

stty -F "$device" -a
