from .models import KolamTemplate, UserPattern, UserPreferences
from .zen_kolam_generator import zen_kolam_generator
import json

class PatternLibraryManager:
    def __init__(self):
        self.kolam_generator = zen_kolam_generator
    
    def get_templates_by_category(self, category=None):
        """Get templates filtered by category"""
        templates = KolamTemplate.objects.all()
        if category:
            templates = templates.filter(category=category)
        return templates.order_by('-is_featured', 'name')
    
    def get_featured_templates(self):
        """Get featured templates"""
        return KolamTemplate.objects.filter(is_featured=True).order_by('name')
    
    def get_templates_by_difficulty(self, difficulty):
        """Get templates by difficulty level"""
        return KolamTemplate.objects.filter(difficulty=difficulty).order_by('name')
    
    def create_template_from_pattern(self, name, description, category, difficulty, pattern_data, grid_size, is_featured=False):
        """Create a new template from pattern data"""
        # Generate preview image
        preview_image = self.kolam_generator.generate_kolam_image(pattern_data, (200, 200), include_dots=True)
        
        template = KolamTemplate.objects.create(
            name=name,
            description=description,
            category=category,
            difficulty=difficulty,
            pattern_data=pattern_data,
            preview_image=preview_image,
            grid_size=grid_size,
            is_featured=is_featured
        )
        return template
    
    def get_user_patterns(self, user_id=None):
        """Get user patterns"""
        patterns = UserPattern.objects.all()
        if user_id:
            # In a real app, you'd filter by user
            pass
        return patterns.order_by('-created_at')
    
    def save_user_pattern(self, name, pattern_data, grid_size, theme, is_favorite=False, category='generated'):
        """Save a user pattern"""
        # Handle different pattern data formats
        if isinstance(pattern_data, dict):
            # If it's a dict with image data, extract the actual pattern
            if 'image' in pattern_data:
                # For digitized patterns, we might not have the actual pattern data
                # Just store the image data as pattern_data
                actual_pattern_data = pattern_data
            else:
                actual_pattern_data = pattern_data
        else:
            actual_pattern_data = pattern_data
        
        # Generate preview image - handle cases where we might not have full pattern data
        try:
            print(f"🔍 Generating preview for pattern: {name}")
            print(f"🔍 Pattern data type: {type(actual_pattern_data)}")
            
            if isinstance(actual_pattern_data, dict) and 'image' in actual_pattern_data:
                # Use the existing image as preview
                print("🔍 Using existing image as preview")
                preview_image = actual_pattern_data['image']
            elif isinstance(actual_pattern_data, dict) and 'type' in actual_pattern_data and actual_pattern_data['type'] == 'digitized':
                # For digitized patterns, use the image from the pattern data
                print("🔍 Using digitized image as preview")
                preview_image = actual_pattern_data.get('image', '')
            else:
                # For generated patterns, check if we have the proper structure
                if isinstance(actual_pattern_data, dict) and 'dots' in actual_pattern_data and 'curves' in actual_pattern_data:
                    print("🔍 Generating preview from pattern data with dots and curves")
                    # Generate preview from pattern data
                    preview_image = self.kolam_generator.generate_kolam_image(actual_pattern_data, (200, 200), include_dots=True, theme=theme)
                    print(f"🔍 Generated preview image length: {len(preview_image) if preview_image else 0}")
                else:
                    # If pattern data doesn't have the right structure, generate a new pattern for preview
                    print(f"🔍 Pattern data structure: {type(actual_pattern_data)}")
                    if isinstance(actual_pattern_data, dict):
                        print(f"🔍 Pattern data keys: {list(actual_pattern_data.keys())}")
                    
                    print("🔍 Generating new pattern for preview")
                    # Generate a simple pattern for preview
                    temp_pattern = self.kolam_generator.generate_kolam_1d(grid_size)
                    preview_image = self.kolam_generator.generate_kolam_image(temp_pattern, (200, 200), include_dots=True, theme=theme)
                    print(f"🔍 Generated temp preview image length: {len(preview_image) if preview_image else 0}")
        except Exception as e:
            print(f"❌ Warning: Could not generate preview image: {e}")
            import traceback
            traceback.print_exc()
            # Create a simple placeholder or use a default
            preview_image = ""
        
        pattern = UserPattern.objects.create(
            name=name,
            pattern_data=actual_pattern_data,
            preview_image=preview_image,
            grid_size=grid_size,
            theme=theme,
            is_favorite=is_favorite,
            category=category
        )
        return pattern
    
    def update_user_pattern(self, pattern_id, name=None, category=None, is_favorite=None):
        """Update a user pattern"""
        try:
            pattern = UserPattern.objects.get(id=pattern_id)
            
            if name is not None:
                pattern.name = name
            if category is not None:
                pattern.category = category
            if is_favorite is not None:
                pattern.is_favorite = is_favorite
            
            pattern.save()
            return pattern
        except UserPattern.DoesNotExist:
            raise ValueError(f"Pattern with ID {pattern_id} not found")
    
    def delete_user_pattern(self, pattern_id):
        """Delete a user pattern"""
        try:
            pattern = UserPattern.objects.get(id=pattern_id)
            pattern.delete()
            return True
        except UserPattern.DoesNotExist:
            return False
    
    def get_user_preferences(self, user_id=None):
        """Get or create user preferences"""
        preferences, created = UserPreferences.objects.get_or_create(
            defaults={
                'default_theme': 'traditional',
                'default_grid_size': 9,
                'line_thickness': 2,
                'dot_size': 3,
                'pattern_density': 'medium',
                'symmetry_type': 'radial',
                'auto_save': True
            }
        )
        return preferences
    
    def update_user_preferences(self, user_id=None, **kwargs):
        """Update user preferences"""
        preferences = self.get_user_preferences(user_id)
        for key, value in kwargs.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)
        preferences.save()
        return preferences
    
    def initialize_default_templates(self):
        """Initialize the database with default kolam templates"""
        if KolamTemplate.objects.exists():
            return  # Templates already exist
        
        # Create some default templates
        default_templates = [
            {
                'name': 'Simple Daily Kolam',
                'description': 'A simple daily kolam perfect for beginners',
                'category': 'daily',
                'difficulty': 'beginner',
                'grid_size': 5,
                'is_featured': True
            },
            {
                'name': 'Festival Lotus',
                'description': 'Beautiful lotus design for festivals',
                'category': 'festival',
                'difficulty': 'intermediate',
                'grid_size': 7,
                'is_featured': True
            },
            {
                'name': 'Wedding Mandala',
                'description': 'Intricate mandala for wedding ceremonies',
                'category': 'wedding',
                'difficulty': 'advanced',
                'grid_size': 9,
                'is_featured': True
            },
            {
                'name': 'Religious Swastika',
                'description': 'Traditional swastika design',
                'category': 'religious',
                'difficulty': 'beginner',
                'grid_size': 5,
                'is_featured': False
            },
            {
                'name': 'Decorative Spiral',
                'description': 'Elegant spiral pattern for decoration',
                'category': 'decorative',
                'difficulty': 'intermediate',
                'grid_size': 7,
                'is_featured': False
            }
        ]
        
        for template_data in default_templates:
            # Generate a simple pattern for each template
            pattern = self.kolam_generator.generate_kolam_1d(template_data['grid_size'])
            self.create_template_from_pattern(**template_data, pattern_data=pattern)

# Global instance
pattern_library = PatternLibraryManager()
