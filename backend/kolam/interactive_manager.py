import json
from datetime import datetime
from .zen_kolam_generator import zen_kolam_generator

class InteractiveManager:
    def __init__(self):
        self.kolam_generator = zen_kolam_generator
        self.pattern_history = []
        self.current_history_index = -1
        self.max_history_size = 20
    
    def add_to_history(self, pattern_data, action_name="Pattern Change"):
        """Add a pattern to the history stack"""
        # Remove any history after current index (for redo functionality)
        if self.current_history_index < len(self.pattern_history) - 1:
            self.pattern_history = self.pattern_history[:self.current_history_index + 1]
        
        # Add new pattern to history
        history_entry = {
            'pattern_data': pattern_data.copy(),
            'action_name': action_name,
            'timestamp': datetime.now().isoformat(),
            'preview_image': self.kolam_generator.generate_kolam_image(pattern_data, (150, 150), include_dots=True)
        }
        
        self.pattern_history.append(history_entry)
        self.current_history_index = len(self.pattern_history) - 1
        
        # Limit history size
        if len(self.pattern_history) > self.max_history_size:
            self.pattern_history.pop(0)
            self.current_history_index -= 1
    
    def undo(self):
        """Undo the last action"""
        if self.current_history_index > 0:
            self.current_history_index -= 1
            return self.pattern_history[self.current_history_index]['pattern_data']
        return None
    
    def redo(self):
        """Redo the last undone action"""
        if self.current_history_index < len(self.pattern_history) - 1:
            self.current_history_index += 1
            return self.pattern_history[self.current_history_index]['pattern_data']
        return None
    
    def get_current_pattern(self):
        """Get the current pattern"""
        if 0 <= self.current_history_index < len(self.pattern_history):
            return self.pattern_history[self.current_history_index]['pattern_data']
        return None
    
    def get_history(self):
        """Get the full history"""
        return self.pattern_history
    
    def get_history_entry(self, index):
        """Get a specific history entry"""
        if 0 <= index < len(self.pattern_history):
            return self.pattern_history[index]
        return None
    
    def can_undo(self):
        """Check if undo is possible"""
        return self.current_history_index > 0
    
    def can_redo(self):
        """Check if redo is possible"""
        return self.current_history_index < len(self.pattern_history) - 1
    
    def clear_history(self):
        """Clear the history"""
        self.pattern_history = []
        self.current_history_index = -1
    
    def generate_preview(self, pattern_data, size=(200, 200), theme='traditional'):
        """Generate a preview image for the pattern"""
        return self.kolam_generator.generate_kolam_image(pattern_data, size, include_dots=True, theme=theme)
    
    def generate_realtime_preview(self, grid_size, theme, customization_options):
        """Generate a real-time preview with current settings"""
        from .customization_manager import customization_manager
        
        # Generate base pattern
        pattern = self.kolam_generator.generate_kolam_1d(grid_size)
        
        # Apply customizations
        customized_pattern = customization_manager.apply_customization(pattern, customization_options)
        
        # Generate preview
        preview_image = self.kolam_generator.generate_kolam_image(customized_pattern, (300, 300), include_dots=True, theme=theme)
        
        return {
            'pattern_data': customized_pattern,
            'preview_image': preview_image
        }

# Global instance
interactive_manager = InteractiveManager()
