from manim import *
import numpy as np
import math


def create_lightbulb(x, y, z, center_radius, center_color, socket_width, socket_height, num_glow_rings, max_glow_radius, animation_duration=1.5):
    """
    Create a parametrized lightbulb with center circle, socket box with lines, and glow rings.
    
    Parameters:
    - x, y, z: bulb position
    - center_radius: radius of the center circle
    - center_color: color of the center circle
    - socket_width: width of the socket box
    - socket_height: height of the socket box
    - num_glow_rings: number of concentric glow rings
    - max_glow_radius: radius of the outermost glow ring
    - animation_duration: total time for glow animation (in seconds)
    
    Returns:
    - Tuple of (lightbulb_group, glow_circles, interval)
    """
    # Fixed styling parameters
    center_stroke_color = BLACK
    center_stroke_width = 6
    
    box_stroke_color = BLACK
    box_stroke_width = 4
    box_fill_color = center_color
    
    line_stroke_color = BLACK
    line_stroke_width = 4
    line_start_fraction = 0.25
    line_slope = 1/5
    line_vertical_spacing = 0.125
    
    lightbulb_position = np.array([x, y, z])
    
    # Create the central dot
    center_circle = Circle(
        radius=center_radius,
        fill_color=center_color,
        fill_opacity=1,
        stroke_color=center_stroke_color,
        stroke_width=center_stroke_width
    )
    center_circle.move_to(lightbulb_position)
    
    # Socket parameters - position socket's top edge center at bulb center
    box_z = 0
    box_x = lightbulb_position[0] - socket_width / 2
    box_y = lightbulb_position[1] - socket_height
    
    # Create socket box
    box = Rectangle(
        width=socket_width,
        height=socket_height,
        stroke_color=box_stroke_color,
        stroke_width=box_stroke_width,
        fill_opacity=1,
        fill_color=box_fill_color,
    )
    box.move_to([box_x + socket_width/2, box_y + socket_height/2, box_z])
    
    # Calculate first line's y-intercept
    line1_start_x = box_x + line_start_fraction * socket_width
    line1_start_y = box_y
    b_first = line1_start_y - line_slope * line1_start_x
    
    # Function to get line-box intersection points
    def get_line_intersection_in_box(b_value, slope, x_min, y_min, x_max, y_max):
        intersection_points = []
        
        # Check left edge (x = x_min)
        y_left = slope * x_min + b_value
        if y_min <= y_left <= y_max:
            intersection_points.append((x_min, y_left))
        
        # Check right edge (x = x_max)
        y_right = slope * x_max + b_value
        if y_min <= y_right <= y_max:
            intersection_points.append((x_max, y_right))
        
        # Check bottom edge (y = y_min)
        if slope != 0:
            x_bottom = (y_min - b_value) / slope
            if x_min <= x_bottom <= x_max:
                intersection_points.append((x_bottom, y_min))
        
        # Check top edge (y = y_max)
        if slope != 0:
            x_top = (y_max - b_value) / slope
            if x_min <= x_top <= x_max:
                intersection_points.append((x_top, y_max))
        
        if len(intersection_points) < 2:
            return None
        
        intersection_points.sort(key=lambda p: p[0])
        return intersection_points[0], intersection_points[-1]
    
    # Create all parallel lines in socket
    lines_to_add = []
    
    # Center line (n=0)
    result = get_line_intersection_in_box(b_first, line_slope, box_x, box_y, box_x + socket_width, box_y + socket_height)
    if result is not None:
        start_pt, end_pt = result
        line = Line(
            start=np.array([start_pt[0], start_pt[1], box_z]),
            end=np.array([end_pt[0], end_pt[1], box_z]),
            stroke_color=line_stroke_color,
            stroke_width=line_stroke_width
        )
        lines_to_add.append(line)
    
    # Positive direction
    n = 1
    while True:
        b_pos = b_first + n * line_vertical_spacing
        result = get_line_intersection_in_box(b_pos, line_slope, box_x, box_y, box_x + socket_width, box_y + socket_height)
        if result is None:
            break
        start_pt, end_pt = result
        line = Line(
            start=np.array([start_pt[0], start_pt[1], box_z]),
            end=np.array([end_pt[0], end_pt[1], box_z]),
            stroke_color=line_stroke_color,
            stroke_width=line_stroke_width
        )
        lines_to_add.append(line)
        n += 1
    
    # Negative direction
    n = 1
    while True:
        b_neg = b_first - n * line_vertical_spacing
        result = get_line_intersection_in_box(b_neg, line_slope, box_x, box_y, box_x + socket_width, box_y + socket_height)
        if result is None:
            break
        start_pt, end_pt = result
        line = Line(
            start=np.array([start_pt[0], start_pt[1], box_z]),
            end=np.array([end_pt[0], end_pt[1], box_z]),
            stroke_color=line_stroke_color,
            stroke_width=line_stroke_width
        )
        lines_to_add.append(line)
        n += 1
    
    # Create glow circles
    glow_circles = []
    for i in range(1, num_glow_rings + 1):
        radius = (i / num_glow_rings) * max_glow_radius
        opacity = max(0, 1 - (i / num_glow_rings) ** 1.5)
        
        glow = Circle(
            radius=radius,
            fill_color=center_color,
            fill_opacity=opacity,
            stroke_color=BLACK,
            stroke_opacity=0,
            stroke_width=0
        )
        glow.move_to(lightbulb_position)
        glow_circles.append(glow)
    
    # Calculate animation interval
    interval = animation_duration / num_glow_rings
    
    # Return main bulb group (without glow for animation), glow circles, and interval
    bulb_group = VGroup(box, *lines_to_add, center_circle)
    return bulb_group, glow_circles, interval


