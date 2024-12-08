import xml
import xml.etree
import xml.etree.ElementTree
from syntax_tree import Node
    
class SemanticError(Exception):
    pass

def semanticAssert(condition, message):
    if not condition:
        raise SemanticError(message)
    
class Context:
    def __init__(self, fill_color, stroke_color, stroke_width):
        self.fill_color = fill_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        
    def copy(self):
        return Context(self.fill_color, self.stroke_color, self.stroke_width)

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
    
layer_classes = {c.__name__: c for c in [Canvas, Fill, Stroke, Rectangle]}

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
            param_value = param_node.children[1].name
            named_parameters[param_name] = param_value
        else:
            param_val_node = param_node.children[0]
            anonymous_parameters.append(param_val_node.name if len(param_val_node.children) == 0 else param_val_node)
            
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
    # canvasNode = root.children[0]
    # semanticAssert(canvasNode.name == 'Canvas', 'Root node must be a Canvas')
    
    # parameters, _ = get_layer_params(canvasNode)
    # semanticAssert('width' in parameters, 'Canvas must have a width parameter')
    # semanticAssert('height' in parameters, 'Canvas must have a height parameter')
    # semanticAssert('length' in parameters, 'Canvas must have a length parameter')
    
    # width = parameters['width']
    # height = parameters['height']
    # length = parameters['length']
    
    # canvas = Canvas(50, 50)
    # fill = Fill('red')
    # rect = Rectangle(10, 10, 20, 20)
    # fill.children.append(rect)
    # canvas.children.append(fill)
    
    # ctx = Context('black', 'black', 1)
    # svg = canvas.to_svg(ctx)
    # print(xml.etree.ElementTree.tostring(svg).decode())
    
    semanticAssert(root.name in layer_classes, f'Unknown layer type: {root.name}')
    layer_class = layer_classes[root.name]
    
    named_parameters, anonymous_parameters = get_layer_params(root)
    children = get_layer_children(root)
    
    layer = layer_class(*anonymous_parameters, **named_parameters)
    for child in children:
        layer.children.append(parse_ast(child))
        
    return layer