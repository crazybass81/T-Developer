"""
Celery Application Configuration
엔터프라이즈 비동기 작업 큐 설정
"""

import os
from celery import Celery, Task
from celery.signals import task_prerun, task_postrun, task_failure, task_success
from kombu import Exchange, Queue
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
REDIS_BACKEND = os.getenv('REDIS_BACKEND_URL', 'redis://localhost:6379/1')

# Create Celery app
celery_app = Celery(
    'tdeveloper',
    broker=REDIS_URL,
    backend=REDIS_BACKEND,
    include=[
        'src.tasks.project_tasks',
        'src.tasks.email_tasks',
        'src.tasks.data_tasks',
        'src.tasks.agent_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task execution
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'src.tasks.project_tasks.*': {'queue': 'projects'},
        'src.tasks.email_tasks.*': {'queue': 'emails'},
        'src.tasks.data_tasks.*': {'queue': 'data'},
        'src.tasks.agent_tasks.*': {'queue': 'agents'},
    },
    
    # Task behavior
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result backend
    result_expires=86400,  # Results expire after 1 day
    result_compression='gzip',
    
    # Retry configuration
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-old-projects': {
            'task': 'src.tasks.project_tasks.cleanup_old_projects',
            'schedule': timedelta(hours=1),
            'options': {'queue': 'projects'}
        },
        'generate-daily-reports': {
            'task': 'src.tasks.data_tasks.generate_daily_reports',
            'schedule': timedelta(days=1),
            'options': {'queue': 'data'}
        },
        'check-expired-subscriptions': {
            'task': 'src.tasks.data_tasks.check_expired_subscriptions',
            'schedule': timedelta(hours=6),
            'options': {'queue': 'data'}
        },
        'cleanup-expired-sessions': {
            'task': 'src.tasks.data_tasks.cleanup_expired_sessions',
            'schedule': timedelta(hours=1),
            'options': {'queue': 'data'}
        },
    },
    
    # Queue configuration
    task_queues=(
        Queue('projects', Exchange('projects'), routing_key='projects',
              queue_arguments={'x-max-priority': 10}),
        Queue('emails', Exchange('emails'), routing_key='emails',
              queue_arguments={'x-max-priority': 5}),
        Queue('data', Exchange('data'), routing_key='data',
              queue_arguments={'x-max-priority': 3}),
        Queue('agents', Exchange('agents'), routing_key='agents',
              queue_arguments={'x-max-priority': 8}),
    ),
    
    # Worker configuration
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (memory leak prevention)
    worker_disable_rate_limits=False,
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Custom Task class with additional features
class TDeveloperTask(Task):
    """Custom task with retry and error handling"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes max backoff
    retry_jitter = True  # Add randomness to retry delay
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f'Task {self.name}[{task_id}] failed: {exc}')
        # Send alert for critical tasks
        if hasattr(self, 'critical') and self.critical:
            send_task_failure_alert(self.name, task_id, str(exc))
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        logger.warning(f'Task {self.name}[{task_id}] retry: {exc}')
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(f'Task {self.name}[{task_id}] succeeded')

# Set default task class
celery_app.Task = TDeveloperTask

# Signal handlers for monitoring
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Before task execution"""
    logger.info(f'Starting task {task.name}[{task_id}]')
    # Record start time in Redis for monitoring
    import redis
    r = redis.Redis.from_url(REDIS_BACKEND)
    r.hset(f'task:{task_id}', 'started_at', str(timedelta.now()))
    r.expire(f'task:{task_id}', 86400)  # Expire after 1 day

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extra):
    """After task execution"""
    logger.info(f'Completed task {task.name}[{task_id}] with state {state}')
    # Update task metrics
    update_task_metrics(task.name, state)

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra):
    """On task failure"""
    logger.error(f'Task {sender.name}[{task_id}] failed with {exception}')
    # Store failure info for debugging
    store_task_failure(task_id, sender.name, str(exception), str(einfo))

@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """On task success"""
    logger.info(f'Task {sender.name} completed successfully')

# Helper functions
def get_task_info(task_id: str) -> dict:
    """Get task status and result"""
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.successful() else None,
        'error': str(result.info) if result.failed() else None,
        'traceback': result.traceback if result.failed() else None,
    }

def send_task_failure_alert(task_name: str, task_id: str, error: str):
    """Send alert for critical task failures"""
    # Implement alerting (email, Slack, etc.)
    logger.critical(f'CRITICAL: Task {task_name}[{task_id}] failed: {error}')

def update_task_metrics(task_name: str, state: str):
    """Update task execution metrics"""
    import redis
    r = redis.Redis.from_url(REDIS_BACKEND)
    
    # Increment counters
    r.hincrby('task_metrics', f'{task_name}:total', 1)
    r.hincrby('task_metrics', f'{task_name}:{state}', 1)
    
    # Update last execution time
    r.hset('task_metrics', f'{task_name}:last_execution', str(timedelta.now()))

def store_task_failure(task_id: str, task_name: str, error: str, traceback: str):
    """Store task failure information"""
    import redis
    import json
    r = redis.Redis.from_url(REDIS_BACKEND)
    
    failure_info = {
        'task_id': task_id,
        'task_name': task_name,
        'error': error,
        'traceback': traceback,
        'timestamp': str(timedelta.now())
    }
    
    # Store in Redis with expiry
    r.setex(
        f'task_failure:{task_id}',
        86400 * 7,  # Keep for 7 days
        json.dumps(failure_info)
    )
    
    # Add to failure list
    r.lpush('task_failures', task_id)
    r.ltrim('task_failures', 0, 999)  # Keep last 1000 failures

# Import after app creation to avoid circular imports
from datetime import datetime as timedelta