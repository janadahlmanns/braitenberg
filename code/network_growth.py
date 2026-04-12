from manim import *
import numpy as np
import csv

class NetworkGrowth(MovingCameraScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.network_data = []
        self.dots = []  # Keep track of all dots added
        self.histogram_bars = {}  # {degree: bar_object}
        self.orange = "#E79E16"
        self.current_orange_elements = []  # Track current orange dot and connections
    
    def load_network_data(self):
        """Load network data from CSV file"""
        with open('network_data.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.network_data.append(row)
    
    def init_histogram(self):
        """Initialize all 25 histogram bars with height 0"""
        for degree in range(1, 26):  # Degrees 1-25
            # Map degree (0-25) to right-side x-axis (10.25-15.25 in manim coords)
            x_pos = 10.25 + (degree / 25.0) * 5.0
            # Bar width of 1 unit on the right-side axis = 0.2 in manim coordinates
            bar_width = (1.0 / 25.0) * 5.0  # = 0.2
            bar_height = 0  # Start at height 0
            y_pos = 0.5 + bar_height / 2
            
            bar = Rectangle(width=bar_width, height=bar_height, 
                           fill_color=WHITE, fill_opacity=1, stroke_width=0)
            bar.move_to([x_pos, y_pos, 0])
            self.histogram_bars[degree] = bar
            self.add(bar)
    
    def update_histogram(self, node_index, histogram_duration=15/15):
        """Update histogram based on degree data from current node"""
        from collections import Counter
        
        node_data = self.network_data[node_index]
        
        # Get degree values for all added nodes (indices 0 to node_index)
        degrees = []
        for i in range(node_index + 1):
            degree_key = f'degree_at_node_{i}'
            if degree_key in node_data:
                degree = int(float(node_data[degree_key]))
                if degree > 0:  # Only count non-zero degrees
                    degrees.append(degree)
        
        # Count frequency of each degree
        degree_counts = Counter(degrees)
        
        # Create replacement transform animations for all bars
        replacement_animations = []
        bars_to_update = []
        
        for degree in range(1, 26):  # Degrees 1-25
            count = degree_counts.get(degree, 0)
            
            # Map degree (0-25) to right-side x-axis (10.25-15.25 in manim coords)
            x_pos = 10.25 + (degree / 25.0) * 5.0
            # Bar width of 1 unit on the right-side axis = 0.2 in manim coordinates
            bar_width = (1.0 / 25.0) * 5.0  # = 0.2
            bar_height = count * (7.0 / 35.0)  # Scale count (0-35) to axis span of 7.0
            y_pos = 0.5 + bar_height / 2
            
            old_bar = self.histogram_bars[degree]
            new_bar = Rectangle(width=bar_width, height=bar_height,
                               fill_color=WHITE, fill_opacity=1, stroke_width=0)
            new_bar.move_to([x_pos, y_pos, 0])
            
            replacement_animations.append(ReplacementTransform(old_bar, new_bar, run_time=histogram_duration))
            bars_to_update.append((degree, new_bar))
        
        # Play all bar updates simultaneously
        if replacement_animations:
            self.play(*replacement_animations)
        
        # Update dictionary with new bar objects
        for degree, new_bar in bars_to_update:
            self.histogram_bars[degree] = new_bar
    
    def add_node(self, node_index):
        """Create, add to scene, and return a dot for the given node index"""
        # Flatten previous orange elements to white
        for element in self.current_orange_elements:
            element.set_fill(WHITE)
            # Only set stroke to white for connections (Lines), not dots (Circles)
            if isinstance(element, Line):
                element.set_stroke(WHITE)
        self.current_orange_elements = []
        
        # Set animation durations based on node_index
        if node_index < 5:
            dot_duration = 15/15
            connection_duration = 10/15
            histogram_duration = 10/15
            histo_wait_duration = 5/15
        else:
            dot_duration = 3/15
            connection_duration = 2/15
            histogram_duration = 2/15
            histo_wait_duration = 0
        
        node_data = self.network_data[node_index]
        x_orig = float(node_data['x'])
        y_orig = float(node_data['y'])
        
        # Normalize from original range [-5, 5] for x and [-3, 3] for y to [0, 2]
        x_normalized = ((x_orig + 5) / 10) * 2  # [-5, 5] -> [0, 1] -> [0, 2]
        y_normalized = ((y_orig + 3) / 6) * 2   # [-3, 3] -> [0, 1] -> [0, 2]
        
        # Scale to Manim coordinates [0.25, 8.25] for x and [0.5, 8.5] for y
        x_manim = 0.28 +  x_normalized * 4
        y_manim = -0.25 + y_normalized * 4
        
        # Create circle with black stroke width 2 and orange fill
        dot = Circle(radius=0.15, stroke_color=BLACK, stroke_width=2, fill_color=self.orange, fill_opacity=1)
        dot.move_to([x_manim, y_manim, 0])
        self.current_orange_elements.append(dot)
        
        # Retrieve and draw connections to target nodes
        connections = []
        for i in range(20):  # Max 20 targets per node
            target_x_key = f'target_{i}_x'
            target_y_key = f'target_{i}_y'
            
            if target_x_key not in node_data:
                break  # No more targets
            
            target_x_str = node_data[target_x_key]
            target_y_str = node_data[target_y_key]
            
            # Skip empty or None values
            if not target_x_str or target_x_str == 'None':
                break
            
            try:
                target_x_orig = float(target_x_str)
                target_y_orig = float(target_y_str)
                
                # Normalize target coordinates
                target_x_normalized = ((target_x_orig + 5) / 10) * 2
                target_y_normalized = ((target_y_orig + 3) / 6) * 2
                
                # Scale to Manim coordinates
                target_x_manim = 0.28 + target_x_normalized * 4
                target_y_manim = -0.25 + target_y_normalized * 4
                
                # Create line from current node to target
                line = Line(start=np.array([x_manim, y_manim, 0]),
                           end=np.array([target_x_manim, target_y_manim, 0]),
                           stroke_color=self.orange, stroke_width=4)
                connections.append(line)
                self.current_orange_elements.append(line)
            except (ValueError, KeyError):
                break
        
        # Fade in the dot first
        self.play(FadeIn(dot, run_time=dot_duration))
        
        # Store dot and bring to front
        self.dots.append(dot)
        self.bring_to_front(dot)
        
        # Draw connection lines growing from the new node simultaneously
        if connections:
            # Set z-index before animating
            for conn in connections:
                conn.set_z_index(-1)
            create_animations = [Create(conn, run_time=connection_duration) for conn in connections]
            self.play(*create_animations)
        
        # Update histogram based on current degree distribution
        self.update_histogram(node_index, histogram_duration)
        
        if histo_wait_duration > 0:
            self.wait(histo_wait_duration)
        
        return dot
    
    def construct(self):
        # --- CAMERA SETTINGS ---
        # 16:9 landscape aspect ratio
        self.camera.frame.set_width(16)
        self.camera.frame.set_height(9)
        self.camera.frame.move_to([8, 3.5, 0])
        self.camera.background_color = "#000000"
        
        # --- COORDINATE SYSTEM ---
        # (Left-side axes removed, but coordinate mapping still applies to dots and connections)
        
        # --- LOAD NETWORK DATA ---
        self.load_network_data()
        
        # --- HISTOGRAM COORDINATE SYSTEM (Right Pane) ---
        # X-axis (width)
        hist_x_axis = Line(start=np.array([10.25, 0.5, 0]), end=np.array([15.25, 0.5, 0]), stroke_color=WHITE, stroke_width=2)
        
        # Y-axis (height - degree range 0 to 25)
        hist_y_axis = Line(start=np.array([10.25, 0.5, 0]), end=np.array([10.25, 7.5, 0]), stroke_color=WHITE, stroke_width=2)
        
        # Y-axis ticks and labels (0 to 35 count range mapped to 0.5-7.5 axis)
        hist_y_positions = np.linspace(0.5, 7.5, 8)  # 8 ticks for 0, 5, 10, 15, 20, 25, 30, 35
        hist_y_values_labels = [0, 5, 10, 15, 20, 25, 30, 35]
        
        hist_y_ticks = []
        hist_y_labels = []
        
        for pos, val in zip(hist_y_positions, hist_y_values_labels):
            tick = Line(start=np.array([10.25, pos, 0]), end=np.array([10.05, pos, 0]), stroke_color=WHITE, stroke_width=1.5)
            hist_y_ticks.append(tick)
            
            label = Text(f"{val}", font_size=28, color=WHITE, font="sans-serif")
            label.move_to([9.55, pos, 0])
            hist_y_labels.append(label)
        
        # Add unlabeled ticks at every integer count (0-35)
        hist_y_minor_ticks = []
        for count in range(0, 36):
            y_manim = 0.5 + (count / 35.0) * 7.0
            tick = Line(start=np.array([10.25, y_manim, 0]), end=np.array([10.15, y_manim, 0]), stroke_color=WHITE, stroke_width=1)
            hist_y_minor_ticks.append(tick)
        
        # X-axis ticks and labels (for degree values 0-25)
        hist_x_positions = np.linspace(10.25, 15.25, 6)  # 6 ticks
        hist_x_values_labels = [0, 5, 10, 15, 20, 25]  # Degree values
        
        hist_x_ticks = []
        hist_x_labels = []
        
        for pos, val in zip(hist_x_positions, hist_x_values_labels):
            tick = Line(start=np.array([pos, 0.5, 0]), end=np.array([pos, 0.3, 0]), stroke_color=WHITE, stroke_width=1.5)
            hist_x_ticks.append(tick)
            
            label = Text(f"{val}", font_size=28, color=WHITE, font="sans-serif")
            label.move_to([pos, 0.05, 0])
            hist_x_labels.append(label)
        
        # Add unlabeled ticks at every integer degree
        hist_x_minor_ticks = []
        for degree in range(0, 26):
            x_manim = 10.25 + (degree / 25.0) * 5.0
            tick = Line(start=np.array([x_manim, 0.5, 0]), end=np.array([x_manim, 0.35, 0]), stroke_color=WHITE, stroke_width=1)
            hist_x_minor_ticks.append(tick)
        
        # Add histogram coordinate system
        self.add(hist_x_axis, hist_y_axis)
        self.add(*hist_y_ticks, *hist_y_labels)
        self.add(*hist_y_minor_ticks)
        self.add(*hist_x_ticks, *hist_x_labels)
        self.add(*hist_x_minor_ticks)
        
        # Add axis labels
        x_axis_label = Text("number of connections", font_size=32, color=WHITE, font="sans-serif")
        x_axis_label.move_to([12.75, -0.5, 0])
        self.add(x_axis_label)
        
        y_axis_label = Text("count", font_size=32, color=WHITE, font="sans-serif")
        y_axis_label.rotate(np.pi / 2)
        y_axis_label.move_to([9.0, 4.0, 0])
        self.add(y_axis_label)
        
        # Initialize histogram bars with height 0
        self.init_histogram()

        # --- PLOT NETWORK NODES ---
        for node_index in range(60):
            self.add_node(node_index)

        # Create smooth histogram curve over the bars
        from scipy.interpolate import CubicSpline
        from collections import Counter
        
        final_node_index = 59  # Last node added (0-indexed)
        node_data = self.network_data[final_node_index]
        
        # Get final degree counts
        degrees = []
        for i in range(final_node_index + 1):
            degree_key = f'degree_at_node_{i}'
            if degree_key in node_data:
                degree = int(float(node_data[degree_key]))
                if degree > 0:
                    degrees.append(degree)
        
        degree_counts = Counter(degrees)
        
        # Create points for curve
        curve_points = []
        for degree in range(0, 26):  # Include 0 to 25
            count = degree_counts.get(degree, 0)
            bar_height = count * (7.0 / 35.0)  # Map to 0-35 scale
            x_pos = 10.25 + (degree / 25.0) * 5.0
            y_pos = 0.5 + bar_height
            curve_points.append([x_pos, y_pos])
        
        x_vals = [p[0] for p in curve_points]
        y_vals = [p[1] for p in curve_points]
        
        # Create curve directly from data points without any smoothing
        curve_points_array = np.array([[x_vals[i], y_vals[i], 0] for i in range(len(x_vals))])
        
        # Create curve VMobject
        curve = VMobject()
        curve.set_points_as_corners(curve_points_array)
        curve.set_stroke(color=self.orange, width=6)
        
        self.play(Create(curve, run_time=15/15))

        self.wait(2)
