import cv2
import numpy as np
from PIL import Image
import io
import math
import base64
import time

def _trace_path(skeleton, start_point, visited):
    """An improved helper function to trace a single path from a starting point."""
    path = [start_point]
    visited[start_point[1], start_point[0]] = 255
    
    # Directions to check for neighboring pixels (8-connectivity)
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    current_point = start_point
    max_path_length = 1000  # Prevent infinite loops
    path_length = 0
    
    while path_length < max_path_length:
        found_next = False
        best_next = None
        min_distance = float('inf')
        
        # Look for the best next point (closest to current direction)
        for dx, dy in directions:
            next_x, next_y = current_point[0] + dx, current_point[1] + dy
            
            # Check bounds
            if 0 <= next_y < skeleton.shape[0] and 0 <= next_x < skeleton.shape[1]:
                if skeleton[next_y, next_x] == 255 and visited[next_y, next_x] == 0:
                    # Calculate distance from current point
                    distance = np.sqrt(dx*dx + dy*dy)
                    if distance < min_distance:
                        min_distance = distance
                        best_next = (next_x, next_y)
                        found_next = True
        
        if found_next and best_next:
            current_point = best_next
            path.append(current_point)
            visited[current_point[1], current_point[0]] = 255
            path_length += 1
        else:
            break
            
    return path

def _find_paths_from_skeleton(skeleton):
    """
    Traces all the distinct line paths from a skeleton image with improved accuracy.
    """
    paths = []
    # Create a mask to keep track of visited pixels
    visited = np.zeros(skeleton.shape, dtype=np.uint8)
    
    # Find all white pixels (potential path points)
    white_pixels = np.argwhere(skeleton == 255)
    
    # Sort pixels by their distance from center for better path ordering
    center_y, center_x = skeleton.shape[0] // 2, skeleton.shape[1] // 2
    white_pixels = sorted(white_pixels, key=lambda p: np.sqrt((p[0] - center_y)**2 + (p[1] - center_x)**2))
    
    for pixel in white_pixels:
        # The pixel coordinates are returned as (row, col) which is (y, x)
        y, x = pixel
        if visited[y, x] == 0:
            # If we haven't visited this pixel, it's the start of a new path
            new_path = _trace_path(skeleton, (x, y), visited)
            if len(new_path) > 5:  # Reduced minimum length for better coverage
                # Smooth the path for better accuracy
                smoothed_path = _smooth_path(new_path)
                paths.append(smoothed_path)
                
    return paths

def _smooth_path(path, window_size=3):
    """
    Smooth a path by applying a moving average filter.
    """
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

def _estimate_grid_from_dots(dot_coords, tolerance_factor=0.3):
    """
    An improved method to estimate grid size by clustering dot coordinates with better accuracy.
    """
    if len(dot_coords) < 2:
        return 3 if dot_coords else 3  # Default to 3x3 grid

    coords = np.array(dot_coords)
    
    # Calculate pairwise distances to estimate grid spacing
    distances = []
    for i in range(len(coords)):
        for j in range(i+1, len(coords)):
            dist = np.sqrt((coords[i][0] - coords[j][0])**2 + (coords[i][1] - coords[j][1])**2)
            distances.append(dist)
    
    if not distances:
        return 3
    
    # Use median distance as base grid spacing
    median_distance = np.median(distances)
    tolerance = median_distance * tolerance_factor
    
    # Cluster X coordinates to find columns
    sorted_x = np.sort(coords[:, 0])
    clusters_x = []
    if len(sorted_x) > 0:
        current_cluster = [sorted_x[0]]
        for x in sorted_x[1:]:
            if x - current_cluster[-1] < tolerance:
                current_cluster.append(x)
            else:
                clusters_x.append(current_cluster)
                current_cluster = [x]
        clusters_x.append(current_cluster)
    num_cols = len(clusters_x)
    
    # Cluster Y coordinates to find rows
    sorted_y = np.sort(coords[:, 1])
    clusters_y = []
    if len(sorted_y) > 0:
        current_cluster = [sorted_y[0]]
        for y in sorted_y[1:]:
            if y - current_cluster[-1] < tolerance:
                current_cluster.append(y)
            else:
                clusters_y.append(current_cluster)
                current_cluster = [y]
        clusters_y.append(current_cluster)
    num_rows = len(clusters_y)
    
    # Use the more reliable dimension (usually the larger one)
    grid_size = max(num_rows, num_cols)
    
    # Ensure we have a reasonable grid size
    if grid_size < 3:
        grid_size = 3
    elif grid_size > 15:
        grid_size = 15
    
    # Do not force odd numbers; allow even square sizes like 4x4, 6x6

    return grid_size

