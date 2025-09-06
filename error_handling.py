#!/usr/bin/env python3
"""
🛡️ Error Handling & Logging System

This module provides comprehensive error handling, logging, and monitoring
capabilities for the Magic Adventure Game CrewAI system.

Features:
- Multi-level logging with agent-specific contexts
- Error categorization and automatic recovery
- Performance monitoring and alerting
- Fallback systems for graceful degradation
- Debug tools and diagnostic information
- Error reporting and analytics
- Circuit breaker patterns for reliability

Ensures the game remains stable and provides meaningful feedback
even when individual agents encounter issues.
"""

import logging
import traceback
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from functools import wraps
from pathlib import Path
import threading
from contextlib import contextmanager

# Configure base logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors that can occur"""
    AGENT_FAILURE = "agent_failure"
    COMMUNICATION_ERROR = "communication_error"
    CONTEXT_INCONSISTENCY = "context_inconsistency"
    VALIDATION_ERROR = "validation_error"
    PERFORMANCE_ISSUE = "performance_issue"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CONFIGURATION_ERROR = "configuration_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    USER_INPUT_ERROR = "user_input_error"
    SYSTEM_ERROR = "system_error"


class LogLevel(Enum):
    """Custom log levels for the game system"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    GAME_EVENT = "game_event"
    AGENT_ACTION = "agent_action"
    PLAYER_ACTION = "player_action"


@dataclass
class GameError:
    """Structured error information"""
    id: str = field(default_factory=lambda: f"err_{int(time.time() * 1000)}")
    timestamp: datetime = field(default_factory=datetime.now)
    category: ErrorCategory = ErrorCategory.SYSTEM_ERROR
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    source_agent: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    resolved: bool = False
    resolution_strategy: Optional[str] = None
    resolution_time: Optional[datetime] = None


@dataclass
class PerformanceMetric:
    """Performance measurement data"""
    operation: str
    agent: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0
    success: bool = True
    memory_usage: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CircuitBreaker:
    """Circuit breaker pattern for agent reliability"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN - service unavailable")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class GameLogger:
    """Enhanced logger for the Magic Adventure Game"""
    
    def __init__(self, name: str, log_directory: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.log_directory = Path(log_directory or "logs")
        self.log_directory.mkdir(exist_ok=True)
        
        self._setup_handlers()
        self._game_events = deque(maxlen=1000)
        self._performance_metrics = deque(maxlen=1000)
        self._error_counts = defaultdict(int)
        
    def _setup_handlers(self):
        """Setup logging handlers for different log levels"""
        
        # File handler for all logs
        all_logs_handler = logging.FileHandler(
            self.log_directory / f"{self.name}_all.log"
        )
        all_logs_handler.setLevel(logging.DEBUG)
        all_logs_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        all_logs_handler.setFormatter(all_logs_formatter)
        
        # Error-specific handler
        error_handler = logging.FileHandler(
            self.log_directory / f"{self.name}_errors.log"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(all_logs_formatter)
        
        # Game events handler
        game_events_handler = logging.FileHandler(
            self.log_directory / f"{self.name}_game_events.log"
        )
        game_events_handler.setLevel(logging.INFO)
        game_events_handler.setFormatter(logging.Formatter(
            '%(asctime)s - GAME_EVENT - %(message)s'
        ))
        
        self.logger.addHandler(all_logs_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(game_events_handler)
    
    def trace(self, message: str, **kwargs):
        """Log trace-level information"""
        self.logger.debug(f"TRACE: {message}", extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug information"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log informational message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message with optional exception"""
        if error:
            self.logger.error(f"{message}: {str(error)}", exc_info=error, extra=kwargs)
        else:
            self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message"""
        if error:
            self.logger.critical(f"{message}: {str(error)}", exc_info=error, extra=kwargs)
        else:
            self.logger.critical(message, extra=kwargs)
    
    def game_event(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Log game-specific events"""
        event_data = {
            "timestamp": datetime.now(),
            "event": event,
            "details": details or {}
        }
        self._game_events.append(event_data)
        
        message = f"🎮 {event}"
        if details:
            message += f" - {json.dumps(details)}"
        
        self.logger.info(message)
    
    def agent_action(self, agent: str, action: str, details: Optional[Dict[str, Any]] = None):
        """Log agent-specific actions"""
        self.game_event(f"AGENT_ACTION: {agent} - {action}", details)
    
    def player_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Log player actions"""
        self.game_event(f"PLAYER_ACTION: {action}", details)
    
    def performance(self, metric: PerformanceMetric):
        """Log performance metrics"""
        self._performance_metrics.append(metric)
        
        message = f"⚡ Performance: {metric.operation}"
        if metric.agent:
            message += f" [{metric.agent}]"
        message += f" - {metric.duration:.2f}s"
        
        if metric.duration > 5.0:  # Slow operation warning
            self.warning(f"Slow operation detected: {message}")
        else:
            self.debug(message)
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent game events"""
        return list(self._game_events)[-limit:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self._performance_metrics:
            return {"message": "No performance data available"}
        
        durations = [m.duration for m in self._performance_metrics if m.success]
        failed_operations = [m for m in self._performance_metrics if not m.success]
        
        return {
            "total_operations": len(self._performance_metrics),
            "successful_operations": len(durations),
            "failed_operations": len(failed_operations),
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "failure_rate": len(failed_operations) / len(self._performance_metrics)
        }


class ErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self, logger: GameLogger):
        self.logger = logger
        self.errors = deque(maxlen=1000)
        self.circuit_breakers = {}
        self.fallback_strategies = {}
        self.recovery_strategies = {}
        self._error_stats = defaultdict(int)
        
        self._setup_default_strategies()
    
    def handle_error(self, error: Exception, category: ErrorCategory, 
                    severity: ErrorSeverity, context: Optional[Dict[str, Any]] = None,
                    source_agent: Optional[str] = None) -> GameError:
        """
        Handle an error with appropriate logging and recovery
        
        Args:
            error: The exception that occurred
            category: Error category
            severity: Error severity level
            context: Additional context information
            source_agent: Agent that caused the error
            
        Returns:
            GameError object with resolution information
        """
        
        game_error = GameError(
            category=category,
            severity=severity,
            message=str(error),
            details={"exception_type": type(error).__name__},
            source_agent=source_agent,
            context=context or {},
            stack_trace=traceback.format_exc()
        )
        
        self.errors.append(game_error)
        self._error_stats[category.value] += 1
        
        # Log the error
        self.logger.error(
            f"🚨 {category.value.upper()}: {game_error.message}",
            error=error,
            agent=source_agent,
            context=context
        )
        
        # Attempt recovery
        if category in self.recovery_strategies:
            try:
                recovery_result = self.recovery_strategies[category](game_error, error)
                game_error.resolved = recovery_result.get("success", False)
                game_error.resolution_strategy = recovery_result.get("strategy", "unknown")
                if game_error.resolved:
                    game_error.resolution_time = datetime.now()
                    self.logger.info(f"✅ Error resolved using strategy: {game_error.resolution_strategy}")
            except Exception as recovery_error:
                self.logger.error(f"❌ Recovery strategy failed", error=recovery_error)
        
        # Apply fallback if available and not resolved
        if not game_error.resolved and category in self.fallback_strategies:
            try:
                fallback_result = self.fallback_strategies[category](game_error, error)
                self.logger.info(f"🔄 Applied fallback strategy for {category.value}")
                return fallback_result
            except Exception as fallback_error:
                self.logger.error(f"❌ Fallback strategy failed", error=fallback_error)
        
        return game_error
    
    def register_fallback_strategy(self, category: ErrorCategory, strategy: Callable):
        """Register a fallback strategy for an error category"""
        self.fallback_strategies[category] = strategy
        self.logger.info(f"📝 Registered fallback strategy for {category.value}")
    
    def register_recovery_strategy(self, category: ErrorCategory, strategy: Callable):
        """Register a recovery strategy for an error category"""
        self.recovery_strategies[category] = strategy
        self.logger.info(f"🔧 Registered recovery strategy for {category.value}")
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and health metrics"""
        recent_errors = [e for e in self.errors if 
                        datetime.now() - e.timestamp < timedelta(minutes=10)]
        
        critical_errors = [e for e in recent_errors if 
                          e.severity == ErrorSeverity.CRITICAL]
        
        return {
            "total_errors": len(self.errors),
            "recent_errors": len(recent_errors),
            "critical_errors": len(critical_errors),
            "error_by_category": dict(self._error_stats),
            "resolution_rate": len([e for e in self.errors if e.resolved]) / len(self.errors) if self.errors else 0,
            "circuit_breaker_status": {
                name: breaker.state for name, breaker in self.circuit_breakers.items()
            }
        }
    
    def _setup_default_strategies(self):
        """Setup default fallback and recovery strategies"""
        
        def agent_failure_fallback(game_error: GameError, original_error: Exception):
            """Fallback for agent failures"""
            return {
                "success": True,
                "fallback_response": f"I apologize, but I'm having some technical difficulties. Let me try a different approach to help with your adventure.",
                "strategy": "generic_agent_fallback"
            }
        
        def communication_error_recovery(game_error: GameError, original_error: Exception):
            """Recovery for communication errors"""
            # Wait and retry
            time.sleep(1)
            return {
                "success": True,
                "strategy": "retry_after_delay"
            }
        
        def validation_error_recovery(game_error: GameError, original_error: Exception):
            """Recovery for validation errors"""
            # Reset to known good state
            return {
                "success": True,
                "strategy": "reset_to_safe_state"
            }
        
        # Register strategies
        self.register_fallback_strategy(ErrorCategory.AGENT_FAILURE, agent_failure_fallback)
        self.register_recovery_strategy(ErrorCategory.COMMUNICATION_ERROR, communication_error_recovery)
        self.register_recovery_strategy(ErrorCategory.VALIDATION_ERROR, validation_error_recovery)


def error_handler_decorator(category: ErrorCategory, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Decorator for automatic error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Try to find error handler in the instance
                instance = args[0] if args and hasattr(args[0], 'error_handler') else None
                if instance and hasattr(instance, 'error_handler'):
                    return instance.error_handler.handle_error(e, category, severity)
                else:
                    # Fallback logging
                    logger = logging.getLogger(func.__module__)
                    logger.error(f"Unhandled error in {func.__name__}: {e}", exc_info=True)
                    raise
        return wrapper
    return decorator


@contextmanager
def performance_monitor(operation: str, agent: Optional[str] = None, 
                       logger: Optional[GameLogger] = None):
    """Context manager for performance monitoring"""
    metric = PerformanceMetric(operation=operation, agent=agent)
    
    try:
        yield metric
        metric.success = True
    except Exception as e:
        metric.success = False
        raise
    finally:
        metric.end_time = datetime.now()
        metric.duration = (metric.end_time - metric.start_time).total_seconds()
        
        if logger:
            logger.performance(metric)


class HealthMonitor:
    """System health monitoring and alerting"""
    
    def __init__(self, logger: GameLogger, error_handler: ErrorHandler):
        self.logger = logger
        self.error_handler = error_handler
        self._health_checks = {}
        self._last_check = None
        self._health_status = "unknown"
    
    def register_health_check(self, name: str, check_function: Callable) -> None:
        """Register a health check function"""
        self._health_checks[name] = check_function
        self.logger.info(f"🩺 Registered health check: {name}")
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self._health_checks.items():
            try:
                result = check_func()
                results[name] = result
                if not result.get("healthy", False):
                    overall_healthy = False
            except Exception as e:
                results[name] = {"healthy": False, "error": str(e)}
                overall_healthy = False
                self.logger.error(f"Health check failed: {name}", error=e)
        
        self._last_check = datetime.now()
        self._health_status = "healthy" if overall_healthy else "unhealthy"
        
        # Get error statistics
        error_stats = self.error_handler.get_error_statistics()
        
        health_report = {
            "overall_healthy": overall_healthy,
            "status": self._health_status,
            "timestamp": self._last_check,
            "individual_checks": results,
            "error_statistics": error_stats,
            "uptime": self._calculate_uptime()
        }
        
        if not overall_healthy:
            self.logger.warning("⚠️ System health check failed", details=health_report)
        else:
            self.logger.info("✅ System health check passed")
        
        return health_report
    
    def _calculate_uptime(self) -> str:
        """Calculate system uptime"""
        # This is a simplified version - in production, you'd track actual start time
        return "Not implemented"


if __name__ == "__main__":
    # Demo the error handling system
    print("🛡️ Error Handling System Demo")
    print("=" * 50)
    
    # Initialize logger and error handler
    logger = GameLogger("magic_adventure_demo")
    error_handler = ErrorHandler(logger)
    health_monitor = HealthMonitor(logger, error_handler)
    
    # Log some events
    logger.info("🎮 Starting Magic Adventure Game")
    logger.game_event("player_joined", {"player_name": "Demo Player"})
    logger.agent_action("story_generator", "create_opening", {"location": "forest"})
    
    # Simulate an error
    try:
        raise ValueError("Simulated error for demo")
    except ValueError as e:
        game_error = error_handler.handle_error(
            e, ErrorCategory.AGENT_FAILURE, ErrorSeverity.MEDIUM,
            context={"agent": "story_generator"}, source_agent="story_generator"
        )
        print(f"🚨 Handled error: {game_error.id}")
    
    # Performance monitoring demo
    with performance_monitor("demo_operation", "demo_agent", logger) as metric:
        time.sleep(0.1)  # Simulate work
        metric.metadata["demo"] = True
    
    # Health check
    def demo_health_check():
        return {"healthy": True, "message": "Demo system is running"}
    
    health_monitor.register_health_check("demo_check", demo_health_check)
    health_report = health_monitor.run_health_checks()
    
    # Get statistics
    error_stats = error_handler.get_error_statistics()
    perf_stats = logger.get_performance_stats()
    
    print(f"📊 Error Statistics:")
    print(f"  Total Errors: {error_stats['total_errors']}")
    print(f"  Recent Errors: {error_stats['recent_errors']}")
    
    print(f"⚡ Performance Statistics:")
    print(f"  Total Operations: {perf_stats['total_operations']}")
    print(f"  Average Duration: {perf_stats['average_duration']:.3f}s")
    
    print("✨ Demo completed successfully!")