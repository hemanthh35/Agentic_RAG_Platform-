from abc import ABC, abstractmethod
from typing import Callable, Any
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger(__name__)

class ProcessingQueue(ABC):
    """Abstract interface for document processing queues to allow modular execution runners."""
    
    @abstractmethod
    def enqueue(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Enqueue a background task."""
        pass


class FastAPIBackgroundQueue(ProcessingQueue):
    """Queue implementation using FastAPI's BackgroundTasks."""
    
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks
        
    def enqueue(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        logger.info(f"Enqueuing task {task.__name__} in FastAPI BackgroundTasks")
        self.background_tasks.add_task(task, *args, **kwargs)
