from manim import *
import numpy as np

class BraitenbergV1(MovingCameraScene):
    def construct(self):
        # --- CAMERA SETTINGS ---
        self.camera.frame.set_width(14)
        self.camera.frame.move_to([6, 6, 0])
        self.camera.background_color = "#2F9137"
        
        # Create horizontal white lines at various y values with width 2
        y_values = [0, 2, 4, 6, 8, 10, 12]
        lines = []
        labels = []
        
        for y in y_values:
            line = Line(start=np.array([0, y, 0]), end=np.array([12, y, 0]), stroke_color=WHITE, stroke_width=2)
            lines.append(line)
            
            # Create label at middle of line, slightly above
            label = Text(f"y={y}", font_size=24, color=WHITE)
            label.move_to([5, y + 0.4, 0])
            labels.append(label)
        
        # Create vertical white lines at various x values with width 2
        x_values = [0, 2, 4, 6, 8, 10, 12]
        
        for x in x_values:
            line = Line(start=np.array([x, 0, 0]), end=np.array([x, 12, 0]), stroke_color=WHITE, stroke_width=2)
            lines.append(line)
            
            # Create label at 1/3 the length, slightly to the right
            label = Text(f"x={x}", font_size=24, color=WHITE)
            label.move_to([x + 0.4, 10/3, 0])
            labels.append(label)
        
        # Display all lines and labels
        self.play(*[Create(line) for line in lines], *[Create(label) for label in labels])



# --- LIGHTBULB ---
        lightbulb_position = np.array([8, 10, 0])
        
        # Create the central dot (center_circle)
        center_circle = Circle(radius=0.5, fill_color="#FFDE05", fill_opacity=1, 
                          stroke_color="#000000", stroke_width=6)
        center_circle.move_to(lightbulb_position)
        
        # Create glow/shine effect: concentric circles with decreasing opacity
        glow_circles = []
        max_glow_radius = 4.5
        num_glow_rings = 10
        animation_duration = 1.5  # Total time for all circles to appear
        interval = animation_duration / num_glow_rings  # Time between each circle
        
        for i in range(1, num_glow_rings + 1):
            radius = (i / num_glow_rings) * max_glow_radius
            # Opacity decreases with distance (inverse square-like falloff)
            opacity = max(0, 1 - (i / num_glow_rings) ** 1.5)
            
            glow = Circle(radius=radius, fill_color="#FFDE05", fill_opacity=opacity,
                         stroke_color="#000000", stroke_opacity=0, stroke_width=0)
            glow.move_to(lightbulb_position)
            glow_circles.append(glow)
        

        # Socket parameters
        # Box Position: middle of top edge at lightbulb center [6, 10, 0]
        box_width = 0.5
        box_height = 0.75
        box_z = 0
        box_x = lightbulb_position[0] - box_width / 2  # So middle of top edge x = lightbulb x
        box_y = lightbulb_position[1] - box_height     # So top edge y = lightbulb y
        
        # Line parameters
        line_start_fraction = 0.25  # 1/4 along bottom edge
        line_slope = 1/5 # Jana, stop obsessing, 1/5 looks good enough.
        line_vertical_spacing = 0.125
        
        # Create box: no fill, black stroke
        box = Rectangle(
            width=box_width, 
            height=box_height, 
            stroke_color=BLACK, 
            stroke_width=4, 
            fill_opacity=0
        )
        box.move_to([box_x + box_width/2, box_y + box_height/2, box_z])
        
        # Calculate first line's y-intercept (b value)
        # First line starts at (box_x + line_start_fraction * box_width, box_y)
        line1_start_x = box_x + line_start_fraction * box_width
        line1_start_y = box_y
        b_first = line1_start_y - line_slope * line1_start_x
        
        # Function to get line-box intersection points
        def get_line_intersection_in_box(b_value, slope, x_min, y_min, x_max, y_max):
            """
            Returns (start_point, end_point) of line within box, or None if no intersection.
            Line equation: y = slope * x + b_value
            """
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
            
            # Sort by x-coordinate to get start and end points
            intersection_points.sort(key=lambda p: p[0])
            return intersection_points[0], intersection_points[-1]
        
        # Create all parallel lines until they don't intersect the box
        lines_to_add = []
        
        # First, the center line (n=0)
        result = get_line_intersection_in_box(b_first, line_slope, box_x, box_y, box_x + box_width, box_y + box_height)
        if result is not None:
            start_pt, end_pt = result
            line = Line(
                start=np.array([start_pt[0], start_pt[1], box_z]),
                end=np.array([end_pt[0], end_pt[1], box_z]),
                stroke_color=BLACK,
                stroke_width=4
            )
            lines_to_add.append(line)
        
        # Positive direction (upward)
        n = 1
        while True:
            b_pos = b_first + n * line_vertical_spacing
            result = get_line_intersection_in_box(b_pos, line_slope, box_x, box_y, box_x + box_width, box_y + box_height)
            if result is None:
                break
            start_pt, end_pt = result
            line = Line(
                start=np.array([start_pt[0], start_pt[1], box_z]),
                end=np.array([end_pt[0], end_pt[1], box_z]),
                stroke_color=BLACK,
                stroke_width=4
            )
            lines_to_add.append(line)
            n += 1
        
        # Negative direction (downward)
        n = 1
        while True:
            b_neg = b_first - n * line_vertical_spacing
            result = get_line_intersection_in_box(b_neg, line_slope, box_x, box_y, box_x + box_width, box_y + box_height)
            if result is None:
                break
            start_pt, end_pt = result
            line = Line(
                start=np.array([start_pt[0], start_pt[1], box_z]),
                end=np.array([end_pt[0], end_pt[1], box_z]),
                stroke_color=BLACK,
                stroke_width=4
            )
            lines_to_add.append(line)
            n += 1
        
        # Add lightbulb at t=0 without animation
        # Create a group containing the box, lines, and center circle
        lightbulb = VGroup(box, *lines_to_add, center_circle)
        self.add(lightbulb)
        
        # Staggered appearance: each circle appears after the interval
        for glow in glow_circles:
            self.wait(interval)
            self.add(glow)
            self.bring_to_front(lightbulb)
        
            
        self.wait(3)
