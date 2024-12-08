import xml
import xml.etree
import xml.etree.ElementTree
from syntax_tree import Node
from ast import literal_eval
    
class SemanticError(Exception):
    pass

def semanticAssert(condition, message):
    if not condition:
        raise SemanticError(message)
    
class Context:
    def __init__(self, fill_color, stroke_color, stroke_width, frame):
        self.fill_color = fill_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.frame = frame
        
    def copy(self):
        return Context(self.fill_color, self.stroke_color, self.stroke_width, self.frame)

class Layer:
    def to_svg(self) -> xml.etree.ElementTree:
        raise NotImplementedError()
    
class Canvas(Layer):
    def __init__(self, width, height, length):
        self.width = width
        self.height = height
        self.length = length
        self.children = []
        
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        svg = xml.etree.ElementTree.Element('svg', xmlns='http://www.w3.org/2000/svg', version='1.1',
                                            width=str(self.width), height=str(self.height))
        
        for child in self.children:
            svg.append(child.to_svg(ctx))
        
        return svg
    
def get_color(node):
    semanticAssert(node.name == 'Solid', 'Only solid colors are supported')
    return node.children[0].children[0].name.strip('\'"')
    
class Fill(Layer):
    def __init__(self, color):
        self.color = get_color(color)
        self.children = []
        
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        ctx_copy = ctx.copy()
        ctx_copy.fill_color = self.color
        
        g = xml.etree.ElementTree.Element('g')
        for child in self.children:
            g.append(child.to_svg(ctx_copy))
            
        return g
            
class Stroke(Layer):
    def __init__(self, color=None, width=None):
        self.color = get_color(color) if color is not None else None
        self.width = width
        self.children = []
        
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        ctx_copy = ctx.copy()
        if self.color is not None:
            ctx_copy.stroke_color = self.color
        
        if self.width is not None:
            ctx_copy.stroke_width = self.width
        
        g = xml.etree.ElementTree.Element('g')
        for child in self.children:
            g.append(child.to_svg(ctx_copy))
            
        return g
    
class Translate(Layer):
    def __init__(self, x, y, start=None, end=None, length=None):
        self.x = x
        self.y = y
        self.children = []
        
        if start is None and end is None and length is None:
            self.start = None
            self.length = None
            self.animated = False
        else:
            self.animated = True
            if start is not None and end is not None:
                semanticAssert(length is None, 'Cannot specify both start and end and length')
                self.start = start
                self.length = end - start + 1
                
            elif start is not None and length is not None:
                self.start = start
                self.length = length
                
            elif end is not None and length is not None:
                self.length = length
                self.start = end - length + 1
                
            else:
                raise SemanticError('Must specify two of start, end, and length, or none')
        
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        if self.animated:
            t = max(0, min(1, (ctx.frame - self.start) / self.length))
            x = self.x * t
            y = self.y * t
            g = xml.etree.ElementTree.Element('g', transform=f'translate({x}, {y})')
        else:
            g = xml.etree.ElementTree.Element('g', transform=f'translate({self.x}, {self.y})')
            
        for child in self.children:
            g.append(child.to_svg(ctx))
            
        return g
    
class Rectangle(Layer):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        rect = xml.etree.ElementTree.Element('rect', x=str(self.x), y=str(self.y), width=str(self.width), height=str(self.height))
        rect.set('fill', ctx.fill_color)
        rect.set('stroke', ctx.stroke_color)
        rect.set('stroke-width', str(ctx.stroke_width))
        return rect
    
layer_classes = {c.__name__: c for c in [Canvas, Fill, Stroke, Translate, Rectangle]}

def get_layer_params(node):
    parameters_node = None
    for child in node.children:
        if child.name == 'parameters':
            parameters_node = child
            break
        
    if parameters_node is None:
        return {}
    
    named_parameters = {}
    anonymous_parameters = []
    for param_node in parameters_node.children:
        param_type = param_node.name
        if param_type == 'NamedParameter':
            param_name = param_node.children[0].name
            param_value = literal_eval(param_node.children[1].name)
            named_parameters[param_name] = param_value
        else:
            param_val_node = param_node.children[0]
            anonymous_parameters.append(literal_eval(param_val_node.name) if len(param_val_node.children) == 0 else param_val_node)
            
    return named_parameters, anonymous_parameters
        
def get_layer_children(node):
    children_node = None
    for child in node.children:
        if child.name == 'children':
            children_node = child
            break
        
    if children_node is None:
        return []
    
    return children_node.children
    

def parse_ast(root: Node) -> Layer:        
    semanticAssert(root.name in layer_classes, f'Unknown layer type: {root.name}')
    layer_class = layer_classes[root.name]
    
    named_parameters, anonymous_parameters = get_layer_params(root)
    children = get_layer_children(root)
    
    layer = layer_class(*anonymous_parameters, **named_parameters)
    for child in children:
        layer.children.append(parse_ast(child))
        
    return layer