from .zen_kolam_generator import zen_kolam_generator
import json

class CustomizationManager:
    def __init__(self):
        self.kolam_generator = zen_kolam_generator
    
    def apply_customization(self, pattern_data, customization_options):
        """Apply customization options to a kolam pattern"""
        # Clone the pattern data
        customized_pattern = pattern_data.copy()
        
        # Apply line thickness
        if 'line_thickness' in customization_options:
            customized_pattern['line_thickness'] = customization_options['line_thickness']
        
        # Apply dot size
        if 'dot_size' in customization_options:
            if 'dots' in customized_pattern:
                for dot in customized_pattern['dots']:
                    dot['radius'] = customization_options['dot_size']
        
        # Apply pattern density
        if 'pattern_density' in customization_options:
            density = customization_options['pattern_density']
            if density == 'sparse':
                # Remove some curves to make it sparser
                if 'curves' in customized_pattern:
                    customized_pattern['curves'] = customized_pattern['curves'][::2]
            elif density == 'dense':
                # Add more curves to make it denser
                if 'curves' in customized_pattern:
                    # Duplicate and slightly modify some curves
                    original_curves = customized_pattern['curves'].copy()
                    for curve in original_curves[::2]:  # Take every other curve
                        new_curve = curve.copy()
                        if 'curvePoints' in new_curve:
                            # Slightly offset the curve points
                            for point in new_curve['curvePoints']:
                                point['x'] += 2
                                point['y'] += 2
                        customized_pattern['curves'].append(new_curve)
        
        # Apply symmetry type
        if 'symmetry_type' in customization_options:
            symmetry = customization_options['symmetry_type']
            if symmetry == 'horizontal':
                customized_pattern = self._apply_horizontal_symmetry(customized_pattern)
            elif symmetry == 'vertical':
                customized_pattern = self._apply_vertical_symmetry(customized_pattern)
            elif symmetry == 'diagonal':
                customized_pattern = self._apply_diagonal_symmetry(customized_pattern)
            # 'radial' is the default, no changes needed
        
        return customized_pattern
    
    def _apply_horizontal_symmetry(self, pattern):
        """Apply horizontal symmetry to the pattern"""
        if 'curves' not in pattern:
            return pattern
        
        new_curves = pattern['curves'].copy()
        center_y = pattern['dimensions']['height'] / 2
        
        for curve in pattern['curves']:
            if 'curvePoints' in curve:
                new_curve = curve.copy()
                new_curve['curvePoints'] = []
                for point in curve['curvePoints']:
                    new_point = point.copy()
                    new_point['y'] = center_y - (point['y'] - center_y)
                    new_curve['curvePoints'].append(new_point)
                new_curves.append(new_curve)
        
        pattern['curves'] = new_curves
        return pattern
    
    def _apply_vertical_symmetry(self, pattern):
        """Apply vertical symmetry to the pattern"""
        if 'curves' not in pattern:
            return pattern
        
        new_curves = pattern['curves'].copy()
        center_x = pattern['dimensions']['width'] / 2
        
        for curve in pattern['curves']:
            if 'curvePoints' in curve:
                new_curve = curve.copy()
                new_curve['curvePoints'] = []
                for point in curve['curvePoints']:
                    new_point = point.copy()
                    new_point['x'] = center_x - (point['x'] - center_x)
                    new_curve['curvePoints'].append(new_point)
                new_curves.append(new_curve)
        
        pattern['curves'] = new_curves
        return pattern
    
    def _apply_diagonal_symmetry(self, pattern):
        """Apply diagonal symmetry to the pattern"""
        if 'curves' not in pattern:
            return pattern
        
        new_curves = pattern['curves'].copy()
        center_x = pattern['dimensions']['width'] / 2
        center_y = pattern['dimensions']['height'] / 2
        
        for curve in pattern['curves']:
            if 'curvePoints' in curve:
                new_curve = curve.copy()
                new_curve['curvePoints'] = []
                for point in curve['curvePoints']:
                    new_point = point.copy()
                    # Reflect across diagonal (swap x and y)
                    new_point['x'] = center_y - (point['y'] - center_y)
                    new_point['y'] = center_x - (point['x'] - center_x)
                    new_curve['curvePoints'].append(new_point)
                new_curves.append(new_curve)
        
        pattern['curves'] = new_curves
        return pattern
    
    def generate_customized_kolam(self, grid_size, theme, customization_options):
        """Generate a kolam with customizations applied"""
        # Generate base pattern
        pattern = self.kolam_generator.generate_kolam_1d(grid_size)
        
        # Apply customizations
        customized_pattern = self.apply_customization(pattern, customization_options)
        
        return customized_pattern

# Global instance
customization_manager = CustomizationManager()