def create_wheel_box(x, y, z, tilt, width, height, line_offset_percent=0.05, connector_direction=False):
    """
    Create a parametrized rectangular wheel box seen from above.
    
    Parameters:
    - x, y, z: wheel position 
    - tilt: slope of the bottom edge 
    - width: length of the bottom edge along the slope
    - height: perpendicular distance from bottom to top edge
    - line_offset_percent: starting offset of lines as a fraction of height (0.0 to 1.0)
    - connector_direction: True for right side connector, False for left side connector
    
    Returns:
    - Tuple of (wheel_vgroup, connector_end_point)
      - wheel_vgroup: VGroup containing the wheel box, interior lines, and connector line
      - connector_end_point: numpy array [x, y, z] coordinates of the connector line endpoint
    """
    # Fixed styling parameters
    box_fill_color = WHITE
    box_stroke_color = BLACK
    box_stroke_width = 4
    
    line_stroke_color = "#3A3A3A"  # Darkest gray from CLprompts.txt
    line_stroke_width = 2
    line_spacing = 0.1
    line_offset_start = line_offset_percent * height
    
    connector_length = 0.3
    
    # Convert wheel position to numpy array
    pos = np.array([x, y, z])
    
    # Calculate angle from slope
    angle = math.atan(tilt)
    
    # Unit vector along the slope
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Bottom-left corner (starting point)
    p1 = pos + np.array([0, 0, 0])
    
    # Bottom-right corner (along the slope)
    p2 = pos + np.array([width * cos_a, width * sin_a, 0])
    
    # Perpendicular direction vector (rotated 90 degrees counter-clockwise)
    perp_x = -sin_a
    perp_y = cos_a
    
    # Top-right corner (perpendicular from bottom-right)
    p3 = p2 + np.array([height * perp_x, height * perp_y, 0])
    
    # Top-left corner (perpendicular from bottom-left)
    p4 = p1 + np.array([height * perp_x, height * perp_y, 0])
    
    # Create polygon from the four corners
    wheel_box = Polygon(
        p1, p2, p3, p4,
        fill_color=box_fill_color,
        fill_opacity=1,
        stroke_color=box_stroke_color,
        stroke_width=box_stroke_width
    )
    
    # Calculate y-intercept of the reference edge (bottom edge)
    # Reference edge passes through p1 with slope = tilt
    b_ref = p1[1] - tilt * p1[0]
    
    # Create interior parallel lines
    interior_lines = []
    
    # Generate all offset distances: start at line_offset_start and go both directions
    offset_distances = [line_offset_start]
    
    # Positive direction
    offset = line_offset_start + line_spacing
    while offset < height:
        offset_distances.append(offset)
        offset += line_spacing
    
    # Negative direction
    offset = line_offset_start - line_spacing
    while offset > 0:
        offset_distances.append(offset)
        offset -= line_spacing
    
    # Draw lines for each offset distance
    for offset_distance in offset_distances:
        # Calculate y-intercept for this offset line
        b_new = b_ref + offset_distance / cos_a
        
        # Find intersection with left edge (segment p1-p4)
        p1_x, p1_y = p1[0], p1[1]
        p4_x, p4_y = p4[0], p4[1]
        
        denom_left = (p4_y - p1_y) - tilt * (p4_x - p1_x)
        numer_left = tilt * p1_x + b_new - p1_y
        
        if abs(denom_left) > 1e-10:
            t_left = numer_left / denom_left
            if 0 <= t_left <= 1:
                left_point = p1 + t_left * (p4 - p1)
            else:
                left_point = None
        else:
            left_point = None
        
        # Find intersection with right edge (segment p2-p3)
        p2_x, p2_y = p2[0], p2[1]
        p3_x, p3_y = p3[0], p3[1]
        
        denom_right = (p3_y - p2_y) - tilt * (p3_x - p2_x)
        numer_right = tilt * p2_x + b_new - p2_y
        
        if abs(denom_right) > 1e-10:
            t_right = numer_right / denom_right
            if 0 <= t_right <= 1:
                right_point = p2 + t_right * (p3 - p2)
            else:
                right_point = None
        else:
            right_point = None
        
        # Draw line if both endpoints exist
        if left_point is not None and right_point is not None:
            line = Line(
                start=left_point,
                end=right_point,
                stroke_color=line_stroke_color,
                stroke_width=line_stroke_width
            )
            interior_lines.append(line)
    
    # Create connector line
    if connector_direction == False:
        # Left side connector: from lower x corner (p1)
        # Middle of perpendicular edge p1-p4
        connector_start = (p1 + p4) / 2
        # Draw in negative x direction with given slope
        connector_end = connector_start + np.array([-connector_length, -connector_length * tilt, 0])
    else:
        # Right side connector: from higher x corner (p2)
        # Middle of perpendicular edge p2-p3
        connector_start = (p2 + p3) / 2
        # Draw in positive x direction with given slope
        connector_end = connector_start + np.array([connector_length, connector_length * tilt, 0])
    
    connector_line = Line(
        start=connector_start,
        end=connector_end,
        stroke_color=box_stroke_color,
        stroke_width=box_stroke_width,
    )
    
    # Create connector label based on direction
    connector_label = Text("+", color=BLACK, font_size=20)
    if connector_direction == False:
        # Left side: label at connector_end x, connector_end y - 0.15, z = 0
        connector_label.move_to([connector_end[0], connector_end[1] - 0.15, 0])
    else:
        # Right side: label at connector_end x, connector_end y, z = 0
        connector_label.move_to([connector_end[0], connector_end[1], 0])
    
    # Return a group containing the box, interior lines, connector line, plus the connector endpoint and label
    return VGroup(wheel_box, *interior_lines, connector_line, connector_label), connector_end


