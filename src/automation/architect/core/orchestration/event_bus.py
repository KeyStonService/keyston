"""
Event Bus - 事件總線
用於系統內部事件傳遞和通知
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class Event:
    """事件數據類"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str


class EventBus:
    """
    事件總線
    
    提供事件發布/訂閱機制：
    - 事件發布
    - 事件訂閱
    - 事件處理
    """
    
    def __init__(self):
        """初始化事件總線"""
        self._subscribers: Dict[str, List[Callable]] = {}
        logger.info('EventBus initialized')
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        訂閱事件
        
        Args:
            event_type: 事件類型
            handler: 事件處理函數
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f'Subscribed to event: {event_type}')
    
    async def publish(self, event: Event):
        """
        發布事件
        
        Args:
            event: 事件對象
        """
        logger.debug(f'Publishing event: {event.type}')
        
        if event.type in self._subscribers:
            for handler in self._subscribers[event.type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f'Error handling event {event.type}: {e}')
