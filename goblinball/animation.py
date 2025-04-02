class Animation:
    """Represents an animation sequence for visualization"""
    def __init__(self, type, source=None, target=None, result=None, duration=30):
        self.type = type  # "move", "block", "knockdown", "score", etc.
        self.source = source  # Source goblin
        self.target = target  # Target position or goblin
        self.result = result  # Outcome
        self.duration = duration  # In frames
        self.frame = 0  # Current frame
        self.complete = False
    
    def update(self):
        """Update the animation frame counter"""
        self.frame += 1
        if self.frame >= self.duration:
            self.complete = True
    
    def is_complete(self):
        """Check if the animation is complete"""
        return self.complete
        
    def get_progress(self):
        """Get animation progress as a value between 0.0 and 1.0"""
        return min(1.0, self.frame / self.duration)
        
class AnimationManager:
    """Manages a queue of animations"""
    def __init__(self):
        self.animations = []
        self.active_animation = None
        self.paused = False
        
    def add_animation(self, animation_type, source=None, target=None, result=None, duration=30):
        """Add a new animation to the queue"""
        animation = Animation(animation_type, source, target, result, duration)
        self.animations.append(animation)
        
        # If no active animation, start this one
        if not self.active_animation:
            self.active_animation = self.animations.pop(0)
            
    def update(self):
        """Update animations"""
        if self.paused or not self.active_animation:
            return
            
        self.active_animation.update()
        
        if self.active_animation.is_complete():
            # Move to next animation
            if self.animations:
                self.active_animation = self.animations.pop(0)
            else:
                self.active_animation = None
                
    def clear(self):
        """Clear all animations"""
        self.animations = []
        self.active_animation = None
        
    def is_complete(self):
        """Check if all animations are complete"""
        return self.active_animation is None and not self.animations
        
    def set_paused(self, paused):
        """Pause or unpause animations"""
        self.paused = paused
        
    def get_active_animation(self):
        """Get the currently active animation"""
        return self.active_animation
        
    def get_queue_size(self):
        """Get the number of queued animations"""
        return len(self.animations) 