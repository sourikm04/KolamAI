from django.db import models
import json

class KolamDesign(models.Model):
    name = models.CharField(max_length=100, blank=True)
    original_image = models.ImageField(upload_to='kolam_images/')
    analyzed_image = models.TextField(blank=True)  # Base64 encoded
    digitized_image = models.TextField(blank=True)  # Base64 encoded
    custom_grid_image = models.TextField(blank=True)  # Base64 encoded
    grid_size = models.IntegerField(default=5)
    custom_grid_size = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Kolam Design - {self.name or 'Unnamed'}"

class KolamTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('daily', 'Daily'),
        ('festival', 'Festival'),
        ('wedding', 'Wedding'),
        ('religious', 'Religious'),
        ('decorative', 'Decorative'),
        ('traditional', 'Traditional'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='daily')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    pattern_data = models.JSONField()  # Stores the kolam pattern data
    preview_image = models.TextField(blank=True)  # Base64 encoded preview
    grid_size = models.IntegerField(default=5)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class UserPattern(models.Model):
    CATEGORY_CHOICES = [
        ('generated', 'Generated'),
        ('digitized', 'Digitized'),
        ('favorites', 'Favorites'),
    ]
    
    name = models.CharField(max_length=100)
    pattern_data = models.JSONField()  # Stores the kolam pattern data
    preview_image = models.TextField(blank=True)  # Base64 encoded preview
    grid_size = models.IntegerField(default=5)
    theme = models.CharField(max_length=20, default='traditional')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='generated')
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"User Pattern - {self.name}"

class UserPreferences(models.Model):
    default_theme = models.CharField(max_length=20, default='traditional')
    default_grid_size = models.IntegerField(default=9)
    line_thickness = models.IntegerField(default=2)
    dot_size = models.IntegerField(default=3)
    pattern_density = models.CharField(max_length=20, default='medium')
    symmetry_type = models.CharField(max_length=20, default='radial')
    auto_save = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"User Preferences - {self.id}"
