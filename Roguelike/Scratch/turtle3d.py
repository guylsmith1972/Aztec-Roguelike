import numpy as np


class Turtle3D:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0])
        self.orientation = np.array([0.0, 1.0, 0.0])  # Pointing upwards initially
        self.state_stack = []

    def forward(self, distance):
        """Move forward by a certain distance and return the old and new position."""
        old_position = self.position.copy()
        self.position += self.orientation * distance
        return old_position, self.position.copy()

    def turn(self, pitch, yaw, roll):
        """Rotate the turtle by the specified angles (in degrees)."""
        # Convert angles to radians
        pitch, yaw, roll = np.radians(pitch), np.radians(yaw), np.radians(roll)
        
        # Rotation matrices
        Rx = np.array([[1, 0, 0],
                       [0, np.cos(pitch), -np.sin(pitch)],
                       [0, np.sin(pitch), np.cos(pitch)]])
        
        Ry = np.array([[np.cos(yaw), 0, np.sin(yaw)],
                       [0, 1, 0],
                       [-np.sin(yaw), 0, np.cos(yaw)]])
        
        Rz = np.array([[np.cos(roll), -np.sin(roll), 0],
                       [np.sin(roll), np.cos(roll), 0],
                       [0, 0, 1]])
        
        # Apply rotations
        R = np.dot(Rz, np.dot(Ry, Rx))
        self.orientation = np.dot(R, self.orientation)

    def push_state(self):
        """Save the current state."""
        self.state_stack.append((self.position.copy(), self.orientation.copy()))

    def pop_state(self):
        """Restore the last saved state."""
        self.position, self.orientation = self.state_stack.pop()


def main():
    turtle = Turtle3D()
    segments = []
    segments.append(turtle.forward(10))
    turtle.turn(30, 45, 0)
    segments.append(turtle.forward(10))

    print(segments)
    

if __name__ == '__main__':
    main()
    