def analyze_kolam_image(image_file_bytes):
    """
    Ultra-advanced kolam analysis with vector-based pattern recognition for maximum accuracy.
    """
    # Enable OpenCV optimizations (do not force single-thread)
    try:
        cv2.setUseOptimized(True)
    except Exception:
        pass

    pil_image = Image.open(io.BytesIO(image_file_bytes)).convert('RGB')
    open_cv_image = np.array(pil_image)
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    
    # Downscale very large images for faster processing (without noticeable quality loss)
    max_dim = max(open_cv_image.shape[0], open_cv_image.shape[1])
    process_image = open_cv_image
    scale_factor = 1.0
    if max_dim > 1000:
        scale_factor = 1000.0 / max_dim
        process_image = cv2.resize(open_cv_image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
    
    # === 1. ULTRA-ADVANCED IMAGE PREPROCESSING ===
    gray = cv2.cvtColor(process_image, cv2.COLOR_BGR2GRAY)
    
    # Multiple enhancement techniques
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Bilateral filter to preserve edges while reducing noise
    # Use bilateral for medium images; Gaussian for very large ones (faster)
    if max_dim > 2000:
        filtered = cv2.GaussianBlur(enhanced, (3,3), 0)
    else:
        filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    overall_start = time.time()
    overall_budget_sec = 55.0

    # === 2. ULTRA-SOPHISTICATED DOT DETECTION ===
    dot_coords = _detect_dots_ultra_advanced(filtered, process_image)
    
    # === 3. VECTOR-BASED PATTERN TRACING (with fallback for hand-drawn) ===
    traced_paths = []
    time_left = overall_budget_sec - (time.time() - overall_start)
    if time_left > 0:
        traced_paths = _trace_kolam_vector_based(filtered, process_image, dot_coords)
        if (not traced_paths or len(traced_paths) == 0) and (time.time() - overall_start) < overall_budget_sec:
            traced_paths = _trace_kolam_fallback_handdrawn(process_image)
    
    # === 4. GRID ESTIMATION ===
    grid_size = _estimate_grid_from_dots(dot_coords)
    
    # === 5. RETURN RESULTS ===
    _, buffer = cv2.imencode('.png', process_image)
    processed_image_b64 = base64.b64encode(buffer).decode('utf-8')

    return grid_size, dot_coords, traced_paths, processed_image_b64

def _detect_dots_ultra_advanced(gray_image, output_image):
    """Ultra-advanced dot detection with maximum accuracy."""
    dot_coords = []
    start_time = time.time()
    time_budget_sec = 8.0  # keep dot detection bounded
    
    # Method 1: Multi-scale HoughCircles detection
    for scale in [0.8, 1.0, 1.2]:
        if time.time() - start_time > time_budget_sec:
            break
        scaled_image = cv2.resize(gray_image, None, fx=scale, fy=scale)
        
        for min_dist in [10, 15, 20, 25]:
            if time.time() - start_time > time_budget_sec:
                break
            for param2 in [10, 15, 20, 25, 30]:
                if time.time() - start_time > time_budget_sec:
                    break
                circles = cv2.HoughCircles(
                    scaled_image, 
                    cv2.HOUGH_GRADIENT, 
                    dp=1, 
                    minDist=min_dist,
                    param1=30,
                    param2=param2,
                    minRadius=2, 
                    maxRadius=40
                )
                
                if circles is not None:
                    circles = np.round(circles[0, :]).astype("int")
                    for (x, y, r) in circles:
                        # Scale back coordinates
                        x = int(x / scale)
                        y = int(y / scale)
                        r = int(r / scale)
                        
                        # Check if this dot is not already detected
                        if not any(np.sqrt((x-cx)**2 + (y-cy)**2) < 8 for cx, cy in dot_coords):
                            dot_coords.append((x, y))
                            cv2.circle(output_image, (x, y), r, (0, 255, 0), 2)
                        # Early exit if enough dots found
                        if len(dot_coords) >= 150:
                            break
                    if len(dot_coords) >= 150:
                        break
            if len(dot_coords) >= 150:
                break
    
    # Method 2: Advanced contour-based detection
    if time.time() - start_time < time_budget_sec:
        _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if time.time() - start_time > time_budget_sec:
                break
            area = cv2.contourArea(contour)
            if 10 < area < 800:  # Wider range for dot detection
                # Check if contour is roughly circular
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.6:  # More lenient circularity check
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            # Check if this dot is not already detected
                            if not any(np.sqrt((cx-x)**2 + (cy-y)**2) < 12 for x, y in dot_coords):
                                dot_coords.append((cx, cy))
                                cv2.circle(output_image, (cx, cy), 4, (0, 255, 0), 2)
    
    return dot_coords

def _trace_kolam_vector_based(gray_image, output_image, dot_coords):
    """Vector-based kolam pattern tracing for maximum accuracy."""
    traced_paths = []
    start_time = time.time()
    time_budget_sec = 20.0
    
    # Create binary image with multiple thresholding methods
    _, binary1 = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    binary2 = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Combine binary images
    binary = cv2.bitwise_or(binary1, binary2)
    
    # Invert so lines are white
    binary = cv2.bitwise_not(binary)
    
    # Advanced morphological operations
    kernel_close = np.ones((2,2), np.uint8)
    kernel_open = np.ones((1,1), np.uint8)
    
    # Close gaps in lines
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)
    # Remove noise
    cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_open)
    
    # Crop to active region to reduce processing area
    nz = cv2.findNonZero(cleaned)
    offset_x = 0
    offset_y = 0
    roi = cleaned
    if nz is not None and len(nz) > 0:
        x, y, w, h = cv2.boundingRect(nz)
        pad = 8
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(cleaned.shape[1], x + w + pad)
        y1 = min(cleaned.shape[0], y + h + pad)
        roi = cleaned[y0:y1, x0:x1]
        offset_x, offset_y = x0, y0
    
    # Skeletonization on ROI (with safe fallback)
    try:
        skeleton = cv2.ximgproc.thinning(roi)
    except Exception:
        skel = np.zeros_like(roi)
        elem = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
        eroded = np.copy(roi)
        while True:
            eroded = cv2.erode(eroded, elem)
            opened = cv2.morphologyEx(eroded, cv2.MORPH_OPEN, elem)
            temp = cv2.subtract(eroded, opened)
            skel = cv2.bitwise_or(skel, temp)
            if cv2.countNonZero(eroded) == 0 or (time.time() - start_time) > time_budget_sec:
                break
        skeleton = skel
    
    # Find contours with hierarchy to capture all details
    contours, hierarchy = cv2.findContours(skeleton, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:100]
    
    # Process each contour with ultra-fine precision
    for i, contour in enumerate(contours):
        if (time.time() - start_time) > time_budget_sec:
            break
        if len(contour) > 5:
            epsilon = 0.001 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Convert to path format
            path = [(point[0][0] + offset_x, point[0][1] + offset_y) for point in approx]
            
            if len(path) > 1:
                # No smoothing - preserve all details
                traced_paths.append(path)
                
                # Draw the path
                for i in range(len(path) - 1):
                    cv2.line(output_image, path[i], path[i+1], (255, 0, 0), 1)
    
    # Also detect straight lines (only if time allows)
    lines = None
    if (time.time() - start_time) < time_budget_sec * 0.8:
        lines = cv2.HoughLinesP(skeleton, 1, np.pi/180, threshold=10, minLineLength=5, maxLineGap=2)
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            x1 += offset_x; x2 += offset_x; y1 += offset_y; y2 += offset_y
            path = [(x1, y1), (x2, y2)]
            traced_paths.append(path)
            cv2.line(output_image, (x1, y1), (x2, y2), (255, 0, 0), 1)
    
    # Connect nearby endpoints to create continuous paths
    traced_paths = _connect_nearby_paths(traced_paths)
    
    return traced_paths