def create_body(x, y, z, width, height, tilt):
    """
    Create a parametrized rectangular body for the Braitenberg vehicle.
    
    Parameters:
    - x, y, z: body position (center)
    - width: width of the body along the slope
    - height: perpendicular distance of the body
    - tilt: slope of the body reference edge
    
    Returns:
    - A manim Polygon object
    """
    # Fixed styling parameters
    fill_color = "#AFCBCF"  # Light blue from CLprompts.txt
    stroke_color = BLACK
    stroke_width = 4
    
    # Convert body position to numpy array
    pos = np.array([x, y, z])
    
    # Calculate angle from slope
    angle = math.atan(tilt)
    
    # Unit vector along the slope
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Bottom-left corner (starting point)
    p1 = pos + np.array([0, 0, 0])
    
    # Bottom-right corner (along the slope)
    p2 = pos + np.array([width * cos_a, width * sin_a, 0])
    
    # Perpendicular direction vector (rotated 90 degrees counter-clockwise)
    perp_x = -sin_a
    perp_y = cos_a
    
    # Top-right corner (perpendicular from bottom-right)
    p3 = p2 + np.array([height * perp_x, height * perp_y, 0])
    
    # Top-left corner (perpendicular from bottom-left)
    p4 = p1 + np.array([height * perp_x, height * perp_y, 0])
    
    # Create polygon from the four corners
    body = Polygon(
        p1, p2, p3, p4,
        fill_color=fill_color,
        fill_opacity=1,
        stroke_color=stroke_color,
        stroke_width=stroke_width
    )
    
    return body


