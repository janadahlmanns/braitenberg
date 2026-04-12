from manim import *
import numpy as np

class GridTemplate(MovingCameraScene):
    def construct(self):
        # --- CAMERA SETTINGS ---
        self.camera.frame.set_width(14)
        self.camera.frame.move_to([6, 6, 0])
        self.camera.background_color = "#8bc08c"
        
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
        self.wait(2)
