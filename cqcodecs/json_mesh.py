semb_json_template = (
"""
{
"metadata": {
"format": "cadquery-custom",
"formatVersion": 1.0,
"generatedBy": "semblage-server"
},
"components": %(components)s
}
""")

component_template = (
"""
{
"id": -1,
"vertexCount": %(nVertices)d,
"triangleCount": %(nTriangles)d,
"normalCount": 0,
"colorCount": 0,
"uvCount": 0,
"materials": 1,
"largestDim": %(largestDim)d,
"vertices": %(vertices)s,
"triangles": %(triangles)s,
"normals": [],
"uvs": [],
"color": %(color)s,
"cq_vertices": [],
"cq_edges": [],
"cq_faces": []
}
""")

cq_vertex_template = (
"""
{
    "id": -1,
    "x": -1,
    "y": -1,
    "z": -1
}
"""
)

cq_edge_template = (
"""
{
    "id": -1,
    "type": "line",
    "start": "None",
    "end": "None",
    "center": "None",
    "radius": "None" 
}
""")

cq_face_template = (
"""
{
    "id": -1,
    "vertices": [],
    "edges": []
}
""")

class JsonMesh(object):
    components = []
    vertices = []
    triangles = []
    nVertices = 0
    nTriangles = 0
    largestDim = -1
    color = [] # rgba

    def addVertex(self, x, y, z):
        self.nVertices += 1
        self.vertices.extend([x, y, z])

    """
    Add triangle composed of the three provided vertex indices
    """
    def addTriangle(self, i, j, k):
        self.nTriangles += 1
        self.triangles.extend([int(i), int(j), int(k)])

    """
    Adds the largest dimension for the current component
    """
    def addLargestDim(self, dimension):
        self.largestDim = dimension

    """
    Adds the red, green blue alpha colors to the JSON mesh.
    """
    def addColor(self, r, g, b, a):
        self.color = [r, g, b, a]

    """
    Separates the current set of vertices, triangles, etc into a separate component.
    """
    def addComponent(self):
        template = component_template % {
            "vertices": str(self.vertices),
            "triangles": str(self.triangles),
            "nVertices": self.nVertices,
            "nTriangles": self.nTriangles,
            "largestDim": self.largestDim,
            "color": self.color
        }

        self.components.append(template)

        # Reset for the next component
        self.vertices = []
        self.triangles = []
        self.nVertices = 0
        self.nTriangles = 0
        self.largestDim = -1

    """
    Get a json model from this model.
    For now we'll forget about colors, vertex normals, and all that stuff
    """
    def toJson(self):
        return_json = semb_json_template % {
            "components": str(self.components),
        }
        return_json = return_json.replace("'", "")
        return_json = return_json.replace("\\n", "")

        return return_json