def calculate_wheel_center_position(body_x, body_y, body_z, body_width, body_height, body_tilt, wheel_width, wheel_height):
    """
    Calculate the center position of a wheel to be centered within the body.
    
    Parameters:
    - body_x, body_y, body_z: body corner position
    - body_width, body_height: body dimensions
    - body_tilt: body slope
    - wheel_width, wheel_height: wheel dimensions
    
    Returns:
    - Tuple of (wheel_x, wheel_y, wheel_z, wheel_tilt, connector_direction)
    """
    # Calculate angle from slope
    body_angle = math.atan(body_tilt)
    cos_a = math.cos(body_angle)
    sin_a = math.sin(body_angle)
    
    # Open space in each direction
    open_space_width = body_width - wheel_width
    open_space_height = body_height - wheel_height
    
    # Center the wheel by moving half the open space from body corner
    wheel_x = body_x + 0.5 * open_space_width * cos_a + 0.5 * open_space_height * (-sin_a)
    wheel_y = body_y + 0.5 * open_space_width * sin_a + 0.5 * open_space_height * cos_a
    wheel_z = body_z
    
    # Wheel tilt equal to body tilt
    wheel_tilt = body_tilt
    
    # Connector direction (True for right side)
    connector_direction = False
    
    return wheel_x, wheel_y, wheel_z, wheel_tilt, connector_direction


def calculate_sensor_center_position(body_x, body_y, body_z, body_width, body_height, body_tilt, sensor_radius):
    """
    Calculate the center position of a sensor to be positioned on the body.
    
    Parameters:
    - body_x, body_y, body_z: body corner position
    - body_width, body_height: body dimensions
    - body_tilt: body slope
    - sensor_radius: radius of the sensor half-circle
    
    Returns:
    - Tuple of (sensor_x, sensor_y, sensor_z)
    """
    # Fixed default parameters
    sensor_distance = 2
    
    # Convert body position to numpy array
    pos = np.array([body_x, body_y, body_z])
    
    # Calculate angle from slope
    angle = math.atan(body_tilt)
    
    # Unit vector along the slope
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Perpendicular direction vector (rotated 90 degrees counter-clockwise)
    perp_x = -sin_a
    perp_y = cos_a
    
    # Calculate the four corners of the body
    # Bottom-left corner (reference edge starting point)
    p1 = pos + np.array([0, 0, 0])
    
    # Bottom-right corner (along the slope - reference edge endpoint)
    p2 = pos + np.array([body_width * cos_a, body_width * sin_a, 0])
    
    # Top-right corner (perpendicular from bottom-right)
    p3 = p2 + np.array([body_height * perp_x, body_height * perp_y, 0])
    
    # Top-left corner (perpendicular from bottom-left)
    p4 = p1 + np.array([body_height * perp_x, body_height * perp_y, 0])
    
    # Find the middle of the opposite edge (top edge: p4-p3)
    anchor_point = (p4 + p3) / 2
    
    # Step perpendicular to the slope by sensor_distance * sensor_radius
    step_distance = sensor_distance * sensor_radius
    sensor_pos = anchor_point + np.array([step_distance * perp_x, step_distance * perp_y, 0])
    
    return sensor_pos[0], sensor_pos[1], sensor_pos[2], anchor_point[0], anchor_point[1], anchor_point[2]


