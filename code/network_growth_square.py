from manim import *
import numpy as np
import csv

class NetworkGrowthSquare(MovingCameraScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.network_data = []
        self.dots = []  # Keep track of all dots added
        self.orange = "#E79E16"
        self.current_orange_elements = []  # Track current orange dot and connections
    
    def load_network_data(self):
        """Load network data from CSV file"""
        with open('network_data.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.network_data.append(row)
    
    def update_histogram(self, node_index, histogram_duration=15/15):
        """Keep original timing slot where histogram updates used to run."""
        _ = node_index
        if histogram_duration > 0:
            self.wait(histogram_duration)
    
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
        if node_index < 9:
            dot_duration = 60/125
            connection_duration = 30/125
            histogram_duration = 30/125
            histo_wait_duration = 0/125
        else:
            dot_duration = 30/125
            connection_duration = 15/125
            histogram_duration = 15/125
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
        elif connection_duration > 0:
            self.wait(connection_duration)
        
        # Update histogram based on current degree distribution
        self.update_histogram(node_index, histogram_duration)
        
        if histo_wait_duration > 0:
            self.wait(histo_wait_duration)
        
        return dot
    
    def construct(self):
        # --- CAMERA SETTINGS ---
        # 16:9 landscape aspect ratio
        self.camera.frame.set_width(9)
        self.camera.frame.set_height(9)
        self.camera.frame.move_to([4.25, 3.5, 0])
        self.camera.background_color = "#000000"
        
        # --- COORDINATE SYSTEM ---
        # (Left-side axes removed, but coordinate mapping still applies to dots and connections)
        
        # --- LOAD NETWORK DATA ---
        self.load_network_data()
        #self.wait(480/125)
        # --- PLOT NETWORK NODES ---
        for node_index in range(60):
            self.add_node(node_index)

        self.wait(120/125)
