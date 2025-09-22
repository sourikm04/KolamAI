# kolam/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.aboutUs, name='aboutUs'),
    path('digitize/', views.analyze_kolam, name='analyze_kolam'),
    path('generate/', views.generate_kolam, name='generate_kolam'),
    path('generate-by-type/', views.generate_kolam_by_type, name='generate_kolam_by_type'),
    path('kolam-types/', views.get_kolam_types, name='get_kolam_types'),
    
    # Pattern Library APIs
    path('templates/', views.get_templates, name='get_templates'),
    path('load-template/', views.load_template, name='load_template'),
    
    # User Patterns APIs
    path('user-patterns/', views.get_user_patterns, name='get_user_patterns'),
    path('save-pattern/', views.save_user_pattern, name='save_user_pattern'),
    path('update-pattern/', views.update_user_pattern, name='update_user_pattern'),
    path('delete-pattern/', views.delete_user_pattern, name='delete_user_pattern'),
    
    # Customization APIs
    path('generate-customized/', views.generate_customized_kolam, name='generate_customized_kolam'),
    
    # Interactive Features APIs
    path('add-to-history/', views.add_to_history, name='add_to_history'),
    path('undo/', views.undo_action, name='undo_action'),
    path('redo/', views.redo_action, name='redo_action'),
    path('realtime-preview/', views.generate_realtime_preview, name='generate_realtime_preview'),
    
    # User Preferences APIs
    path('preferences/', views.get_user_preferences, name='get_user_preferences'),
    path('update-preferences/', views.update_user_preferences, name='update_user_preferences'),
]