def create_sensor(x, y, z, radius, body_tilt, sensor_anchor_x, sensor_anchor_y, sensor_anchor_z):
    """
    Create a sensor as a no-fill half-circle with a connector line.
    
    Parameters:
    - x, y, z: sensor center position
    - radius: radius of the half-circle
    - body_tilt: slope of the body
    - sensor_anchor_x, sensor_anchor_y, sensor_anchor_z: anchor point coordinates
    
    Returns:
    - Tuple of (sensor_vgroup, connector_end_point)
      - sensor_vgroup: VGroup containing the half-circle and connector line
      - connector_end_point: numpy array [x, y, z] coordinates of the connector line endpoint
    """
    # Fixed default parameters
    sensor_stroke_color = BLACK
    sensor_stroke_width = 4
    connector_length = 0.1
    
    # Convert positions to numpy arrays
    sensor_pos = np.array([x, y, z])
    anchor_pos = np.array([sensor_anchor_x, sensor_anchor_y, sensor_anchor_z])
    
    # Draw dot at sensor position
    sensor_dot = Circle(
        radius=radius,
        fill_color=sensor_stroke_color,
        fill_opacity=1,
        stroke_color=sensor_stroke_color,
        stroke_width=sensor_stroke_width
    )
    sensor_dot.move_to(sensor_pos)
    
    # Draw line from sensor to anchor
    line_to_anchor = Line(
        start=sensor_pos,
        end=anchor_pos,
        stroke_color=sensor_stroke_color,
        stroke_width=sensor_stroke_width
    )
    
    # Calculate perpendicular direction (away from sensor)
    angle = math.atan(body_tilt)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Perpendicular direction pointing away from sensor (negative of the direction pointing to sensor)
    neg_perp_x = sin_a
    neg_perp_y = -cos_a
    
    # Draw connector line from anchor point away from sensor
    connector_end = anchor_pos + np.array([connector_length * neg_perp_x, connector_length * neg_perp_y, 0])
    connector_line = Line(
        start=anchor_pos,
        end=connector_end,
        stroke_color=sensor_stroke_color,
        stroke_width=sensor_stroke_width
    )
    
    # Return group and connector endpoint
    return VGroup(sensor_dot, line_to_anchor, connector_line), connector_end


def create_vehicle(x, y, z, tilt, line_offset):
    """
    Create a complete Braitenberg vehicle with body, wheel, sensor, and connecting wire.
    
    Parameters:
    - x, y, z: position of the vehicle body
    - tilt: rotation angle of the body
    - line_offset: offset percentage for the wheel line (0.0 to 1.0)
    
    Returns:
    - Tuple of (body, wheel1, sensor1, wire1) - all VMobjects to be added to scene
    """
    # Fixed body dimensions
    body_width = 1.5
    body_height = 2.5
    
    # Create body
    body = create_body(x=x, y=y, z=z, width=body_width, height=body_height, tilt=tilt)
    
    # Fixed wheel dimensions
    wheel_width = 0.5
    wheel_height = 1
    
    # Calculate and create wheel
    wheel_x, wheel_y, wheel_z, wheel_tilt, connector_direction = calculate_wheel_center_position(
        x, y, z, body_width, body_height, tilt, wheel_width, wheel_height
    )
    wheel1, wheel1_connector_end = create_wheel_box(
        x=wheel_x, y=wheel_y, z=wheel_z, tilt=wheel_tilt, 
        width=wheel_width, height=wheel_height, 
        line_offset_percent=line_offset, connector_direction=connector_direction
    )
    
    # Fixed sensor radius
    sensor_radius = 0.1
    
    # Calculate and create sensor
    sensor_x, sensor_y, sensor_z, sensor_anchor_x, sensor_anchor_y, sensor_anchor_z = calculate_sensor_center_position(
        x, y, z, body_width, body_height, tilt, sensor_radius
    )
    sensor1, sensor1_connector_end = create_sensor(
        x=sensor_x, y=sensor_y, z=sensor_z, radius=sensor_radius, 
        body_tilt=tilt, sensor_anchor_x=sensor_anchor_x, 
        sensor_anchor_y=sensor_anchor_y, sensor_anchor_z=sensor_anchor_z
    )
    
    # Create connecting wire
    wire1 = Line(start=wheel1_connector_end, end=sensor1_connector_end, stroke_color=BLACK, stroke_width=4)
    
    # Return as a single group
    vehicle = VGroup(body, wheel1, sensor1, wire1)
    return vehicle


