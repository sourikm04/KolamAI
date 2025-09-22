from PIL import Image, ImageDraw
import io
import base64
import numpy as np

def create_digitized_kolam(original_dot_coords, traced_paths, estimated_rows, estimated_cols, theme='traditional'):
    """
    Creates an ultra-accurate digitized version that preserves ALL intricate kolam details.
    """
    # Theme color definitions
    theme_colors = {
        'traditional': {'background': '#ffffff', 'stroke': '#000000'},
        'colorful': {'background': '#ffffff', 'stroke': '#ff6b6b'},
        'golden': {'background': '#fff8e1', 'stroke': '#ff8f00'},
        'ocean': {'background': '#e3f2fd', 'stroke': '#1976d2'},
        'sunset': {'background': '#fce4ec', 'stroke': '#e91e63'},
        'forest': {'background': '#f1f8e9', 'stroke': '#388e3c'}
    }
    
    colors = theme_colors.get(theme, theme_colors['traditional'])
    
    # 1. Setup a clean canvas and a new, perfectly aligned dot grid
    image, draw, new_dot_grid = _setup_canvas_and_dots(estimated_rows, estimated_cols, background_color=colors['background'])
    
    if not traced_paths:
        return _image_to_b64(image)

    # 2. Get grid bounds
    new_grid_flat = [item for sublist in new_dot_grid for item in sublist]
    dest_coords = np.array(new_grid_flat)
    dest_min_x, dest_min_y = np.min(dest_coords, axis=0)
    dest_max_x, dest_max_y = np.max(dest_coords, axis=0)
    dest_width = dest_max_x - dest_min_x
    dest_height = dest_max_y - dest_min_y

    # 3. Calculate transformation parameters
    if len(original_dot_coords) > 0:
        orig_coords = np.array(original_dot_coords)
        orig_min_x, orig_min_y = np.min(orig_coords, axis=0)
        orig_max_x, orig_max_y = np.max(orig_coords, axis=0)
        orig_width = orig_max_x - orig_min_x
        orig_height = orig_max_y - orig_min_y
    else:
        orig_min_x = orig_min_y = 0
        orig_width = orig_height = 1

    # 4. Process and draw each traced path with maximum detail preservation
    for path in traced_paths:
        if len(path) < 2:
            continue
            
        # Transform to grid coordinates with ultra-high precision
        transformed_path = []
        for (x, y) in path:
            if orig_width > 0 and orig_height > 0:
                # Normalize to 0-1 with ultra-high precision
                norm_x = (x - orig_min_x) / orig_width
                norm_y = (y - orig_min_y) / orig_height
            else:
                norm_x = 0.5
                norm_y = 0.5
            
            # Map to grid coordinates
            new_x = dest_min_x + (norm_x * dest_width)
            new_y = dest_min_y + (norm_y * dest_height)
            
            transformed_path.append((new_x, new_y))
        
        # Draw the path with maximum detail preservation
        if len(transformed_path) > 1:
            # Use thin lines to preserve intricate details
            line_width = max(1, min(3, int(200 / (estimated_rows * estimated_cols))))
            
            # Draw each line segment individually for maximum control
            for i in range(len(transformed_path) - 1):
                start = transformed_path[i]
                end = transformed_path[i + 1]
                
                # Draw with precise control
                draw.line([start, end], fill=colors['stroke'], width=line_width)

    return _image_to_b64(image)

def _smooth_path_light(path, window_size=3):
    """Light smoothing that preserves more details."""
    if len(path) < window_size:
        return path
    
    smoothed = []
    for i in range(len(path)):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(path), i + window_size // 2 + 1)
        
        window = path[start_idx:end_idx]
        avg_x = sum(point[0] for point in window) / len(window)
        avg_y = sum(point[1] for point in window) / len(window)
        smoothed.append((int(avg_x), int(avg_y)))
    
    return smoothed

