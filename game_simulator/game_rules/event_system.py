# game_simulator/game_rules/event_system.py
from enum import Enum
from typing import Dict, List, Callable, Any

class EventType(Enum):
    TOWER_CAPTURED = "tower_captured"
    UNIT_SPAWNED = "unit_spawned"
    UNIT_DIED = "unit_died"
    BATTLE_STARTED = "battle_started"
    BATTLE_ENDED = "battle_ended"
    RESOURCES_GAINED = "resources_gained"
    TOWER_UPGRADED = "tower_upgraded"

class GameEvent:
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        self.type = event_type
        self.data = data or {}
        self.timestamp = 0.0  # Will be set by event system

class EventSystem:
    def __init__(self):
        self.listeners: Dict[EventType, List[Callable]] = {}
        self.event_queue: List[GameEvent] = []
        self.current_time = 0.0
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe a callback function to an event type"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe a callback function from an event type"""
        if event_type in self.listeners and callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
    
    def emit(self, event: GameEvent):
        """Emit an event to be processed"""
        event.timestamp = self.current_time
        self.event_queue.append(event)
    
    def process_events(self, game_state):
        """Process all queued events"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            self._handle_event(event, game_state)
    
    def _handle_event(self, event: GameEvent, game_state):
        """Handle a single event by calling all registered listeners"""
        if event.type in self.listeners:
            for callback in self.listeners[event.type]:
                try:
                    callback(event, game_state)
                except Exception as e:
                    print(f"Error handling event {event.type}: {e}")
    
    def update(self, dt, game_state):
        """Update the event system"""
        self.current_time += dt
        self.process_events(game_state)

# Predefined event handlers for common game events
def on_tower_captured(event: GameEvent, game_state):
    """Handle tower capture events"""
    tower_id = event.data.get('tower_id')
    new_owner = event.data.get('new_owner')
    print(f"Tower {tower_id} captured by {new_owner}")

def on_battle_started(event: GameEvent, game_state):
    """Handle battle start events"""
    tower_id = event.data.get('tower_id')
    print(f"Battle started at tower {tower_id}")

def on_unit_died(event: GameEvent, game_state):
    """Handle unit death events"""
    unit_id = event.data.get('unit_id')
    team = event.data.get('team')
    print(f"Unit {unit_id} from team {team} has died")

# Factory function to create a configured event system
def create_game_event_system():
    """Create and configure the game event system with default handlers"""
    event_system = EventSystem()
    
    # Subscribe default handlers
    event_system.subscribe(EventType.TOWER_CAPTURED, on_tower_captured)
    event_system.subscribe(EventType.BATTLE_STARTED, on_battle_started)
    event_system.subscribe(EventType.UNIT_DIED, on_unit_died)
    
    return event_system