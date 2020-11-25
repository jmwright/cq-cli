import sys
import traceback
import cadquery as cq
from .json_mesh import JsonMesh


def add_component(mesher, shape, largest_dimension, color, loc):
    """
    Adds a single component to the resultant JSON.
    """

    # Protect against this being called with just a blank workplane object in the stack
    if not hasattr(shape, "ShapeType"):
        return

    tess = shape.tessellate(0.001)
    
    # Use the location, if there is one
    if loc is not None:
        loc_x = loc.X()
        loc_y = loc.Y()
        loc_z = loc.Z()
    else:
        loc_x = 0.0
        loc_y = 0.0
        loc_z = 0.0

    # Add vertices
    for v in tess[0]:
        mesher.addVertex(v.x + loc_x, v.y + loc_y, v.z + loc_z)

    # Add triangles
    for ixs in tess[1]:
        mesher.addTriangle(*ixs)

    # Add CadQuery-reported vertices
    for vert in shape.Vertices():
        mesher.addCQVertex(vert.X, vert.Y, vert.Z)

    # Make sure that the largest dimension is represented accurately for camera positioning
    mesher.addLargestDim(largest_dimension)

    # Make sure that the color is set correctly for the current component
    if color is None: color = cq.Color(1.0, 0.36, 0.05, 1.0)
    mesher.addColor(color.wrapped.GetRGB().Red(), color.wrapped.GetRGB().Green(), color.wrapped.GetRGB().Blue(), color.wrapped.Alpha())

    # Snapshot the current vertices and triangles as a component
    mesher.addComponent()


def handle_shape(mesher, shape, color, loc):
    """
    Common code for handling a Compound vs a Shape.
    """
    # If the shape is a compound we have to extract the subshapes
    if shape.ShapeType() == "Compound":
        for s in shape.__iter__():
            add_component(mesher, s, cq.Workplane().add(s).largestDimension(), color, loc)
    else:
        # We are dealing with a stock shape object, so just add it
        add_component(mesher, shape, cq.Workplane().add(shape).largestDimension(), color, loc)


def convert(build_result, output_file=None, error_file=None):
    """
    Called by the cq-cli plugin system when requested by the user.
    """
    # We need to do a broad try/catch to let the user know if something higher-level fails
    try:
        mesher = JsonMesh()

        if build_result.success:
            # Display all the results that the caller
            for result in build_result.results:
                # Extract all the individual components of the assembly and add them to the JSON
                if isinstance(result.shape, cq.Assembly):
                    # Get the parent location of the assembly
                    parent_loc = result.shape.loc.wrapped.Transformation().TranslationPart()

                    # Get the parent color to use as the default
                    parent_color = result.shape.color

                    # Step through the shapes/assemblies that were added to this assembly by calling add()
                    for assy in result.shape.children:
                        # Get the color to use for the shape
                        color = assy.color
                        loc = assy.loc.wrapped.Transformation().TranslationPart()

                        # Extract the shape(s) from the added assembly
                        for shape in assy.shapes:
                            handle_shape(mesher, shape, color, loc)

                    # Still need to add the base shape that the assembly was created from
                    for shape in result.shape.shapes:
                        # If the shape is a compound we have to extract the subshapes
                        handle_shape(mesher, shape, parent_color, parent_loc)
                else:
                    # Add the single CQ shape to the JSON
                    add_component(mesher, result.shape.val(), result.shape.largestDimension(), None, None)

            # If an output file was specified write to it, otherwise print the JSON to stdout
            if output_file != None:
                # Write the mesh to the file
                with open(output_file, 'w') as file:
                    file.write(mesher.toJson())

                # Let the process know we are done writing to the file
                with open(output_file, 'a') as file:
                    file.write("semb_process_finished")
            else:
                print(mesher.toJson())
                print("semb_process_finished")
        else :
            # Re-throw the exception so that it will be caught and formatted correctly
            raise(build_result.exception)

    except Exception:
        out_tb = traceback.format_exc()

        # If there is an error file specified write to that, otherwise write to stderr
        if error_file != None:
            # We need to let the user know there was a build exception
            with open(error_file, 'w') as file:
                file.write("Component Generation Error: %s" % str(out_tb))

            # Let the process know we are done writing to the file
            with open(error_file, 'a') as file:
                file.write("semb_process_finished")
        else:
            print("Conversion codec error: " + str(out_tb), file=sys.stderr)

        return None

    return None