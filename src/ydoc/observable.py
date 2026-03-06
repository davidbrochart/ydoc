"""
Observable pattern implementation for YDoc event system.
Inspired by lib0/observable but simplified for Python.
"""

from typing import Dict, List, Callable, Any, TypeVar, Generic

T = TypeVar('T')


class Observable(Generic[T]):
    """
    Base observable class that can emit events and have listeners.
    """
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def on(self, event_name: str, callback: Callable) -> None:
        """Add an event listener."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)
    
    def off(self, event_name: str, callback: Callable) -> None:
        """Remove an event listener."""
        if event_name in self._listeners:
            try:
                self._listeners[event_name].remove(callback)
            except ValueError:
                pass  # Callback wasn't in the list
    
    def emit(self, event_name: str, *args, **kwargs) -> None:
        """Emit an event to all listeners."""
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args, **kwargs)
    
    def once(self, event_name: str, callback: Callable) -> None:
        """Add a one-time event listener."""
        def wrapper(*args, **kwargs):
            callback(*args, **kwargs)
            self.off(event_name, wrapper)
        self.on(event_name, wrapper)
    
    def remove_all_listeners(self, event_name: str | None = None) -> None:
        """Remove all listeners for an event, or all events if None."""
        if event_name is None:
            self._listeners.clear()
        elif event_name in self._listeners:
            self._listeners[event_name].clear()
    
    def has_listeners(self, event_name: str) -> bool:
        """Check if there are listeners for an event."""
        return event_name in self._listeners and len(self._listeners[event_name]) > 0