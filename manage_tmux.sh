#!/bin/bash
# Script untuk mengelola session tmux aplikasi forecasting

case "$1" in
    start)
        echo "Starting tmux sessions..."
        ./start_tmux_sessions.sh
        ;;
    stop)
        echo "Stopping tmux sessions..."
        tmux kill-session -t forecast-app 2>/dev/null || echo "forecast-app session not found"
        tmux kill-session -t model-scheduler 2>/dev/null || echo "model-scheduler session not found"
        echo "Sessions stopped."
        ;;
    restart)
        echo "Restarting tmux sessions..."
        tmux kill-session -t forecast-app 2>/dev/null || echo "forecast-app session not found"
        tmux kill-session -t model-scheduler 2>/dev/null || echo "model-scheduler session not found"
        sleep 2
        ./start_tmux_sessions.sh
        ;;
    status)
        echo "Current tmux sessions:"
        tmux ls
        ;;
    attach-app)
        echo "Attaching to forecast application session..."
        tmux attach -t forecast-app
        ;;
    attach-scheduler)
        echo "Attaching to model scheduler session..."
        tmux attach -t model-scheduler
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|attach-app|attach-scheduler}"
        exit 1
        ;;
esac