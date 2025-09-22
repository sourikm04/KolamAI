"""
Zen Kolam Generator - Python implementation of the traditional South Indian kolam generation algorithm
Based on the TypeScript implementation from zen-kolam project
"""

import numpy as np
import random
from typing import List, Dict, Tuple, Any
from PIL import Image, ImageDraw
import io
import base64
import json
import os

class ZenKolamGenerator:
    """Traditional South Indian kolam pattern generator using mathematical algorithms"""
    
    # Core constants for kolam generation (from original MATLAB algorithm)
    PT_DN = [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1]
    PT_RT = [0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1]
    
    # Mate points for connectivity rules
    MATE_PT_DN = {
        1: [2, 3, 5, 6, 9, 10, 12],
        2: [4, 7, 8, 11, 13, 14, 15, 16]
    }
    
    MATE_PT_RT = {
        1: [2, 3, 4, 6, 7, 11, 13],
        2: [5, 8, 9, 10, 12, 14, 15, 16]
    }
    
    # Symmetry transformations
    H_INV = [1, 2, 5, 4, 3, 9, 8, 7, 6, 10, 11, 12, 15, 14, 13, 16]
    V_INV = [1, 4, 3, 2, 5, 7, 6, 9, 8, 10, 11, 14, 13, 12, 15, 16]
    
    def __init__(self):
        self.cell_spacing = 60
        self.patterns_data = self._load_patterns_data()
    
    def _load_patterns_data(self) -> Dict:
        """Load kolam patterns data from JSON file.

        The repository stores the canonical dataset at `generator_kolam/src/data/kolamPatternsData.json`.
        Older paths (like `zen-kolam/src/data/...`) may not exist locally, so we try a list of
        candidate locations relative to this file.
        """
        base_dir = os.path.dirname(__file__)
        candidates = [
            # Current repo layout
            os.path.join(base_dir, '..', '..', 'generator_kolam', 'src', 'data', 'kolamPatternsData.json'),
            # Legacy/alternative layout that might exist in some checkouts
            os.path.join(base_dir, '..', 'zen-kolam', 'src', 'data', 'kolamPatternsData.json'),
        ]

        for path in candidates:
            try:
                abs_path = os.path.abspath(path)
                if os.path.exists(abs_path):
                    with open(abs_path, 'r') as f:
                        return json.load(f)
            except Exception as e:
                print(f"Warning: Failed reading kolam patterns from {abs_path}: {e}")

        # Fallback to basic patterns if nothing found
        print("Warning: Using built-in basic patterns; dataset file not found.")
        return self._create_basic_patterns()
    
    def _create_basic_patterns(self) -> Dict:
        """Create basic pattern data as fallback"""
        return {
            "patterns": [
                {
                    "id": i,
                    "points": [
                        {"x": 0.25, "y": 0},
                        {"x": 0.75, "y": 0},
                        {"x": 0.75, "y": 0.5},
                        {"x": 0.25, "y": 0.5},
                        {"x": 0.25, "y": 0}
                    ],
                    "hasDownConnection": i % 2 == 0,
                    "hasRightConnection": i % 3 == 0
                } for i in range(1, 17)
            ]
        }
    
    def _find_self_inverse(self, inv_array: List[int]) -> List[int]:
        """Find self-inverse elements"""
        result = []
        for i in range(len(inv_array)):
            if inv_array[i] == i + 1:  # 1-indexed
                result.append(i + 1)
        return result
    
    def _intersect(self, arr1: List[int], arr2: List[int]) -> List[int]:
        """Array intersection"""
        return [x for x in arr1 if x in arr2]
    
    def _random_choice(self, arr: List[int]) -> int:
        """Random array element selector"""
        if not arr:
            return 1
        return random.choice(arr)
    
    def _ones(self, size: int) -> List[List[int]]:
        """Create matrix filled with ones"""
        return [[1 for _ in range(size)] for _ in range(size)]
    
    def propose_kolam_1d(self, size_of_kolam: int) -> List[List[int]]:
        """
        Generate 1D kolam pattern using traditional algorithm
        Literal translation of propose_kolam1D.m
        """
        odd = (size_of_kolam % 2) != 0
        
        if odd:
            hp = (size_of_kolam - 1) // 2
        else:
            hp = size_of_kolam // 2
        
        # Initialize matrix
        Mat = self._ones(hp + 2)
        
        # Generate pattern using connectivity rules
        for i in range(1, hp + 1):
            for j in range(1, hp + 1):
                # Get valid patterns based on neighbors
                pt_dn_value = self.PT_DN[Mat[i - 1][j] - 1]
                valid_by_up = self.MATE_PT_DN[pt_dn_value + 1]
                
                pt_rt_value = self.PT_RT[Mat[i][j - 1] - 1]
                valid_by_lt = self.MATE_PT_RT[pt_rt_value + 1]
                
                valids = self._intersect(valid_by_up, valid_by_lt)
                
                try:
                    v = self._random_choice(valids)
                    Mat[i][j] = v
                except:
                    Mat[i][j] = 1
        
        # Set boundary conditions
        Mat[hp + 1][0] = 1
        Mat[0][hp + 1] = 1
        
        # Fill remaining cells with symmetry constraints
        for j in range(1, hp + 1):
            pt_dn_value = self.PT_DN[Mat[hp][j] - 1]
            valid_by_up = self.MATE_PT_DN[pt_dn_value + 1]
            
            pt_rt_value = self.PT_RT[Mat[hp + 1][j - 1] - 1]
            valid_by_lt = self.MATE_PT_RT[pt_rt_value + 1]
            
            valids = self._intersect(valid_by_up, valid_by_lt)
            valids = self._intersect(valids, self._find_self_inverse(self.V_INV))
            
            try:
                v = self._random_choice(valids)
                Mat[hp + 1][j] = v
            except:
                Mat[hp + 1][j] = 1
        
        for i in range(1, hp + 1):
            pt_dn_value = self.PT_DN[Mat[i - 1][hp + 1] - 1]
            valid_by_up = self.MATE_PT_DN[pt_dn_value + 1]
            
            pt_rt_value = self.PT_RT[Mat[i][hp] - 1]
            valid_by_lt = self.MATE_PT_RT[pt_rt_value + 1]
            
            valids = self._intersect(valid_by_up, valid_by_lt)
            valids = self._intersect(valids, self._find_self_inverse(self.H_INV))
            
            try:
                v = self._random_choice(valids)
                Mat[i][hp + 1] = v
            except:
                Mat[i][hp + 1] = 1
        
        # Corner cell
        pt_dn_value = self.PT_DN[Mat[hp][hp + 1] - 1]
        valid_by_up = self.MATE_PT_DN[pt_dn_value + 1]
        
        pt_rt_value = self.PT_RT[Mat[hp + 1][hp] - 1]
        valid_by_lt = self.MATE_PT_RT[pt_rt_value + 1]
        
        valids = self._intersect(valid_by_up, valid_by_lt)
        valids = self._intersect(valids, self._find_self_inverse(self.H_INV))
        valids = self._intersect(valids, self._find_self_inverse(self.V_INV))
        
        try:
            v = self._random_choice(valids)
            Mat[hp + 1][hp + 1] = v
        except:
            Mat[hp + 1][hp + 1] = 1
        
        # Extract core pattern
        Mat1 = [[Mat[i][j] for j in range(1, hp + 1)] for i in range(1, hp + 1)]
        
        # Apply symmetry transformations
        Mat3 = [[self.V_INV[Mat1[hp - 1 - i][j] - 1] for j in range(hp)] for i in range(hp)]
        Mat2 = [[self.H_INV[Mat1[i][hp - 1 - j] - 1] for j in range(hp)] for i in range(hp)]
        Mat4 = [[self.V_INV[Mat2[hp - 1 - i][j] - 1] for j in range(hp)] for i in range(hp)]
        
        # Assemble final matrix
        if odd:
            size = 2 * hp + 1
            M = [[1 for _ in range(size)] for _ in range(size)]
            
            # Copy Mat1
            for i in range(hp):
                for j in range(hp):
                    M[i][j] = Mat1[i][j]
            
            # Add boundary elements
            for i in range(1, hp + 1):
                M[i - 1][hp] = Mat[i][hp + 1]
            
            for i in range(hp):
                for j in range(hp):
                    M[i][hp + 1 + j] = Mat2[i][j]
            
            for j in range(1, hp + 2):
                M[hp][j - 1] = Mat[hp + 1][j]
            
            for j in range(hp, 0, -1):
                M[hp][hp + (hp - j + 1)] = self.H_INV[Mat[hp + 1][j] - 1]
            
            for i in range(hp):
                for j in range(hp):
                    M[hp + 1 + i][j] = Mat3[i][j]
            
            for i in range(hp, 0, -1):
                M[hp + (hp - i + 1)][hp] = self.V_INV[Mat[i][hp + 1] - 1]
            
            for i in range(hp):
                for j in range(hp):
                    M[hp + 1 + i][hp + 1 + j] = Mat4[i][j]
        else:
            size = 2 * hp
            M = [[1 for _ in range(size)] for _ in range(size)]
            
            # Copy all four quadrants
            for i in range(hp):
                for j in range(hp):
                    M[i][j] = Mat1[i][j]
                    M[i][hp + j] = Mat2[i][j]
                    M[hp + i][j] = Mat3[i][j]
                    M[hp + i][hp + j] = Mat4[i][j]
        
        return M
    
    def draw_kolam(self, matrix: List[List[int]]) -> Dict[str, Any]:
        """Convert matrix to visual kolam pattern"""
        m, n = len(matrix), len(matrix[0])
        
        # Flip matrix vertically
        flipped_matrix = [matrix[m - 1 - i][:] for i in range(m)]
        
        dots = []
        curves = []
        
        for i in range(m):
            for j in range(n):
                if flipped_matrix[i][j] > 0:
                    # Add dot
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
                    
                    # Add curve pattern
                    pattern_id = flipped_matrix[i][j] - 1
                    if pattern_id < len(self.patterns_data['patterns']):
                        pattern = self.patterns_data['patterns'][pattern_id]
                        curve_points = []
                        
                        for point in pattern['points']:
                            curve_points.append({
                                'x': ((j + 1) + point['x']) * self.cell_spacing,
                                'y': ((i + 1) + point['y']) * self.cell_spacing
                            })
                        
                        if len(curve_points) > 1:
                            curves.append({
                                'id': f'curve-{i}-{j}',
                                'start': curve_points[0],
                                'end': curve_points[-1],
                                'curvePoints': curve_points,
                                'strokeWidth': 2,
                                'color': '#000000'
                            })
        
        return {
            'id': f'kolam-{m}x{n}',
            'name': f'Kolam {m}×{n}',
            'grid': {
                'size': max(m, n),
                'cells': [[{
                    'row': i,
                    'col': j,
                    'patternId': flipped_matrix[i][j],
                    'dotCenter': {
                        'x': (j + 1) * self.cell_spacing,
                        'y': (i + 1) * self.cell_spacing
                    }
                } for j in range(n)] for i in range(m)],
                'cellSpacing': self.cell_spacing
            },
            'curves': curves,
            'dots': dots,
            'symmetryType': '1D',
            'dimensions': {
                'width': (n + 1) * self.cell_spacing,
                'height': (m + 1) * self.cell_spacing
            }
        }
    
    def generate_kolam_1d(self, size: int) -> Dict[str, Any]:
        """Main entry point - generate kolam pattern"""
        print(f"🎨 Generating 1D Kolam of size {size}")
        
        matrix = self.propose_kolam_1d(size)
        print(f"📊 Generated matrix: {len(matrix)}x{len(matrix[0])}")
        
        pattern = self.draw_kolam(matrix)
        print(f"✅ Created kolam with {len(pattern['dots'])} dots and {len(pattern['curves'])} curves")
        
        return pattern
    
    def generate_kolam_svg(self, pattern: Dict[str, Any], options: Dict[str, Any] = None) -> str:
        """Generate SVG representation of kolam pattern"""
        if options is None:
            options = {}
        
        background = options.get('background', '#fef3c7')
        brush = options.get('brush', '#92400e')
        padding = options.get('padding', 40)
        
        dimensions = pattern['dimensions']
        dots = pattern['dots']
        curves = pattern['curves']
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{dimensions['width']}" height="{dimensions['height']}" viewBox="0 0 {dimensions['width']} {dimensions['height']}" xmlns="http://www.w3.org/2000/svg" style="max-width: 100%; height: auto; background-color: {background};">
    <defs>
        <style>
            .kolam-curve {{
                fill: none;
                stroke: {brush};
                stroke-width: 3;
                stroke-linecap: round;
                stroke-linejoin: round;
            }}
            .kolam-dot {{
                fill: {brush};
            }}
        </style>
    </defs>'''
        
        # Add dots
        for dot in dots:
            svg_content += f'''
    <circle class="kolam-dot"
        cx="{dot['center']['x']}" 
        cy="{dot['center']['y']}" 
        r="{dot.get('radius', 3)}" 
        fill="{brush}" 
        stroke="{brush}" 
        stroke-width="1"/>'''
        
        # Add curves
        for curve in curves:
            if 'curvePoints' in curve and len(curve['curvePoints']) > 1:
                # Create SVG path
                path_data = "M"
                for i, point in enumerate(curve['curvePoints']):
                    if i == 0:
                        path_data += f" {point['x']},{point['y']}"
                    else:
                        path_data += f" L {point['x']},{point['y']}"
                
                svg_content += f'''
    <path class="kolam-curve" d="{path_data}"/>'''
            else:
                # Simple line
                svg_content += f'''
    <line class="kolam-curve" x1="{curve['start']['x']}" y1="{curve['start']['y']}" x2="{curve['end']['x']}" y2="{curve['end']['y']}"/>'''
        
        svg_content += '''
