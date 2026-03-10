import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.models.model_trainer import train_all_models
import atexit
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelRetrainScheduler:
    def __init__(self, use_expanding_window: bool = False):
        self.use_expanding_window = use_expanding_window
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # Schedule the retraining job to run daily at 00:00 UTC
        self.scheduler.add_job(
            func=self.retrain_models,
            trigger=CronTrigger(hour=0, minute=0, timezone='UTC'),  # Daily at 00:00 UTC
            id='daily_retrain_job',
            name='Daily model retraining',
            replace_existing=True
        )

        # Also run once when the scheduler starts (optional)
        # Uncomment the next line if you want to run immediately when starting
        # self.scheduler.add_job(self.retrain_models, 'date', run_date=datetime.now(), id='initial_run')

        logger.info(f"Scheduled daily model retraining at 00:00 UTC (expanding window: {use_expanding_window})")

        # Shut down the scheduler when exiting the app
        atexit.register(lambda: self.shutdown())

    def retrain_models(self):
        """Retrain all models and log the results"""
        logger.info(f"Starting scheduled model retraining (expanding window: {self.use_expanding_window})...")
        results = train_all_models(use_expanding_window=self.use_expanding_window)

        for ticker, success in results.items():
            if success:
                logger.info(f"Successfully retrained model for {ticker}")
            else:
                logger.error(f"Failed to retrain model for {ticker}")

        logger.info("Completed scheduled model retraining")

    def shutdown(self):
        """Shut down the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shut down")