class BraitenbergV1neg(MovingCameraScene):
    def construct(self):
        # --- CAMERA SETTINGS ---
        self.camera.frame.set_width(7)
        self.camera.frame.move_to([6, 6, 0])
        self.camera.background_color = "#757575"
        

# region --- LIGHTBULB ---
        lightbulb_off, glow_circles, interval = create_lightbulb(
            x=6, y=10, z=0,
            center_radius=0.5,
            center_color="#FFFFFF",
            socket_width=0.5,
            socket_height=0.85,
            num_glow_rings=16,
            max_glow_radius=8,
            animation_duration=1
        )
        self.add(lightbulb_off)

# endregion --- LIGHTBULB ---     
#    
# region --- Vehicle ---        

        # Draw vehicle at specified position with wheel line offset
        vehicle = create_vehicle(x=5.25, y=5, z=0, tilt=0.0, line_offset=0.02)
        self.add(vehicle)
        self.wait(1)

# endregion --- Vehicle ---   

# region --- TURN ON THE LIGHT ---

        self.remove(lightbulb_off)
        lightbulb_on, glow_circles, interval = create_lightbulb(
            x=6, y=10, z=0,
            center_radius=0.5,
            center_color="#FFDE05",
            socket_width=0.5,
            socket_height=0.85,
            num_glow_rings=16,
            max_glow_radius=8,
            animation_duration=0.3
        )
        self.add(lightbulb_on)
        self.bring_to_front(vehicle)
       # Staggered appearance of glow rings
        for glow in glow_circles:
            self.wait(interval)
            self.add(glow)
            self.bring_to_front(lightbulb_on)
            self.bring_to_front(vehicle)
        
# endregion --- TURN ON THE LIGHT ---

# region --- DRIVE ---

        distance = -4  # Negative = downward movement
        duration = 8
        deceleration_factor = 0.5  # Tuneable parameter: values < 1.0 give deceleration, higher = less deceleration
        
        # Use only the smoother part of the deceleration curve to reduce initial jerkiness
        t_min = 0.15  # Start partway through the curve (smoother region)
        t_max = 1.0
        
        for f in range(60):
                self.remove(vehicle)
                # Calculate normalized time using the smoother curve region
                t_normalized = t_min + (t_max - t_min) * (f / 59.0)
                # Apply deceleration: starting fast, slowing down
                position_factor = t_normalized ** deceleration_factor
                # Scale distance to cover full -4 despite using partial curve
                curve_range = (t_max ** deceleration_factor) - (t_min ** deceleration_factor)
                scaled_distance = distance / curve_range
                # Offset so motion starts at y=5 despite curve offset
                offset = (t_min ** deceleration_factor) * scaled_distance
                # New y position with deceleration
                y_pos = 5 + (position_factor * scaled_distance) - offset
                vehicle = create_vehicle(x=5.25, y=y_pos, z=0, tilt=0.0, line_offset=(0.02 - (f*0.02)))
                self.add(vehicle)
                self.wait(duration/120)

# endregion --- DRIVE ---        
        
        self.wait(1)
