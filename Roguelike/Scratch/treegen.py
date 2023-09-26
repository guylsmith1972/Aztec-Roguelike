from L_system import LSystem
from turtle3d import Turtle3D

import math
import random
import vtk


def generic_tree():
    # r = growing root
    # R = grown root
    # s = growing stem
    # S = grown stem
    # T = grown trunk
    # b = growing branch
    # B = grown branch
    # w = growing twing
    # W = grown twig
    # c = growing leaf cluster
    # L = grown leaf
    rules = {
        'r': [('R s{1,1}', 1)],
        's': [('S{1,2} s{0,1}', 1)],
        'S': [('T [b]{1,3}', 1)],
        'b': [('B [w]{1,6}', 1)],
        'w': [('W [c]{3,7}', 1)],
        'c': [('W [L]{1,5}', 1)]
    }
    return LSystem(rules)


def render_lsystem_to_file(lsystem_string, params, filename):
    '''
    Render the L-system to a 3D image using VTK.
    
    Args:
    - lsystem_string (str): The string representation of the L-system.
    - params (dict): Parameters for the 3D model.
    - filename (str): Path to save the rendered image.
    
    Note: This function requires VTK to be installed and is a template. 
    Adjustments might be required based on the specific requirements and environment.
    '''
    def compute_transformations(start, end):
        '''
        Compute the translation and rotation needed to position and orient a cylinder
        from the start point to the end point.
        '''
        # Default cylinder orientation (e.g., aligned with Z-axis)
        default_orientation = [0, 0, 1]
    
        # Compute direction vector from start to end
        direction = [end[i] - start[i] for i in range(3)]
    
        # Normalize the direction vector
        length = sum([d**2 for d in direction])**0.5
        direction = [d/length for d in direction]
    
        # Compute the rotation axis using cross product
        axis = [
            default_orientation[1] * direction[2] - default_orientation[2] * direction[1],
            default_orientation[2] * direction[0] - default_orientation[0] * direction[2],
            default_orientation[0] * direction[1] - default_orientation[1] * direction[0]
        ]
    
        # Compute the angle between default orientation and direction (in degrees)
        dot_product = sum([default_orientation[i] * direction[i] for i in range(3)])
        angle = math.degrees(math.acos(dot_product))
    
        # Compute the midpoint for translation
        midpoint = [(start[i] + end[i]) / 2.0 for i in range(3)]
    
        return midpoint, axis, angle

    # Initialize the 3D turtle
    turtle = Turtle3D()

    # Interpret the L-system string and record segments and leaf positions
    segments = []
    leaves = []

    for char in lsystem_string:
        if char in ['T', 'B']:
            start, end = turtle.forward(params['segment_length'])
            segments.append((start, end))
        elif char == '[':
            turtle.push_state()
            turtle.turn(yaw=params['branching_angle']['yaw'], roll=params['branching_angle']['roll'], pitch=params['branching_angle']['pitch'])
        elif char == ']':
            turtle.pop_state()
            turtle.turn(yaw=-params['branching_angle']['yaw'], roll=-params['branching_angle']['roll'], pitch=-params['branching_angle']['pitch'])
        elif char == 'L':
            leaves.append(turtle.position)
            
    print(segments)

    # Use VTK to create cylinders for segments and spheres for leaves
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    for start, end in segments:
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetHeight(params['segment_length'])
        cylinder.SetRadius(params['segment_thickness'])
        cylinder.SetResolution(20)

        transform = vtk.vtkTransform()
        translation, rotation_axis, rotation_angle = compute_transformations(start, end)
        transform.Translate(*translation)
        transform.RotateWXYZ(rotation_angle, *rotation_axis)

        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputConnection(cylinder.GetOutputPort())
        transform_filter.SetTransform(transform)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transform_filter.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(params['colors']['trunk'])

        ren.AddActor(actor)

    for leaf_pos in leaves:
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(params['leaf_size'])

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetPosition(leaf_pos)
        actor.GetProperty().SetColor(params['colors']['leaf'])

        ren.AddActor(actor)

    ren.SetBackground(1, 1, 1)
    renWin.SetSize(512, 512)

    camera = ren.GetActiveCamera()
    camera.SetPosition(50, 50, 50)
    camera.SetFocalPoint(0, 0, 0)

    renWin.Render()

    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename)
    writer.SetInputData(w2if.GetOutput())
    writer.Write()



def test_lsystem():
    lsystem = generic_tree()

    rng = random.Random(42)
    result = lsystem.iterate('r', 20, rng)
    print(result)
    # render_lsystem_to_file(result, {'branching_angle': {'yaw': 20, 'roll': 20, 'pitch': 20}, 'segment_length': 10, 'segment_thickness': 1, 'leaf_size': 0.1, 'colors': {'trunk': (0,0,0), 'leaf': (0,1,0)}}, 'test_article.png')
    

if __name__ == '__main__':
    test_lsystem()
