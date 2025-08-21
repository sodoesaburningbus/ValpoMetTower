#!/bin/bash
### Written by ChatGPT


# ==== CONFIG ====
SCRIPT="rapid_retrieve_data.py"
PYTHON="/miniforge3/envs/main/bin/python3"
PYTHON_PID_FILE="/tmp/python_job.pid"
PID_FILE="./watchdog.pid"
LOG_FILE="./watchdog.log"
# ================

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Already running (PID $(cat $PID_FILE))"
        exit 1
    fi

    echo "Starting run_tower_feed.sh..."
    (
        # Trap cleanup inside subshell
        trap "rm -f $PID_FILE; exit 0" SIGINT SIGTERM

        trap "rm -f $PYTHON_PID_FILE; exit 0" SIGINT SIGTERM

        echo $$ > "$PID_FILE"
        while true; do
            echo "[$(date)] Starting $SCRIPT..." | tee -a "$LOG_FILE"
            $PYTHON "$SCRIPT" & PY_PID=$!
            echo $PY_PID > "$PYTHON_PID_FILE"

            wait $PY_PID
            EXIT_CODE=$?
            echo "[$(date)] Script exited with code $EXIT_CODE. Restarting in 5 seconds..." | tee -a "$LOG_FILE"
            sleep 5
        done
    ) &
    echo "Started watchdog with PID $!"
}

stop() {
    if [ -f "$PYTHON_PID_FILE" ]; then
        PY_PID=$(cat "$PYTHON_PID_FILE")
        echo "Stopping Python process (PID $PY_PID)..."
        kill -9 "$PY_PID" 2>/dev/null
    fi

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "Stopping watchdog (PID $PID)..."
        kill -9 "$PID" 2>/dev/null
        echo "Stopped."
    else
        echo "Not running."
    fi
}

status() {

    if [ -f "$PYTHON_PID_FILE" ] && kill -0 $(cat "$PYTHON_PID_FILE") 2>/dev/null; then
        echo "Python job running (PID $(cat $PYTHON_PID_FILE))"
    else
        echo "Python job not running"
    fi
  

    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Watchdog running (PID $(cat $PID_FILE))"
    else
        echo "Not running."
    fi
}

case "$1" in
    start) start ;;
    stop) stop ;;
    status) status ;;
    restart) stop; start ;;
    *) echo "Usage: $0 {start|stop|status|restart}" ;;
esac
