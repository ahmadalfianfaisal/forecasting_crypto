#!/bin/bash
# Script untuk mengelola session tmux aplikasi forecasting

case "$1" in
    start)
        echo "Starting tmux sessions..."
        ./start_tmux_sessions.sh
        ;;
    start-all)
        echo "Starting all tmux sessions (app, scheduler, auto retrain)..."
        ./start_all_services.sh
        ;;
    start-retrain)
        echo "Starting automatic retraining session..."
        ./auto_retrain.sh
        ;;
    stop)
        echo "Stopping tmux sessions..."
        tmux kill-session -t forecast-app 2>/dev/null || echo "forecast-app session not found"
        tmux kill-session -t model-scheduler 2>/dev/null || echo "model-scheduler session not found"
        tmux kill-session -t model-retrain-auto 2>/dev/null || echo "model-retrain-auto session not found"
        echo "Sessions stopped."
        ;;
    restart)
        echo "Restarting tmux sessions..."
        tmux kill-session -t forecast-app 2>/dev/null || echo "forecast-app session not found"
        tmux kill-session -t model-scheduler 2>/dev/null || echo "model-scheduler session not found"
        tmux kill-session -t model-retrain-auto 2>/dev/null || echo "model-retrain-auto session not found"
        sleep 2
        ./start_tmux_sessions.sh
        ;;
    restart-all)
        echo "Restarting all tmux sessions (app, scheduler, auto retrain)..."
        tmux kill-session -t forecast-app 2>/dev/null || echo "forecast-app session not found"
        tmux kill-session -t model-scheduler 2>/dev/null || echo "model-scheduler session not found"
        tmux kill-session -t model-retrain-auto 2>/dev/null || echo "model-retrain-auto session not found"
        sleep 2
        ./start_all_services.sh
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
    attach-retrain)
        echo "Attaching to automatic retraining session..."
        tmux attach -t model-retrain-auto
        ;;
    *)
        echo "Usage: $0 {start|start-all|start-retrain|stop|restart|restart-all|status|attach-app|attach-scheduler|attach-retrain}"
        exit 1
        ;;
esac