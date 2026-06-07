#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

ROUTER_URL = "http://192.168.8.1/cgi-bin/luci"
ROUTER_USER = "root"
PHONE_HOSTS = {"pixel-10-pro"}
WIFI_INTERFACES = ["wlan0", "wlan1", "wlan2"]


def read_router_password():
    for line in Path("/config/secrets.yaml").read_text(errors="ignore").splitlines():
        if ":" in line and line.split(":", 1)[0].strip() == "router_admin_password":
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


def rpc(token, namespace, method, params):
    payload = {"method": method, "params": params, "id": 1}
    data = json.dumps(payload).encode()
    request = urllib.request.Request(
        f"{ROUTER_URL}/rpc/{namespace}?auth={token}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        result = json.loads(response.read().decode() or "null")
    if result.get("error"):
        raise RuntimeError(result["error"])
    return result.get("result")


def main():
    password = read_router_password()
    if not password:
        print("unknown")
        return

    auth_payload = {"method": "login", "params": [ROUTER_USER, password], "id": 1}
    auth_request = urllib.request.Request(
        f"{ROUTER_URL}/rpc/auth",
        data=json.dumps(auth_payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(auth_request, timeout=8) as response:
        token = json.loads(response.read().decode() or "null").get("result")
    if not token:
        print("unknown")
        return

    leases = rpc(token, "sys", "exec", ["cat /tmp/dhcp.leases"]) or ""
    candidate_macs = set()
    for line in leases.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[3].lower() in PHONE_HOSTS:
            candidate_macs.add(parts[1].lower())

    if not candidate_macs:
        print("away")
        return

    assoc_output = []
    for iface in WIFI_INTERFACES:
        assoc_output.append(rpc(token, "sys", "exec", [f"iwinfo {iface} assoclist 2>/dev/null"]) or "")
    associated = "\n".join(assoc_output).lower()

    if any(mac in associated for mac in candidate_macs):
        print("home")
    else:
        print("away")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("unknown")
