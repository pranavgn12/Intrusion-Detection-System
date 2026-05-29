from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

import subprocess
import signal
import time

# =========================================
# FLASK APP
# =========================================

app = Flask(__name__)

# =========================================
# GLOBAL LIVE IDS DATA
# =========================================

live_dashboard_data = {

    "timestamp": "",

    "prediction": "Waiting...",

    "confidence": {

        "Nothing": 0,
        "PortScan": 0,
        "Reconnaissance": 0,
        "SYNFlood": 0,
        "UDPFlood": 0,
        "ICMPFlood": 0,
        "SSHBruteForce": 0,
        "ARPSpoofing": 0
    },

    "features": {}
}

# =========================================
# RUNNING PROCESSES
# =========================================

running_processes = {}

# =========================================
# SCRIPT CONFIGURATION
# =========================================

SCRIPTS = {

    "Reconnaissance": {

        "type": "bash",

        "path": "scripts/rec.sh"
    },

    "ARP Spoofing": {

        "type": "bash",

        "path": "scripts/arpspoof.sh"
    },

    "ICMP Flood": {

        "type": "python",

        "path": "scripts/icmp.py"
    },

    "UDP Flood": {

        "type": "python",

        "path": "scripts/udp.py"
    },

    "SYN Flood": {

        "type": "python",

        "path": "scripts/syn.py"
    },

    "Port Scan": {

        "type": "bash",

        "path": "scripts/port_scan.sh"
    }
}

# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def index():

    return render_template(

        "index.html",

        scripts=SCRIPTS
    )

# =========================================
# RECEIVE LIVE IDS DATA
# =========================================

@app.route(
    "/update_live_data",
    methods=["POST"]
)
def update_live_data():

    global live_dashboard_data

    try:

        data = request.json

        if not data:

            return jsonify({

                "status": "error",

                "message": "No JSON received"
            })

        live_dashboard_data = data

        print("\n====================================")
        print("LIVE IDS UPDATE RECEIVED")
        print("====================================")

        print(
            "Prediction:",
            data.get("prediction")
        )

        print(
            "Timestamp:",
            data.get("timestamp")
        )

        return jsonify({

            "status": "success"
        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)
        })

# =========================================
# SEND LIVE IDS DATA TO FRONTEND
# =========================================

@app.route("/live_data")
def live_data():

    return jsonify(
        live_dashboard_data
    )

# =========================================
# START SCRIPT
# =========================================

@app.route(
    "/start",
    methods=["POST"]
)
def start_script():

    global running_processes

    try:

        data = request.json

        name = data["name"]

        if name not in SCRIPTS:

            return jsonify({

                "status": "error",

                "message": "Unknown script"
            })

        # Already running

        if name in running_processes:

            process = running_processes[name]

            if process.poll() is None:

                return jsonify({

                    "status": "already_running"
                })

            else:

                del running_processes[name]

        script = SCRIPTS[name]

        # =====================================
        # PYTHON SCRIPT
        # =====================================

        if script["type"] == "python":

            process = subprocess.Popen(

                [
                    "sudo",
                    ".venv/bin/python",
                    script["path"]
                ],

                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # =====================================
        # BASH SCRIPT
        # =====================================

        else:

            process = subprocess.Popen(

                [
                    "sudo",
                    "bash",
                    script["path"]
                ],

                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        running_processes[name] = process

        print(
            f"[STARTED] {name}"
        )

        return jsonify({

            "status": "started"
        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)
        })

# =========================================
# STOP SCRIPT
# =========================================

@app.route(
    "/stop",
    methods=["POST"]
)
def stop_script():

    global running_processes

    try:

        data = request.json

        name = data["name"]

        if name not in running_processes:

            return jsonify({

                "status": "not_running"
            })

        process = running_processes[name]

        # =====================================
        # TERMINATE PROCESS
        # =====================================

        process.send_signal(
            signal.SIGTERM
        )

        time.sleep(0.5)

        # Force kill if still alive

        if process.poll() is None:

            process.kill()

        del running_processes[name]

        print(
            f"[STOPPED] {name}"
        )

        return jsonify({

            "status": "stopped"
        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)
        })

# =========================================
# GET RUNNING STATUS
# =========================================

@app.route("/status")
def status():

    active = []

    for name, process in list(
        running_processes.items()
    ):

        if process.poll() is None:

            active.append(name)

        else:

            del running_processes[name]

    return jsonify({

        "running": active
    })

# =========================================
# MAIN
# =========================================

if __name__ == "__main__":

    app.run(

        host="192.168.122.1",

        port=5000,

        debug=False
    )

