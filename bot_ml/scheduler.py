from apscheduler.schedulers.blocking import BlockingScheduler
from bot_ml.main import run_spider

scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

def job():
    run_spider("Vinil Rock")  # Pode ser alterado pela API

scheduler.add_job(job, 'cron', day_of_week='mon-sat', hour='21-23', minute='5,15,25,35,45,55')
scheduler.start()