def _smooth_path(path, window_size=5):
    """Smooth a path using moving average."""
    if len(path) < window_size:
        return path
    
    smoothed = []
    for i in range(len(path)):
        start_idx = max(0, i - window_size // 2)
        end_idx = min(len(path), i + window_size // 2 + 1)
        
        window = path[start_idx:end_idx]
        avg_x = sum(point[0] for point in window) / len(window)
        avg_y = sum(point[1] for point in window) / len(window)
        smoothed.append((int(avg_x), int(avg_y)))
    
    return smoothed

def create_custom_grid_kolam(original_dot_coords, traced_paths, custom_rows, custom_cols):
    """
    Creates a custom grid version that STRICTLY respects the specified dimensions.
    """
    # 1. Setup canvas with EXACT custom grid dimensions
    image, draw, new_dot_grid = _setup_canvas_and_dots(custom_rows, custom_cols)
    
    if not traced_paths:
        return _image_to_b64(image)

    # 2. Get the actual grid dot positions
    grid_dots = []
    for row in new_dot_grid:
        for dot in row:
            grid_dots.append(dot)
    
    if not grid_dots:
        return _image_to_b64(image)
    
    # 3. Calculate grid bounds
    grid_coords = np.array(grid_dots)
    min_x, min_y = np.min(grid_coords, axis=0)
    max_x, max_y = np.max(grid_coords, axis=0)
    
    # 4. Create a mapping from original pattern to grid coordinates
    for path in traced_paths:
        if len(path) < 2:
            continue
            
        # Convert path to grid coordinates
        grid_path = []
        for x, y in path:
            # Map to grid space (0 to 1)
            if len(original_dot_coords) > 0:
                orig_coords = np.array(original_dot_coords)
                orig_min_x, orig_min_y = np.min(orig_coords, axis=0)
                orig_max_x, orig_max_y = np.max(orig_coords, axis=0)
                orig_width = orig_max_x - orig_min_x
                orig_height = orig_max_y - orig_min_y
                
                if orig_width > 0 and orig_height > 0:
                    # Normalize to 0-1
                    norm_x = (x - orig_min_x) / orig_width
                    norm_y = (y - orig_min_y) / orig_height
                else:
                    norm_x = 0.5
                    norm_y = 0.5
            else:
                norm_x = 0.5
                norm_y = 0.5
            
            # Map to actual grid coordinates
            grid_x = min_x + norm_x * (max_x - min_x)
            grid_y = min_y + norm_y * (max_y - min_y)
            
            # Ensure within bounds
            grid_x = max(min_x, min(max_x, grid_x))
            grid_y = max(min_y, min(max_y, grid_y))
            
            grid_path.append((grid_x, grid_y))
        
        # Draw the path
        if len(grid_path) > 1:
            line_width = max(2, min(4, int(400 / (custom_rows * custom_cols))))
            draw.line(grid_path, fill='red', width=line_width, joint='curve')

    return _image_to_b64(image)

# --- Helper Functions ---

def _setup_canvas_and_dots(rows, cols, image_size=(500, 500), dot_color='black', background_color='white'):
    """Setup canvas with dot grid."""
    image = Image.new('RGB', image_size, background_color)
    draw = ImageDraw.Draw(image)
    padding = 50
    dot_radius = max(2, min(8, int(250 / (rows * 2))))
    
    cell_width = (image_size[0] - 2 * padding) / (cols - 1) if cols > 1 else 0
    cell_height = (image_size[1] - 2 * padding) / (rows - 1) if rows > 1 else 0
    
    dot_grid = []
    for r in range(rows):
        row_coords = []
        for c in range(cols):
            x = padding + c * cell_width
            y = padding + r * cell_height
            row_coords.append((x, y))
            # Dots removed - only keep coordinates for reference
        dot_grid.append(row_coords)
        
    return image, draw, dot_grid

def _image_to_b64(image):
    """Convert PIL image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
