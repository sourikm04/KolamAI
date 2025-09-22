"""
Different types of Kolam generators for various traditional South Indian patterns
"""

import numpy as np
import random
import math
from typing import List, Dict, Tuple, Any
from .zen_kolam_generator import zen_kolam_generator

class KolamTypeGenerator:
    """Base class for different kolam type generators"""
    
    def __init__(self):
        self.cell_spacing = 60
    
    def generate_dots_grid(self, size: int) -> List[Dict]:
        """Generate a grid of dots for the kolam"""
        dots = []
        for i in range(size):
            for j in range(size):
                dots.append({
                    'id': f'dot-{i}-{j}',
                    'center': {
                        'x': (j + 1) * self.cell_spacing,
                        'y': (i + 1) * self.cell_spacing
                    },
                    'radius': 3,
                    'color': '#000000',
                    'filled': True
                })
        return dots

class TraditionalKolamGenerator(KolamTypeGenerator):
    """Traditional 1D symmetry kolam generator (current implementation)"""
    
    def generate(self, size: int) -> Dict[str, Any]:
        """Generate traditional kolam using zen-kolam algorithm"""
        return zen_kolam_generator.generate_kolam_1d(size)

class GeometricKolamGenerator(KolamTypeGenerator):
    """Geometric patterns with mathematical precision using grid points"""
    
    def generate(self, size: int) -> Dict[str, Any]:
        """Generate geometric kolam patterns that weave around grid points"""
        dots = self.generate_dots_grid(size)
        curves = []
        
        # Create curved patterns that weave around every dot
        # Create figure-8 patterns around each dot
        for row in range(size):
            for col in range(size):
                dot_x = (col + 1) * self.cell_spacing
                dot_y = (row + 1) * self.cell_spacing
                
                # Create figure-8 loops around each dot
                for direction in range(4):  # 4 directions around each dot
                    angle_offset = direction * math.pi / 2
                    
                    # Create figure-8 pattern
                    figure8_points = []
                    for t in np.linspace(0, 2 * math.pi, 32):
                        # Figure-8 parametric equations
                        radius = 0.4 * self.cell_spacing
                        x_offset = radius * math.sin(t)
                        y_offset = radius * math.sin(2 * t) * 0.5
                        
                        # Rotate based on direction
                        cos_angle = math.cos(angle_offset)
                        sin_angle = math.sin(angle_offset)
                        rotated_x = x_offset * cos_angle - y_offset * sin_angle
                        rotated_y = x_offset * sin_angle + y_offset * cos_angle
                        
                        x = dot_x + rotated_x
                        y = dot_y + rotated_y
                        figure8_points.append({'x': x, 'y': y})
                    
                    curves.append({
                        'id': f'figure8-{row}-{col}-{direction}',
                        'start': figure8_points[0],
                        'end': figure8_points[-1],
                        'curvePoints': figure8_points,
                        'strokeWidth': 2,
                        'color': '#000000'
                    })
        
        # Create connecting curves between adjacent dots
        for row in range(size):
            for col in range(size):
                dot_x = (col + 1) * self.cell_spacing
                dot_y = (row + 1) * self.cell_spacing
                
                # Connect to adjacent dots with curved paths
                for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:  # right, down, diagonal
                    neighbor_row = row + direction[0]
                    neighbor_col = col + direction[1]
                    
                    if 0 <= neighbor_row < size and 0 <= neighbor_col < size:
                        neighbor_x = (neighbor_col + 1) * self.cell_spacing
                        neighbor_y = (neighbor_row + 1) * self.cell_spacing
                        
                        # Create curved connector
                        connector_points = []
                        for t in np.linspace(0, 1, 16):
                            # Interpolate between dots
                            current_x = dot_x + t * (neighbor_x - dot_x)
                            current_y = dot_y + t * (neighbor_y - dot_y)
                            
                            # Add curve variation
                            curve_amplitude = 0.3 * self.cell_spacing
                            curve_frequency = 3
                            curve_x = current_x + curve_amplitude * math.sin(t * math.pi * curve_frequency) * math.cos(math.atan2(neighbor_y - dot_y, neighbor_x - dot_x) + math.pi/2)
                            curve_y = current_y + curve_amplitude * math.sin(t * math.pi * curve_frequency) * math.sin(math.atan2(neighbor_y - dot_y, neighbor_x - dot_x) + math.pi/2)
                            
                            connector_points.append({'x': curve_x, 'y': curve_y})
                        
                        curves.append({
                            'id': f'connector-{row}-{col}-{direction[0]}-{direction[1]}',
                            'start': connector_points[0],
                            'end': connector_points[-1],
                            'curvePoints': connector_points,
                            'strokeWidth': 2,
                            'color': '#000000'
                        })
        
        # Create center spiral pattern
        center_row = size // 2
        center_col = size // 2
        center_x = (center_col + 1) * self.cell_spacing
        center_y = (center_row + 1) * self.cell_spacing
        
        # Create multiple spirals from center
        for spiral in range(3):
            spiral_angle = spiral * 2 * math.pi / 3
            spiral_points = []
            
            for t in np.linspace(0, 2 * math.pi, 40):
                radius = t * (size // 2) * self.cell_spacing * 0.3
                angle = spiral_angle + t * 2
                
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                spiral_points.append({'x': x, 'y': y})
            
            curves.append({
                'id': f'center-spiral-{spiral}',
                'start': spiral_points[0],
                'end': spiral_points[-1],
                'curvePoints': spiral_points,
                'strokeWidth': 2,
                'color': '#000000'
            })
        
        return {
            'id': f'geometric-kolam-{size}x{size}',
            'name': f'Geometric Kolam {size}×{size}',
            'grid': {
                'size': size,
                'cells': [[{
                    'row': i,
                    'col': j,
                    'patternId': 1,
                    'dotCenter': {
                        'x': (j + 1) * self.cell_spacing,
                        'y': (i + 1) * self.cell_spacing
                    }
                } for j in range(size)] for i in range(size)],
                'cellSpacing': self.cell_spacing
            },
            'curves': curves,
            'dots': dots,
            'symmetryType': '2D',
            'dimensions': {
                'width': (size + 1) * self.cell_spacing,
                'height': (size + 1) * self.cell_spacing
            }
        }

class FloralKolamGenerator(KolamTypeGenerator):
    """Floral and nature-inspired kolam patterns using grid points"""
    
    def generate(self, size: int) -> Dict[str, Any]:
        """Generate floral kolam patterns that weave around grid points"""
        dots = self.generate_dots_grid(size)
        curves = []
        
        # Create flower patterns that weave around every dot
        for row in range(size):
            for col in range(size):
                dot_x = (col + 1) * self.cell_spacing
                dot_y = (row + 1) * self.cell_spacing
                
                # Create flower petals around each dot
                num_petals = 6
                for petal in range(num_petals):
                    petal_angle = petal * 2 * math.pi / num_petals
                    petal_points = []
                    
                    # Create curved petal around dot
                    for t in np.linspace(0, 1, 20):
                        # Petal shape using parametric equations
                        petal_radius = 0.5 * self.cell_spacing * t
                        
                        # Create petal curve
                        petal_curve = 0.3 * self.cell_spacing * math.sin(t * math.pi) * math.sin(petal_angle * 2)
                        
                        # Calculate petal position
                        base_x = dot_x + petal_radius * math.cos(petal_angle)
                        base_y = dot_y + petal_radius * math.sin(petal_angle)
                        
                        # Add curve variation
                        curve_x = base_x + petal_curve * math.cos(petal_angle + math.pi/2)
                        curve_y = base_y + petal_curve * math.sin(petal_angle + math.pi/2)
                        
                        petal_points.append({'x': curve_x, 'y': curve_y})
                    
                    curves.append({
                        'id': f'petal-{row}-{col}-{petal}',
                        'start': petal_points[0],
                        'end': petal_points[-1],
                        'curvePoints': petal_points,
                        'strokeWidth': 2,
                        'color': '#000000'
                    })
                
                # Create small loops around each dot
                for loop in range(3):
                    loop_angle = loop * 2 * math.pi / 3
                    loop_points = []
                    
                    for t in np.linspace(0, 1, 12):
                        radius = 0.2 * self.cell_spacing * t
                        angle = loop_angle + t * 2 * math.pi
                        
                        x = dot_x + radius * math.cos(angle)
                        y = dot_y + radius * math.sin(angle)
                        loop_points.append({'x': x, 'y': y})
                    
                    # Close the loop
                    loop_points.append(loop_points[0])
                    
                    curves.append({
                        'id': f'dot-loop-{row}-{col}-{loop}',
                        'start': loop_points[0],
                        'end': loop_points[-1],
                        'curvePoints': loop_points,
                        'strokeWidth': 1,
                        'color': '#000000'
                    })
        
        # Create center flower pattern
        center_row = size // 2
        center_col = size // 2
        center_x = (center_col + 1) * self.cell_spacing
        center_y = (center_row + 1) * self.cell_spacing
        
        # Create large flower from center
        num_center_petals = 8
        for i in range(num_center_petals):
            angle = i * 2 * math.pi / num_center_petals
            petal_points = []
            
            # Create large curved petal from center
            for t in np.linspace(0, 1, 24):
                petal_radius = t * (size // 2) * self.cell_spacing * 0.7
                petal_angle = angle + (t - 0.5) * 0.3
                
                # Add organic curve variation
                curve_variation = 0.3 * self.cell_spacing * math.sin(t * math.pi * 2) * math.sin(angle * 3)
                
                x = center_x + petal_radius * math.cos(petal_angle) + curve_variation * math.cos(petal_angle + math.pi/2)
                y = center_y + petal_radius * math.sin(petal_angle) + curve_variation * math.sin(petal_angle + math.pi/2)
                petal_points.append({'x': x, 'y': y})
            
            curves.append({
                'id': f'center-petal-{i}',
                'start': petal_points[0],
                'end': petal_points[-1],
                'curvePoints': petal_points,
                'strokeWidth': 2,
                'color': '#000000'
            })
        
        # Create connecting vines between dots
        for row in range(size):
            for col in range(size):
                dot_x = (col + 1) * self.cell_spacing
                dot_y = (row + 1) * self.cell_spacing
                
                # Connect to adjacent dots with vine-like curves
                for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    neighbor_row = row + direction[0]
                    neighbor_col = col + direction[1]
                    
                    if 0 <= neighbor_row < size and 0 <= neighbor_col < size:
                        neighbor_x = (neighbor_col + 1) * self.cell_spacing
                        neighbor_y = (neighbor_row + 1) * self.cell_spacing
                        
                        # Create vine-like connector
                        vine_points = []
                        for t in np.linspace(0, 1, 20):
                            # Interpolate between dots
                            current_x = dot_x + t * (neighbor_x - dot_x)
                            current_y = dot_y + t * (neighbor_y - dot_y)
                            
                            # Add vine curve
                            vine_amplitude = 0.4 * self.cell_spacing
                            vine_frequency = 4
                            vine_x = current_x + vine_amplitude * math.sin(t * math.pi * vine_frequency) * math.cos(math.atan2(neighbor_y - dot_y, neighbor_x - dot_x) + math.pi/2)
                            vine_y = current_y + vine_amplitude * math.sin(t * math.pi * vine_frequency) * math.sin(math.atan2(neighbor_y - dot_y, neighbor_x - dot_x) + math.pi/2)
                            
                            vine_points.append({'x': vine_x, 'y': vine_y})
                        
                        curves.append({
                            'id': f'vine-{row}-{col}-{direction[0]}-{direction[1]}',
                            'start': vine_points[0],
                            'end': vine_points[-1],
                            'curvePoints': vine_points,
                            'strokeWidth': 1,
                            'color': '#000000'
                        })
        
        return {
            'id': f'floral-kolam-{size}x{size}',
            'name': f'Floral Kolam {size}×{size}',
            'grid': {
                'size': size,
                'cells': [[{
                    'row': i,
                    'col': j,
                    'patternId': 1,
                    'dotCenter': {
                        'x': (j + 1) * self.cell_spacing,
                        'y': (i + 1) * self.cell_spacing
                    }
                } for j in range(size)] for i in range(size)],
                'cellSpacing': self.cell_spacing
            },
            'curves': curves,
            'dots': dots,
            'symmetryType': '2D',
            'dimensions': {
                'width': (size + 1) * self.cell_spacing,
                'height': (size + 1) * self.cell_spacing
            }
        }

class MandalaKolamGenerator(KolamTypeGenerator):
    """Mandala-style kolam with intricate patterns using grid points"""
    
    def generate(self, size: int) -> Dict[str, Any]:
        """Generate mandala kolam patterns that weave around grid points"""
        dots = self.generate_dots_grid(size)
        curves = []
        
        # Create mandala patterns that weave around every dot
        for row in range(size):
            for col in range(size):
                dot_x = (col + 1) * self.cell_spacing
                dot_y = (row + 1) * self.cell_spacing
                
                # Create concentric circles around each dot
                for circle in range(3):
                    circle_radius = (circle + 1) * 0.2 * self.cell_spacing
                    circle_points = []
                    
                    for t in np.linspace(0, 2 * math.pi, 24):
                        x = dot_x + circle_radius * math.cos(t)
                        y = dot_y + circle_radius * math.sin(t)
                        circle_points.append({'x': x, 'y': y})
                    
                    # Close the circle
                    circle_points.append(circle_points[0])
                    
                    curves.append({
                        'id': f'circle-{row}-{col}-{circle}',
                        'start': circle_points[0],
                        'end': circle_points[-1],
                        'curvePoints': circle_points,
                        'strokeWidth': 2,
                        'color': '#000000'
                    })
                
                # Create lotus petals around each dot
                num_petals = 8
                for petal in range(num_petals):
                    petal_angle = petal * 2 * math.pi / num_petals
                    petal_points = []
                    
                    # Create curved lotus petal
                    for t in np.linspace(0, 1, 16):
                        petal_radius = 0.4 * self.cell_spacing * t
                        angle = petal_angle + (t - 0.5) * 0.2
                        
                        # Add curve variation for organic look
                        curve_variation = 0.2 * self.cell_spacing * math.sin(t * math.pi * 2) * math.sin(petal_angle * 4)
                        
                        x = dot_x + petal_radius * math.cos(angle) + curve_variation * math.cos(angle + math.pi/2)
                        y = dot_y + petal_radius * math.sin(angle) + curve_variation * math.sin(angle + math.pi/2)
                        petal_points.append({'x': x, 'y': y})
                    
                    curves.append({
                        'id': f'lotus-petal-{row}-{col}-{petal}',
                        'start': petal_points[0],
                        'end': petal_points[-1],
                        'curvePoints': petal_points,
                        'strokeWidth': 1,
                        'color': '#000000'
                    })
        
        # Create center mandala pattern
        center_row = size // 2
        center_col = size // 2
        center_x = (center_col + 1) * self.cell_spacing
        center_y = (center_row + 1) * self.cell_spacing
        
        # Create concentric circles from center
        for layer in range(1, (size // 2) + 1):
            layer_radius = layer * 0.3 * self.cell_spacing
            layer_points = []
            
            for t in np.linspace(0, 2 * math.pi, 32):
                x = center_x + layer_radius * math.cos(t)
                y = center_y + layer_radius * math.sin(t)
                layer_points.append({'x': x, 'y': y})
            
            # Close the circle
            layer_points.append(layer_points[0])
            
            curves.append({
                'id': f'center-layer-{layer}',
                'start': layer_points[0],
                'end': layer_points[-1],
                'curvePoints': layer_points,
                'strokeWidth': 2,
                'color': '#000000'
            })
        
        # Create center lotus pattern
        num_center_petals = 12
        for i in range(num_center_petals):
            angle = i * 2 * math.pi / num_center_petals
            lotus_points = []
            
            # Create large lotus petal from center
            for t in np.linspace(0, 1, 20):
                lotus_radius = t * (size // 2) * self.cell_spacing * 0.8
                lotus_angle = angle + (t - 0.5) * 0.2
                
                # Add curve variation for organic look
                curve_variation = 0.3 * self.cell_spacing * math.sin(t * math.pi * 3) * math.sin(angle * 6)
                
                x = center_x + lotus_radius * math.cos(lotus_angle) + curve_variation * math.cos(lotus_angle + math.pi/2)
                y = center_y + lotus_radius * math.sin(lotus_angle) + curve_variation * math.sin(lotus_angle + math.pi/2)
                lotus_points.append({'x': x, 'y': y})
            
            curves.append({
                'id': f'center-lotus-{i}',
                'start': lotus_points[0],
                'end': lotus_points[-1],
                'curvePoints': lotus_points,
                'strokeWidth': 2,
                'color': '#000000'
            })
        
        # Create connecting patterns between dots
        for row in range(size):
            for col in range(size):
                dot_x = (col + 1) * self.cell_spacing
                dot_y = (row + 1) * self.cell_spacing
                
                # Connect to adjacent dots with mandala patterns
                for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    neighbor_row = row + direction[0]
                    neighbor_col = col + direction[1]
                    
                    if 0 <= neighbor_row < size and 0 <= neighbor_col < size:
                        neighbor_x = (neighbor_col + 1) * self.cell_spacing
                        neighbor_y = (neighbor_row + 1) * self.cell_spacing
                        
                        # Create mandala connector
                        connector_points = []
                        for t in np.linspace(0, 1, 16):
                            # Interpolate between dots
                            current_x = dot_x + t * (neighbor_x - dot_x)
                            current_y = dot_y + t * (neighbor_y - dot_y)
                            
                            # Add mandala curve
                            mandala_amplitude = 0.3 * self.cell_spacing
                            mandala_frequency = 6
                            mandala_x = current_x + mandala_amplitude * math.sin(t * math.pi * mandala_frequency) * math.cos(math.atan2(neighbor_y - dot_y, neighbor_x - dot_x) + math.pi/2)
                            mandala_y = current_y + mandala_amplitude * math.sin(t * math.pi * mandala_frequency) * math.sin(math.atan2(neighbor_y - dot_y, neighbor_x - dot_x) + math.pi/2)
                            
                            connector_points.append({'x': mandala_x, 'y': mandala_y})
                        
                        curves.append({
                            'id': f'mandala-connector-{row}-{col}-{direction[0]}-{direction[1]}',
                            'start': connector_points[0],
                            'end': connector_points[-1],
                            'curvePoints': connector_points,
                            'strokeWidth': 1,
                            'color': '#000000'
                        })
        
        return {
            'id': f'mandala-kolam-{size}x{size}',
            'name': f'Mandala Kolam {size}×{size}',
            'grid': {
                'size': size,
                'cells': [[{
                    'row': i,
                    'col': j,
                    'patternId': 1,
                    'dotCenter': {
                        'x': (j + 1) * self.cell_spacing,
                        'y': (i + 1) * self.cell_spacing
                    }
                } for j in range(size)] for i in range(size)],
                'cellSpacing': self.cell_spacing
            },
            'curves': curves,
            'dots': dots,
            'symmetryType': '2D',
            'dimensions': {
                'width': (size + 1) * self.cell_spacing,
                'height': (size + 1) * self.cell_spacing
            }
        }

class SpiralKolamGenerator(KolamTypeGenerator):
    """Spiral-based kolam patterns using grid points"""
    
    def generate(self, size: int) -> Dict[str, Any]:
        """Generate spiral kolam patterns that weave around grid points"""
        dots = self.generate_dots_grid(size)
        curves = []
        
        # Create spiral patterns that weave around every dot
        for row in range(size):
            for col in range(size):
                dot_x = (col + 1) * self.cell_spacing
                dot_y = (row + 1) * self.cell_spacing
                
                # Create multiple spirals around each dot
                for spiral in range(3):  # 3 spirals per dot
                    spiral_angle = spiral * 2 * math.pi / 3
                    spiral_points = []
                    
                    # Create curved spiral around dot
                    for t in np.linspace(0, 2 * math.pi, 32):
                        radius = 0.4 * self.cell_spacing * t / (2 * math.pi)
                        angle = spiral_angle + t * 2
                        
                        # Add curve variation for organic look
                        radius_variation = 0.1 * self.cell_spacing * math.sin(t * 3)
                        current_radius = radius + radius_variation
                        
                        x = dot_x + current_radius * math.cos(angle)
                        y = dot_y + current_radius * math.sin(angle)
                        spiral_points.append({'x': x, 'y': y})
                    
                    curves.append({
                        'id': f'spiral-{row}-{col}-{spiral}',
                        'start': spiral_points[0],
                        'end': spiral_points[-1],
                        'curvePoints': spiral_points,
                        'strokeWidth': 2,
                        'color': '#000000'
                    })
                
                # Create small loops around each dot
                for loop in range(4):
                    loop_angle = loop * math.pi / 2
                    loop_points = []
                    
                    for t in np.linspace(0, 1, 12):
                        radius = 0.2 * self.cell_spacing * t
                        angle = loop_angle + t * math.pi / 2
                        
                        x = dot_x + radius * math.cos(angle)
                        y = dot_y + radius * math.sin(angle)
                        loop_points.append({'x': x, 'y': y})
                    
                    # Close the loop
                    loop_points.append(loop_points[0])
                    
                    curves.append({
                        'id': f'loop-{row}-{col}-{loop}',
                        'start': loop_points[0],
                        'end': loop_points[-1],
                        'curvePoints': loop_points,
                        'strokeWidth': 1,
                        'color': '#000000'
                    })
        
        # Create center spiral pattern
        center_row = size // 2
        center_col = size // 2
        center_x = (center_col + 1) * self.cell_spacing
        center_y = (center_row + 1) * self.cell_spacing
        
        # Create large spirals from center
        num_center_spirals = 6
        for spiral in range(num_center_spirals):
            spiral_angle = spiral * 2 * math.pi / num_center_spirals
            center_spiral_points = []
            
            # Create large curved spiral from center
            for t in np.linspace(0, 2 * math.pi, 40):
                radius = t * (size // 2) * self.cell_spacing * 0.4
                angle = spiral_angle + t * 1.5
                
                # Add curve variation for organic look
                radius_variation = 0.2 * self.cell_spacing * math.sin(t * 4)
                current_radius = radius + radius_variation
                
                x = center_x + current_radius * math.cos(angle)
                y = center_y + current_radius * math.sin(angle)
                center_spiral_points.append({'x': x, 'y': y})
            
            curves.append({
                'id': f'center-spiral-{spiral}',
                'start': center_spiral_points[0],
                'end': center_spiral_points[-1],
                'curvePoints': center_spiral_points,
                'strokeWidth': 2,
                'color': '#000000'
            })
        
        # Create connecting spirals between dots
        for row in range(size):
            for col in range(size):
                dot_x = (col + 1) * self.cell_spacing
                dot_y = (row + 1) * self.cell_spacing
                
                # Connect to adjacent dots with spiral curves
                for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    neighbor_row = row + direction[0]
                    neighbor_col = col + direction[1]
                    
                    if 0 <= neighbor_row < size and 0 <= neighbor_col < size:
                        neighbor_x = (neighbor_col + 1) * self.cell_spacing
                        neighbor_y = (neighbor_row + 1) * self.cell_spacing
                        
                        # Create spiral connector
                        connector_points = []
                        for t in np.linspace(0, 1, 20):
                            # Interpolate between dots
                            current_x = dot_x + t * (neighbor_x - dot_x)
                            current_y = dot_y + t * (neighbor_y - dot_y)
                            
                            # Add spiral curve
                            spiral_amplitude = 0.4 * self.cell_spacing
                            spiral_frequency = 5
                            spiral_x = current_x + spiral_amplitude * math.sin(t * math.pi * spiral_frequency) * math.cos(math.atan2(neighbor_y - dot_y, neighbor_x - dot_x) + math.pi/2)
                            spiral_y = current_y + spiral_amplitude * math.sin(t * math.pi * spiral_frequency) * math.sin(math.atan2(neighbor_y - dot_y, neighbor_x - dot_x) + math.pi/2)
                            
                            connector_points.append({'x': spiral_x, 'y': spiral_y})
                        
                        curves.append({
                            'id': f'spiral-connector-{row}-{col}-{direction[0]}-{direction[1]}',
                            'start': connector_points[0],
                            'end': connector_points[-1],
                            'curvePoints': connector_points,
                            'strokeWidth': 1,
                            'color': '#000000'
                        })
        
        return {
            'id': f'spiral-kolam-{size}x{size}',
            'name': f'Spiral Kolam {size}×{size}',
            'grid': {
                'size': size,
                'cells': [[{
                    'row': i,
                    'col': j,
                    'patternId': 1,
                    'dotCenter': {
                        'x': (j + 1) * self.cell_spacing,
                        'y': (i + 1) * self.cell_spacing
                    }
                } for j in range(size)] for i in range(size)],
                'cellSpacing': self.cell_spacing
            },
            'curves': curves,
            'dots': dots,
            'symmetryType': '2D',
            'dimensions': {
                'width': (size + 1) * self.cell_spacing,
                'height': (size + 1) * self.cell_spacing
            }
        }

class KolamTypeManager:
    """Manager class for different kolam types"""
    
    def __init__(self):
        self.generators = {
            'traditional': TraditionalKolamGenerator(),
            'geometric': GeometricKolamGenerator(),
            'floral': FloralKolamGenerator(),
            'mandala': MandalaKolamGenerator(),
            'spiral': SpiralKolamGenerator()
        }
    
    def get_available_types(self) -> List[Dict[str, str]]:
        """Get list of available kolam types"""
        return [
            {'id': 'traditional', 'name': 'Traditional 1D', 'description': 'Classic South Indian kolam with 1D symmetry'},
            {'id': 'geometric', 'name': 'Geometric', 'description': 'Mathematical patterns with circles and lines'},
            {'id': 'floral', 'name': 'Floral', 'description': 'Nature-inspired flower patterns'},
            {'id': 'mandala', 'name': 'Mandala', 'description': 'Intricate mandala-style designs'},
            {'id': 'spiral', 'name': 'Spiral', 'description': 'Spiral-based patterns'}
        ]
    
    def generate_kolam(self, kolam_type: str, size: int) -> Dict[str, Any]:
        """Generate kolam of specified type"""
        if kolam_type not in self.generators:
            raise ValueError(f"Unknown kolam type: {kolam_type}")
        
        generator = self.generators[kolam_type]
        return generator.generate(size)

# Global instance
kolam_type_manager = KolamTypeManager()
