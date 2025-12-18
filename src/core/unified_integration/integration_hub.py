"""
Integration Hub - Cross-phase communication and coordination

This module provides the central hub for cross-phase communication,
event routing, and coordination between all SynergyMesh phases.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    CRITICAL = 'critical'


class MessageType(Enum):
    """Types of inter-phase messages"""
    REQUEST = 'request'
    RESPONSE = 'response'
    EVENT = 'event'
    NOTIFICATION = 'notification'
    BROADCAST = 'broadcast'


@dataclass
class IntegrationConfig:
    """Configuration for the integration hub"""
    name: str = 'synergymesh-hub'
    max_queue_size: int = 10000
    message_timeout_seconds: int = 30
    enable_logging: bool = True
    enable_metrics: bool = True
    retry_failed_messages: bool = True
    max_retries: int = 3
    broadcast_timeout_seconds: int = 5


@dataclass
class Message:
    """Inter-phase message"""
    id: str
    type: MessageType
    source_phase: int
    target_phase: Optional[int]  # None for broadcasts
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'source_phase': self.source_phase,
            'target_phase': self.target_phase,
            'payload': self.payload,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'ttl_seconds': self.ttl_seconds,
            'metadata': self.metadata
        }


@dataclass
class Subscription:
    """Event subscription"""
    id: str
    phase_id: int
    event_pattern: str  # Pattern to match event types
    handler: Callable
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationHub:
    """
    Integration Hub - 整合中樞
    
    Central hub for cross-phase communication providing:
    - Message routing between phases
    - Event pub/sub system
    - Request/response coordination
    - Broadcast messaging
    - Message queuing and delivery
    """
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        """Initialize the integration hub"""
        self.config = config or IntegrationConfig()
        
        # Message queues per phase
        self._queues: Dict[int, asyncio.Queue] = {}
        
        # Subscriptions
        self._subscriptions: Dict[str, Subscription] = {}
        self._phase_subscriptions: Dict[int, Set[str]] = {}
        
        # Pending requests awaiting responses
        self._pending_requests: Dict[str, asyncio.Future] = {}
        
        # Message handlers per phase
        self._handlers: Dict[int, Callable] = {}
        
        # Metrics
        self._messages_sent = 0
        self._messages_delivered = 0
        self._messages_failed = 0
        
        # State
        self._is_running = False
        self._processor_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """Start the integration hub"""
        if self._is_running:
            return
            
        self._is_running = True
        logger.info("IntegrationHub started")
        
    async def stop(self) -> None:
        """Stop the integration hub"""
        self._is_running = False
        
        # Cancel pending requests
        for future in self._pending_requests.values():
            future.cancel()
        self._pending_requests.clear()
        
        logger.info("IntegrationHub stopped")
        
    def register_phase(self, phase_id: int, handler: Optional[Callable] = None) -> None:
        """
        Register a phase with the hub
        
        Args:
            phase_id: Phase identifier
            handler: Optional message handler for the phase
        """
        if phase_id not in self._queues:
            self._queues[phase_id] = asyncio.Queue(maxsize=self.config.max_queue_size)
            self._phase_subscriptions[phase_id] = set()
            
        if handler:
            self._handlers[phase_id] = handler
            
        logger.debug(f"Phase {phase_id} registered with hub")
        
    def unregister_phase(self, phase_id: int) -> None:
        """Unregister a phase from the hub"""
        self._queues.pop(phase_id, None)
        self._handlers.pop(phase_id, None)
        
        # Remove subscriptions
        sub_ids = self._phase_subscriptions.pop(phase_id, set())
        for sub_id in sub_ids:
            self._subscriptions.pop(sub_id, None)
            
        logger.debug(f"Phase {phase_id} unregistered from hub")
        
    async def send_message(
        self,
        source_phase: int,
        target_phase: int,
        payload: Dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Send a message to another phase
        
        Args:
            source_phase: Source phase ID
            target_phase: Target phase ID
            payload: Message payload
            message_type: Type of message
            priority: Message priority
            correlation_id: Optional correlation ID
            
        Returns:
            Message ID
        """
        message = Message(
            id=str(uuid4()),
            type=message_type,
            source_phase=source_phase,
            target_phase=target_phase,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id
        )
        
        await self._deliver_message(message)
        return message.id
        
    async def send_request(
        self,
        source_phase: int,
        target_phase: int,
        payload: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a request and wait for response
        
        Args:
            source_phase: Source phase ID
            target_phase: Target phase ID
            payload: Request payload
            timeout: Optional timeout in seconds
            
        Returns:
            Response payload
        """
        message = Message(
            id=str(uuid4()),
            type=MessageType.REQUEST,
            source_phase=source_phase,
            target_phase=target_phase,
            payload=payload,
            priority=MessagePriority.NORMAL
        )
        
        # Create future for response
        future = asyncio.Future()
        self._pending_requests[message.id] = future
        
        try:
            await self._deliver_message(message)
            
            timeout_sec = timeout or self.config.message_timeout_seconds
            response = await asyncio.wait_for(future, timeout=timeout_sec)
            return response
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request to phase {target_phase} timed out")
        finally:
            self._pending_requests.pop(message.id, None)
            
    async def send_response(
        self,
        request_id: str,
        source_phase: int,
        payload: Dict[str, Any]
    ) -> None:
        """
        Send a response to a request
        
        Args:
            request_id: Original request ID
            source_phase: Source phase ID
            payload: Response payload
        """
        future = self._pending_requests.get(request_id)
        if future and not future.done():
            future.set_result(payload)
            
    async def broadcast(
        self,
        source_phase: int,
        event_type: str,
        payload: Dict[str, Any]
    ) -> int:
        """
        Broadcast an event to all subscribed phases
        
        Args:
            source_phase: Source phase ID
            event_type: Event type string
            payload: Event payload
            
        Returns:
            Number of phases notified
        """
        message = Message(
            id=str(uuid4()),
            type=MessageType.BROADCAST,
            source_phase=source_phase,
            target_phase=None,
            payload={'event_type': event_type, 'data': payload},
            priority=MessagePriority.NORMAL
        )
        
        notified = 0
        
        # Find matching subscriptions
        for sub in self._subscriptions.values():
            if self._matches_pattern(event_type, sub.event_pattern):
                try:
                    if asyncio.iscoroutinefunction(sub.handler):
                        await sub.handler(message.payload)
                    else:
                        sub.handler(message.payload)
                    notified += 1
                except Exception as e:
                    logger.error(f"Broadcast handler error: {e}")
                    
        self._messages_sent += 1
        return notified
        
    def subscribe(
        self,
        phase_id: int,
        event_pattern: str,
        handler: Callable
    ) -> str:
        """
        Subscribe to events
        
        Args:
            phase_id: Subscribing phase ID
            event_pattern: Pattern to match event types (supports *)
            handler: Event handler function
            
        Returns:
            Subscription ID
        """
        sub_id = str(uuid4())
        
        subscription = Subscription(
            id=sub_id,
            phase_id=phase_id,
            event_pattern=event_pattern,
            handler=handler
        )
        
        self._subscriptions[sub_id] = subscription
        
        if phase_id not in self._phase_subscriptions:
            self._phase_subscriptions[phase_id] = set()
        self._phase_subscriptions[phase_id].add(sub_id)
        
        logger.debug(f"Phase {phase_id} subscribed to '{event_pattern}'")
        return sub_id
        
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events
        
        Returns:
            True if unsubscribed, False if not found
        """
        subscription = self._subscriptions.pop(subscription_id, None)
        if not subscription:
            return False
            
        phase_subs = self._phase_subscriptions.get(subscription.phase_id)
        if phase_subs:
            phase_subs.discard(subscription_id)
            
        return True
        
    async def get_pending_messages(self, phase_id: int) -> List[Message]:
        """Get all pending messages for a phase"""
        queue = self._queues.get(phase_id)
        if not queue:
            return []
            
        messages = []
        while not queue.empty():
            try:
                message = queue.get_nowait()
                messages.append(message)
            except asyncio.QueueEmpty:
                break
                
        return messages
        
    def get_stats(self) -> Dict[str, Any]:
        """Get hub statistics"""
        queue_sizes = {
            phase_id: queue.qsize()
            for phase_id, queue in self._queues.items()
        }
        
        return {
            'registered_phases': len(self._queues),
            'total_subscriptions': len(self._subscriptions),
            'messages_sent': self._messages_sent,
            'messages_delivered': self._messages_delivered,
            'messages_failed': self._messages_failed,
            'pending_requests': len(self._pending_requests),
            'queue_sizes': queue_sizes,
            'is_running': self._is_running
        }
        
    async def _deliver_message(self, message: Message) -> bool:
        """Deliver a message to target phase"""
        self._messages_sent += 1
        
        target = message.target_phase
        if target is None:
            # Broadcast - handled elsewhere
            return True
            
        queue = self._queues.get(target)
        if not queue:
            self._messages_failed += 1
            logger.warning(f"Target phase {target} not registered")
            return False
            
        try:
            await queue.put(message)
            self._messages_delivered += 1
            
            # Invoke handler if registered
            handler = self._handlers.get(target)
            if handler:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
                    
            return True
            
        except asyncio.QueueFull:
            self._messages_failed += 1
            logger.warning(f"Queue full for phase {target}")
            return False
            
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches pattern"""
        if pattern == '*':
            return True
        if pattern.endswith('*'):
            return event_type.startswith(pattern[:-1])
        return event_type == pattern


# Factory function
def create_integration_hub(config: Optional[IntegrationConfig] = None) -> IntegrationHub:
    """Create a new IntegrationHub instance"""
    return IntegrationHub(config)