def _connect_nearby_paths(paths, threshold=5):
    """Connect nearby path endpoints to create continuous lines."""
    if len(paths) < 2:
        return paths
    
    connected_paths = []
    used_paths = set()
    
    for i, path1 in enumerate(paths):
        if i in used_paths:
            continue
            
        current_path = path1[:]
        used_paths.add(i)
        
        # Try to connect with other paths
        connected = True
        while connected:
            connected = False
            for j, path2 in enumerate(paths):
                if j in used_paths:
                    continue
                
                # Check if paths can be connected
                if _can_connect_paths(current_path, path2, threshold):
                    current_path = _connect_paths(current_path, path2, threshold)
                    used_paths.add(j)
                    connected = True
                    break
        
        connected_paths.append(current_path)
    
    return connected_paths

def _can_connect_paths(path1, path2, threshold):
    """Check if two paths can be connected."""
    if not path1 or not path2:
        return False
    
    # Check all combinations of endpoints
    endpoints1 = [path1[0], path1[-1]]
    endpoints2 = [path2[0], path2[-1]]
    
    for ep1 in endpoints1:
        for ep2 in endpoints2:
            dist = np.sqrt((ep1[0] - ep2[0])**2 + (ep1[1] - ep2[1])**2)
            if dist < threshold:
                return True
    
    return False

