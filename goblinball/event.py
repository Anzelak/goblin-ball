import time

class GameEvent:
    """Represents a significant game event for logging and visualization"""
    def __init__(self, event_type, data=None):
        self.event_type = event_type  # "move", "block", "score", etc.
        self.data = data or {}        # Event-specific data
        self.timestamp = time.time()
        
    def __str__(self):
        """String representation for logging"""
        if self.event_type == "move":
            return f"{self.data.get('goblin_name')} moved to {self.data.get('target')}"
        elif self.event_type == "block":
            return f"{self.data.get('blocker_name')} blocked {self.data.get('target_name')} with result: {self.data.get('result')}"
        elif self.event_type == "score":
            return f"{self.data.get('goblin_name')} scored {self.data.get('points')} points!"
        elif self.event_type == "injury":
            return f"{self.data.get('goblin_name')} suffered a {self.data.get('injury_type')} injury"
        elif self.event_type == "formation":
            return f"{self.data.get('team_name')} adopted {self.data.get('formation')} formation"
        # Add more event types as needed
        return f"Event: {self.event_type} - {self.data}"
        
    def to_dict(self):
        """Convert event to dictionary for saving/loading"""
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create event from dictionary"""
        event = cls(data["event_type"], data["data"])
        event.timestamp = data["timestamp"]
        return event


class EventManager:
    def __init__(self):
        self.listeners = {}
        self.events = []
        
    def add_listener(self, event_type, callback):
        """Add a callback function for an event type"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        
    def dispatch(self, event):
        """Dispatch an event to all registered listeners"""
        self.events.append(event)
        
        event_type = event.event_type
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                callback(event)
                
    def create_and_dispatch(self, event_type, data=None):
        """Create and dispatch an event in one step"""
        event = GameEvent(event_type, data)
        self.dispatch(event)
        return event
        
    def get_recent_events(self, count=10):
        """Get the most recent events"""
        return self.events[-count:] if self.events else []
        
    def get_events_by_type(self, event_type):
        """Get all events of a specific type"""
        return [e for e in self.events if e.event_type == event_type]
        
    def clear_events(self):
        """Clear all events"""
        self.events = [] 