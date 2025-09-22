from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import KolamDesign, KolamTemplate
from .kolam_analysis import analyze_kolam_image
from .kolam_logic import create_digitized_kolam, create_custom_grid_kolam
from .zen_kolam_generator import zen_kolam_generator
from .kolam_types import kolam_type_manager
from .pattern_library import pattern_library
from .customization_manager import customization_manager
from .interactive_manager import interactive_manager

# View for the home page
def index(request):
    return render(request, 'index.html')

# View for the About Us page
def aboutUs(request):
    return render(request, 'aboutUs.html')

@csrf_exempt
@require_http_methods(["POST"])
def analyze_kolam(request):
    """API endpoint to analyze uploaded kolam image."""
    try:
        if 'kolam_image' not in request.FILES:
            return JsonResponse({'error': 'No image uploaded'}, status=400)
        
        uploaded_image = request.FILES['kolam_image']
        image_bytes = uploaded_image.read()
        theme = request.POST.get('theme', 'traditional')
        
        # Analyze the image
        grid_size, dot_coords, traced_paths, analyzed_image_b64 = analyze_kolam_image(image_bytes)
        
        # Create digitized version with theme
        digitized_image_b64 = create_digitized_kolam(dot_coords, traced_paths, grid_size, grid_size, theme=theme)
        
        # Save to database
        kolam_design = KolamDesign.objects.create(
            original_image=uploaded_image,
            analyzed_image=analyzed_image_b64,
            digitized_image=digitized_image_b64,
            grid_size=grid_size,
            custom_grid_size=grid_size
        )
        
        return JsonResponse({
            'success': True,
            'analyzed_image': analyzed_image_b64,
            'digitized_image': digitized_image_b64,
            'grid_size': grid_size,
            'design_id': kolam_design.id
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_kolam(request):
    """API endpoint to generate custom grid kolam using zen-kolam algorithm."""
    try:
        data = json.loads(request.body)
        dots = int(data.get('dots', 9))
        theme = data.get('theme', 'traditional')
        
        # Validate grid size
        if dots < 3 or dots > 15:
            return JsonResponse({'error': 'Grid size must be between 3 and 15'}, status=400)
        
        # Generate kolam using zen-kolam algorithm
        print(f"🎨 Generating zen-kolam with {dots}x{dots} grid in {theme} theme")
        kolam_pattern = zen_kolam_generator.generate_kolam_1d(dots)
        
        # Convert to image with theme
        generated_image_b64 = zen_kolam_generator.generate_kolam_image(kolam_pattern, (500, 500), theme=theme)
        
        # Save to database
        kolam_design = KolamDesign.objects.create(
            grid_size=dots,
            custom_grid_size=dots,
            digitized_image=generated_image_b64,
            analyzed_image=generated_image_b64  # Store the generated image
        )
        
        return JsonResponse({
            'success': True,
            'generated_image': generated_image_b64,
            'grid_size': dots,
            'design_id': kolam_design.id,
            'pattern_data': kolam_pattern,  # Include the actual pattern data
            'pattern_info': {
                'dots_count': len(kolam_pattern['dots']),
                'curves_count': len(kolam_pattern['curves']),
                'symmetry_type': kolam_pattern['symmetryType']
            }
        })
        
    except Exception as e:
        print(f"Error generating kolam: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_kolam_types(request):
    """API endpoint to get available kolam types."""
    try:
        types = kolam_type_manager.get_available_types()
        return JsonResponse({
            'success': True,
            'types': types
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_kolam_by_type(request):
    """API endpoint to generate kolam by type."""
    try:
        data = json.loads(request.body)
        kolam_type = data.get('type', 'traditional')
        dots = int(data.get('dots', 9))
        
        # Validate grid size
        if dots < 3 or dots > 15:
            return JsonResponse({'error': 'Grid size must be between 3 and 15'}, status=400)
        
        # Validate kolam type
        available_types = [t['id'] for t in kolam_type_manager.get_available_types()]
        if kolam_type not in available_types:
            return JsonResponse({'error': f'Invalid kolam type. Available types: {available_types}'}, status=400)
        
        # Generate kolam by type
        print(f"🎨 Generating {kolam_type} kolam with {dots}x{dots} grid")
        pattern = kolam_type_manager.generate_kolam(kolam_type, dots)
        
        # Convert to image
        generated_image_b64 = zen_kolam_generator.generate_kolam_image(pattern, (500, 500))
        
        # Save to database
        kolam_design = KolamDesign.objects.create(
            grid_size=dots,
            custom_grid_size=dots,
            digitized_image=generated_image_b64,
            analyzed_image=generated_image_b64
        )
        
        return JsonResponse({
            'success': True,
            'generated_image': generated_image_b64,
            'grid_size': dots,
            'design_id': kolam_design.id,
            'kolam_type': kolam_type,
            'pattern_data': pattern,  # Include the actual pattern data
            'pattern_info': {
                'dots_count': len(pattern['dots']),
                'curves_count': len(pattern['curves']),
                'symmetry_type': pattern['symmetryType'],
                'pattern_name': pattern['name']
            }
        })
        
    except Exception as e:
        print(f"Error generating {kolam_type} kolam: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# Pattern Library APIs
@csrf_exempt
@require_http_methods(["GET"])
def get_templates(request):
    """Get kolam templates"""
    try:
        category = request.GET.get('category')
        difficulty = request.GET.get('difficulty')
        featured_only = request.GET.get('featured', 'false').lower() == 'true'
        
        if featured_only:
            templates = pattern_library.get_featured_templates()
        elif category:
            templates = pattern_library.get_templates_by_category(category)
        elif difficulty:
            templates = pattern_library.get_templates_by_difficulty(difficulty)
        else:
            templates = pattern_library.get_templates_by_category()
        
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'difficulty': template.difficulty,
                'grid_size': template.grid_size,
                'preview_image': template.preview_image,
                'is_featured': template.is_featured,
                'created_at': template.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'templates': templates_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def load_template(request):
    """Load a specific template"""
    try:
        data = json.loads(request.body)
        template_id = data.get('template_id')
        
        template = KolamTemplate.objects.get(id=template_id)
        
        return JsonResponse({
            'success': True,
            'template': {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'difficulty': template.difficulty,
                'grid_size': template.grid_size,
                'pattern_data': template.pattern_data,
                'preview_image': template.preview_image
            }
        })
        
    except KolamTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# User Patterns APIs
@csrf_exempt
@require_http_methods(["GET"])
def get_user_patterns(request):
    """Get user patterns"""
    try:
        patterns = pattern_library.get_user_patterns()
        
        patterns_data = []
        for pattern in patterns:
            patterns_data.append({
                'id': pattern.id,
                'name': pattern.name,
                'grid_size': pattern.grid_size,
                'theme': pattern.theme,
                'category': pattern.category,
                'preview_image': pattern.preview_image,
                'is_favorite': pattern.is_favorite,
                'created_at': pattern.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'patterns': patterns_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def save_user_pattern(request):
    """Save a user pattern"""
    try:
        data = json.loads(request.body)
        
        pattern = pattern_library.save_user_pattern(
            name=data.get('name'),
            pattern_data=data.get('pattern_data'),
            grid_size=data.get('grid_size'),
            theme=data.get('theme', 'traditional'),
            is_favorite=data.get('is_favorite', False),
            category=data.get('category', 'generated')
        )
        
        return JsonResponse({
            'success': True,
            'pattern_id': pattern.id,
            'message': 'Pattern saved successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_user_pattern(request):
    """Update a user pattern"""
    try:
        data = json.loads(request.body)
        pattern_id = data.get('pattern_id')
        
        if not pattern_id:
            return JsonResponse({'error': 'Pattern ID is required'}, status=400)
        
        # Update pattern using pattern_library
        updated_pattern = pattern_library.update_user_pattern(
            pattern_id=pattern_id,
            name=data.get('name'),
            category=data.get('category'),
            is_favorite=data.get('is_favorite', False)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Pattern updated successfully',
            'pattern': {
                'id': updated_pattern.id,
                'name': updated_pattern.name,
                'category': updated_pattern.category,
                'is_favorite': updated_pattern.is_favorite
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def delete_user_pattern(request):
    """Delete a user pattern"""
    try:
        data = json.loads(request.body)
        pattern_id = data.get('pattern_id')
        
        if not pattern_id:
            return JsonResponse({'error': 'Pattern ID is required'}, status=400)
        
        # Delete pattern using pattern_library
        success = pattern_library.delete_user_pattern(pattern_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Pattern deleted successfully'
            })
        else:
            return JsonResponse({'error': 'Pattern not found or could not be deleted'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Customization APIs
@csrf_exempt
@require_http_methods(["POST"])
def generate_customized_kolam(request):
    """Generate a kolam with customizations"""
    try:
        data = json.loads(request.body)
        grid_size = int(data.get('grid_size', 9))
        theme = data.get('theme', 'traditional')
        customization_options = data.get('customization_options', {})
        
        # Generate customized kolam
        pattern = customization_manager.generate_customized_kolam(
            grid_size, theme, customization_options
        )
        
        # Generate image
        generated_image_b64 = zen_kolam_generator.generate_kolam_image(pattern, (500, 500), include_dots=True, theme=theme)
        
        return JsonResponse({
            'success': True,
            'pattern_data': pattern,
            'generated_image': generated_image_b64,
            'grid_size': grid_size,
            'theme': theme
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Interactive Features APIs
@csrf_exempt
@require_http_methods(["POST"])
def add_to_history(request):
    """Add pattern to history"""
    try:
        data = json.loads(request.body)
        pattern_data = data.get('pattern_data')
        action_name = data.get('action_name', 'Pattern Change')
        
        interactive_manager.add_to_history(pattern_data, action_name)
        
        return JsonResponse({
            'success': True,
            'can_undo': interactive_manager.can_undo(),
            'can_redo': interactive_manager.can_redo()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def undo_action(request):
    """Undo last action"""
    try:
        pattern_data = interactive_manager.undo()
        
        if pattern_data:
            return JsonResponse({
                'success': True,
                'pattern_data': pattern_data,
                'can_undo': interactive_manager.can_undo(),
                'can_redo': interactive_manager.can_redo()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Nothing to undo'
            })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def redo_action(request):
    """Redo last undone action"""
    try:
        pattern_data = interactive_manager.redo()
        
        if pattern_data:
            return JsonResponse({
                'success': True,
                'pattern_data': pattern_data,
                'can_undo': interactive_manager.can_undo(),
                'can_redo': interactive_manager.can_redo()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Nothing to redo'
            })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_realtime_preview(request):
    """Generate real-time preview"""
    try:
        data = json.loads(request.body)
        grid_size = int(data.get('grid_size', 9))
        theme = data.get('theme', 'traditional')
        customization_options = data.get('customization_options', {})
        
        preview_data = interactive_manager.generate_realtime_preview(
            grid_size, theme, customization_options
        )
        
        return JsonResponse({
            'success': True,
            'pattern_data': preview_data['pattern_data'],
            'preview_image': preview_data['preview_image']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# User Preferences APIs
@csrf_exempt
@require_http_methods(["GET"])
def get_user_preferences(request):
    """Get user preferences"""
    try:
        preferences = pattern_library.get_user_preferences()
        
        return JsonResponse({
            'success': True,
            'preferences': {
                'default_theme': preferences.default_theme,
                'default_grid_size': preferences.default_grid_size,
                'line_thickness': preferences.line_thickness,
                'dot_size': preferences.dot_size,
                'pattern_density': preferences.pattern_density,
                'symmetry_type': preferences.symmetry_type,
                'auto_save': preferences.auto_save
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_user_preferences(request):
    """Update user preferences"""
    try:
        data = json.loads(request.body)
        
        preferences = pattern_library.update_user_preferences(**data)
        
        return JsonResponse({
            'success': True,
            'message': 'Preferences updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
