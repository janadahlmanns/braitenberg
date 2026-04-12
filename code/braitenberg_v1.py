from manim import *
import numpy as np

class BraitenbergV1(MovingCameraScene):
    def construct(self):
        # --- CAMERA SETTINGS ---
        self.camera.frame.set_width(14)
        self.camera.frame.move_to([6, 6, 0])
        self.camera.background_color = "#000000"
        
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
        
        # --- LIGHTBULB AT (6, 6, 0) ---
        lightbulb_position = np.array([6, 10, 0])
        
        # Create the central dot (lightbulb)
        lightbulb = Circle(radius=0.5, fill_color="#FFDE05", fill_opacity=1, 
                          stroke_color="#000000", stroke_width=6)
        lightbulb.move_to(lightbulb_position)
        
        # Create glow/shine effect: concentric circles with decreasing opacity
        glow_circles = []
        max_glow_radius = 4
        num_glow_rings = 15
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
        
        # Add lightbulb at t=0 without animation
        self.add(lightbulb)
        
        # Staggered appearance: each circle appears after the interval
        for glow in glow_circles:
            self.wait(interval)
            self.add(glow)
            self.bring_to_front(lightbulb)
        
            
        self.wait(3)