</svg>'''
        
        return svg_content
    
    def generate_kolam_image(self, pattern: Dict[str, Any], image_size: Tuple[int, int] = (500, 500), include_dots: bool = True, theme: str = 'traditional') -> str:
        """Generate PIL image from kolam pattern and return as base64"""
        width, height = image_size
        
        # Theme color definitions
        theme_colors = {
            'traditional': {'background': '#ffffff', 'stroke': '#000000', 'fill': '#000000'},
            'colorful': {'background': '#ffffff', 'stroke': '#ff6b6b', 'fill': '#4ecdc4'},
            'golden': {'background': '#fff8e1', 'stroke': '#ff8f00', 'fill': '#ffb300'},
            'ocean': {'background': '#e3f2fd', 'stroke': '#1976d2', 'fill': '#03a9f4'},
            'sunset': {'background': '#fce4ec', 'stroke': '#e91e63', 'fill': '#ff9800'},
            'forest': {'background': '#f1f8e9', 'stroke': '#388e3c', 'fill': '#689f38'}
        }
        
        colors = theme_colors.get(theme, theme_colors['traditional'])
        image = Image.new('RGB', (width, height), colors['background'])
        draw = ImageDraw.Draw(image)
        
        # Scale pattern to fit image
        pattern_width = pattern['dimensions']['width']
        pattern_height = pattern['dimensions']['height']
        scale_x = width / pattern_width
        scale_y = height / pattern_height
        scale = min(scale_x, scale_y) * 0.8  # Leave some padding
        
        # Draw dots if requested
        if include_dots and 'dots' in pattern:
            for dot in pattern['dots']:
                center_x = int(dot['center']['x'] * scale + width * 0.1)
                center_y = int(dot['center']['y'] * scale + height * 0.1)
                radius = int(dot['radius'] * scale)
                draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], 
                           fill=colors['fill'], outline=colors['stroke'])
        
        # Draw curves
        for curve in pattern['curves']:
            if 'curvePoints' in curve and len(curve['curvePoints']) > 1:
                points = []
                for point in curve['curvePoints']:
                    x = int(point['x'] * scale + width * 0.1)
                    y = int(point['y'] * scale + height * 0.1)
                    points.append((x, y))
                
                if len(points) > 1:
                    draw.line(points, fill=colors['stroke'], width=2)
            else:
                start_x = int(curve['start']['x'] * scale + width * 0.1)
                start_y = int(curve['start']['y'] * scale + height * 0.1)
                end_x = int(curve['end']['x'] * scale + width * 0.1)
                end_y = int(curve['end']['y'] * scale + height * 0.1)
                draw.line([(start_x, start_y), (end_x, end_y)], fill=colors['stroke'], width=2)
        
        # Convert to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Global instance for easy access
zen_kolam_generator = ZenKolamGenerator()