def _connect_paths(path1, path2, threshold):
    """Connect two paths at their closest endpoints."""
    if not path1 or not path2:
        return path1 or path2
    
    endpoints1 = [path1[0], path1[-1]]
    endpoints2 = [path2[0], path2[-1]]
    
    min_dist = float('inf')
    best_connection = None
    
    for i, ep1 in enumerate(endpoints1):
        for j, ep2 in enumerate(endpoints2):
            dist = np.sqrt((ep1[0] - ep2[0])**2 + (ep1[1] - ep2[1])**2)
            if dist < min_dist and dist < threshold:
                min_dist = dist
                best_connection = (i, j)
    
    if best_connection is None:
        return path1
    
    i, j = best_connection
    
    if i == 0 and j == 0:  # Connect start to start
        return path2[::-1] + path1
    elif i == 0 and j == 1:  # Connect start to end
        return path2 + path1
    elif i == 1 and j == 0:  # Connect end to start
        return path1 + path2
    else:  # Connect end to end
        return path1 + path2[::-1]

def _smooth_path_minimal(path, window_size=3):
    """Minimal smoothing that preserves intricate details."""
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

def _smooth_path_advanced(path, window_size=5):
    """Advanced path smoothing that preserves important features."""
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

def _create_paths_between_dots(binary_image, dot_coords):
    """Create paths that connect dots in the kolam pattern."""
    paths = []
    
    if len(dot_coords) < 2:
        return paths
    
    # For each pair of dots, check if there's a line connecting them
    for i, dot1 in enumerate(dot_coords):
        for j, dot2 in enumerate(dot_coords[i+1:], i+1):
            # Check if there's a path between these dots
            path = _find_path_between_points(binary_image, dot1, dot2)
            if path and len(path) > 2:
                paths.append(path)
    
    return paths

def _find_path_between_points(binary_image, start, end):
    """Find a path between two points in the binary image."""
    # Use a simple line sampling approach
    x1, y1 = start
    x2, y2 = end
    
    # Sample points along the line
    num_samples = max(10, int(np.sqrt((x2-x1)**2 + (y2-y1)**2) / 5))
    path = []
    
    for i in range(num_samples + 1):
        t = i / num_samples
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))
        
        # Check if this point is on a line in the binary image
        if (0 <= x < binary_image.shape[1] and 0 <= y < binary_image.shape[0] and 
            binary_image[y, x] > 0):
            path.append((x, y))
    
    return path if len(path) > 2 else None

def _create_paths_from_segments(line_segments):
    """Create continuous paths from line segments."""
    if not line_segments:
        return []
    
    paths = []
    used_segments = set()
    
    for i, segment in enumerate(line_segments):
        if i in used_segments:
            continue
            
        # Start a new path
        path = [segment[0], segment[1]]
        used_segments.add(i)
        
        # Try to extend the path by finding connected segments
        extended = True
        while extended:
            extended = False
            for j, other_segment in enumerate(line_segments):
                if j in used_segments:
                    continue
                
                # Check if segments can be connected
                if _can_connect_segments(path, other_segment):
                    # Add the other segment to the path
                    if _should_append_segment(path, other_segment):
                        path.append(other_segment[1])
                    else:
                        path.insert(0, other_segment[0])
                    used_segments.add(j)
                    extended = True
                    break
        
        if len(path) > 2:
            paths.append(path)
    
    return paths

def _can_connect_segments(path, segment):
    """Check if a segment can be connected to a path."""
    if not path:
        return False
    
    last_point = path[-1]
    first_point = path[0]
    
    # Check if segment endpoints are close to path endpoints
    threshold = 10
    return (np.sqrt((last_point[0] - segment[0][0])**2 + (last_point[1] - segment[0][1])**2) < threshold or
            np.sqrt((last_point[0] - segment[1][0])**2 + (last_point[1] - segment[1][1])**2) < threshold or
            np.sqrt((first_point[0] - segment[0][0])**2 + (first_point[1] - segment[0][1])**2) < threshold or
            np.sqrt((first_point[0] - segment[1][0])**2 + (first_point[1] - segment[1][1])**2) < threshold)

def _should_append_segment(path, segment):
    """Determine if segment should be appended to the end of the path."""
    if not path:
        return True
    
    last_point = path[-1]
    threshold = 10
    
    # Check which endpoint of segment is closer to the last point of path
    dist_to_start = np.sqrt((last_point[0] - segment[0][0])**2 + (last_point[1] - segment[0][1])**2)
    dist_to_end = np.sqrt((last_point[0] - segment[1][0])**2 + (last_point[1] - segment[1][1])**2)
    
    return dist_to_start < dist_to_end
