import numpy as np
from visual import Visual
    
class TextureVisual(Visual):
    """Visual that displays a colored texture."""
    
    def points_compound(self, points=None):
        """Compound function for the coordinates of the texture."""
        if points is None:
            points = (-1, -1, 1, 1)
        x0, y0, x1, y1 = points
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        
        position = np.zeros((4,2))
        position[0,:] = (x0, y0)
        position[1,:] = (x1, y0)
        position[2,:] = (x0, y1)
        position[3,:] = (x1, y1)

        return dict(position=position)
        
    def texture_compound(self, texture):
        """Compound variable for the texture data."""
        return dict(tex_sampler=texture)
    
    def initialize_fragment(self):
        """Set the fragment shader code."""
        if self.ndim == 1:
            shader_pointcoord = ".x"
        else:
            shader_pointcoord = ""
        fragment = """
        out_color = texture%dD(tex_sampler, varying_tex_coords%s);
        """ % (self.ndim, shader_pointcoord)
        # print fragment
        self.add_fragment_main(fragment)
    
    def initialize(self, texture=None, points=None,
            mipmap=None, minfilter=None, maxfilter=None):
        
        shape = texture.shape[:2]
        ncomponents = texture.shape[2]
        if shape[0] == 1:
            ndim = 1
        elif shape[0] > 1:
            ndim = 2
        self.ndim = ndim
        
        # four points for a rectangle containing the texture
        # the rectangle is made up by 2 triangles
        self.size = 4
        self.texsize = shape
        self.primitive_type = 'TRIANGLE_STRIP'
        
        if points is None:
            ratio = shape[1] / float(shape[0])
            if ratio < 1:
                a = ratio
                points = (-a, -1., a, 1.)
            else:
                a = 1. / ratio
                points = (-1., -a, 1., a)
        
        # texture coordinates, interpolated in the fragment shader within the
        # rectangle primitive
        if self.ndim == 1:
            tex_coords = np.array([0, 1, 0, 1])
        elif self.ndim == 2:
            tex_coords = np.zeros((4,2))
            tex_coords[0,:] = (0, 1)
            tex_coords[1,:] = (1, 1)
            tex_coords[2,:] = (0, 0)
            tex_coords[3,:] = (1, 0)
        
        # contains the position of the points
        self.add_attribute("position", vartype="float", ndim=2)
        self.add_compound("points", fun=self.points_compound,
            data=points)
        
        # texture coordinates
        self.add_attribute("tex_coords", vartype="float", ndim=ndim,
            data=tex_coords)
        self.add_varying("varying_tex_coords", vartype="float", ndim=ndim)
        
        self.add_texture("tex_sampler", size=shape, ndim=ndim,
            ncomponents=ncomponents,
            mipmap=mipmap,
            minfilter=minfilter,
            maxfilter=maxfilter,
            )
        # HACK: to avoid conflict in GLSL shader with the "texture" function
        # we redirect the "texture" variable here to "tex_sampler" which
        # is the real name of the variable in the shader
        self.add_compound("texture", fun=self.texture_compound, data=texture)

        # pass the texture coordinates to the varying variable
        self.add_vertex_main("""
            varying_tex_coords = tex_coords;
        """)
        
        # initialize the fragment code
        self.initialize_fragment()
            
        