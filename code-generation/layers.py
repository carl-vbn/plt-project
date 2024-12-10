import xml
import xml.etree
import xml.etree.ElementTree
from syntax_tree import Node
import re
from math import sin, cos, tan, atan, asin, acos, pi, e
    
class SemanticError(Exception):
    pass

def semanticAssert(condition, message):
    if not condition:
        raise SemanticError(message)
    
class Context:
    def __init__(self):
        self.fill_color = None
        self.stroke_color = None
        self.stroke_width = 1
        self.frame = 0
        self.globals = {'sin': sin, 'cos': cos, 'tan': tan, 'atan': atan, 'asin': asin, 'acos': acos, 'pi': pi, 'e': e}
        
    def copy(self):
        copy = Context()
        copy.fill_color = self.fill_color
        copy.stroke_color = self.stroke_color
        copy.stroke_width = self.stroke_width
        copy.frame = self.frame
        copy.globals = self.globals.copy()
        return copy
    

class Layer:
    def to_svg(self) -> xml.etree.ElementTree:
        raise NotImplementedError()
    
class Canvas(Layer):
    def __init__(self, width, height, length=1):
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
    if type(node) is str:
        return node

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

            if start is None:
                start = 0

            if start is not None and end is not None:
                semanticAssert(length is None, 'Cannot specify both start/end and length')
                self.start = start
                self.length = end - start + 1
                
            elif start is not None and length is not None:
                self.start = start
                self.length = length
                
            elif end is not None and length is not None:
                self.length = length
                self.start = end - length + 1
                
            else:
                raise SemanticError('Missing temporal parameters')
            
            if length <= 1:
                raise SemanticError('Length must be over 1')
        
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        if self.animated:
            t = max(0, min(1, (ctx.frame - self.start) / (self.length - 1)))
            x = self.x * t
            y = self.y * t
            g = xml.etree.ElementTree.Element('g', transform=f'translate({x}, {y})')
        else:
            g = xml.etree.ElementTree.Element('g', transform=f'translate({self.x}, {self.y})')
            
        for child in self.children:
            g.append(child.to_svg(ctx))
            
        return g
    
class Rotate(Layer):
    def __init__(self, center, angle, start=None, end=None, length=None):
        self.center = center
        self.angle = angle
        self.children = []
        
        if start is None and end is None and length is None:
            self.start = None
            self.length = None
            self.animated = False
        else:
            self.animated = True

            if start is None:
                start = 0

            if start is not None and end is not None:
                semanticAssert(length is None, 'Cannot specify both start/end and length')
                self.start = start
                self.length = end - start + 1
                
            elif start is not None and length is not None:
                self.start = start
                self.length = length
                
            elif end is not None and length is not None:
                self.length = length
                self.start = end - length + 1
                
            else:
                raise SemanticError('Missing temporal parameters')
        
            if length <= 1:
                raise SemanticError('Length must be over 1')
            
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        if self.animated:
            t = max(0, min(1, (ctx.frame - self.start) / (self.length - 1)))
            angle = self.angle * t
            g = xml.etree.ElementTree.Element('g', transform=f'rotate({angle}, {self.center[0]}, {self.center[1]})')
        else:
            g = xml.etree.ElementTree.Element('g', transform=f'rotate({self.angle}, {self.center[0]}, {self.center[1]})')
            
        for child in self.children:
            g.append(child.to_svg(ctx))
            
        return g
    
class CircularPath(Layer):
    def __init__(self, center, r, start_angle=0, end_angle=360, start=0, end=None, length=None, _exports=None):
        self.center = center
        self.r = r
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.children = []
        self.exports = _exports or []
        
        if start is not None and end is not None:
            semanticAssert(length is None, 'Cannot specify both start/end and length')
            self.start = start
            self.length = end - start + 1
            
        elif start is not None and length is not None:
            self.start = start
            self.length = length
            
        elif end is not None and length is not None:
            self.length = length
            self.start = end - length + 1
            
        else:
            raise SemanticError('Missing temporal parameters')
    
        if length <= 1:
            raise SemanticError('Length must be over 1')
        
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        t = max(0, min(1, (ctx.frame - self.start) / (self.length - 1)))
        angle = self.start_angle + (self.end_angle - self.start_angle) * t
        x = self.center[0] + self.r * cos(angle * pi / 180)
        y = self.center[1] + self.r * sin(angle * pi / 180)

        ctx_copy = ctx.copy()
        available_exports = (x, y, t, angle)

        if self.exports is not None:
            for i, export in enumerate(self.exports):
                ctx_copy.globals[export] = available_exports[i]
        
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
        
        if ctx.fill_color is not None:
            rect.set('fill', ctx.fill_color)
        
        if ctx.stroke_color is not None:
            rect.set('stroke', ctx.stroke_color)
            rect.set('stroke-width', str(ctx.stroke_width))
        return rect
    
class Circle(Layer):
    def __init__(self, x, y, r):
        super().__init__()
        self.x = x
        self.y = y
        self.r = r
        
    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        circle = xml.etree.ElementTree.Element('circle', cx=str(self.x), cy=str(self.y), r=str(self.r))
        
        if ctx.fill_color is not None:
            circle.set('fill', ctx.fill_color)
        
        if ctx.stroke_color is not None:
            circle.set('stroke', ctx.stroke_color)
            circle.set('stroke-width', str(ctx.stroke_width))
        return circle
    
class Arrow(Layer):
    def __init__(self, origin, vector):
        self.origin = origin
        self.vector = vector

    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        line = xml.etree.ElementTree.Element('line', x1=str(self.origin[0]), y1=str(self.origin[1]), x2=str(self.origin[0] + self.vector[0]), y2=str(self.origin[1] + self.vector[1]))
        
        if ctx.stroke_color is not None:
            line.set('stroke', ctx.stroke_color)
            line.set('stroke-width', str(ctx.stroke_width))
        
        return line

class Latex(Layer):
    def __init__(self, code, x, y, size=4):
        self.code = code
        self.x = x
        self.y = y
        self.size = size

    def to_svg(self, ctx: Context) -> xml.etree.ElementTree:
        # Very primitive latex parsing while waiting for a better solution
        # Replace \textrm{A} and \textbf{A} with A
        processed_code = re.sub(r'\\textrm\{(.+?)\}', r'\1', self.code)
        processed_code = re.sub(r'\\textbf\{(.+?)\}', r'\1', processed_code)

        # Replace \frac{A}{B} and \dfrac{A}{B} with A/B
        processed_code = re.sub(r'\\frac\{(.+?)\}\{(.+?)\}', r'\1/\2', processed_code)
        processed_code = re.sub(r'\\dfrac\{(.+?)\}\{(.+?)\}', r'\1/\2', processed_code)

        # Replace \eval{A} with the evaluation
        processed_code = re.sub(r'\\eval\{(.+?)\}', lambda m: str(eval(m.group(1), ctx.globals)), processed_code)

        if type(self.x) == str:
            x = eval(self.x, ctx.globals)
        else:
            x = self.x

        if type(self.y) == str:
            y = eval(self.y, ctx.globals)
        else:
            y = self.y
                    

        text = xml.etree.ElementTree.Element('text', x=str(x), y=str(y))
            
        if ctx.fill_color is not None:
            text.set('fill', ctx.fill_color)
            
        if ctx.stroke_color is not None:
            text.set('stroke', ctx.stroke_color)
            text.set('stroke-width', str(ctx.stroke_width))
    
        text.text = processed_code
        text.set('font-size', str(self.size))
        return text
    
layer_classes = {c.__name__: c for c in [Canvas, Fill, Stroke, Translate, Rotate, CircularPath, Rectangle, Circle, Arrow, Latex]}

def eval_node(node):
    if node.name == 'Tuple':
        return tuple([eval_node(child) for child in node.children])
    
    # Integer
    elif re.match(r'^\d+$', node.name):
        return int(node.name)
    
    # Float
    elif re.match(r'^\d+\.\d+$', node.name):
        return float(node.name)
    
    # Single quote string
    elif re.match(r'^\'[^\']*\'$', node.name):
        return node.name.strip('\'')
    
    # Double quote string
    elif re.match(r'^\"[^\"]*\"$', node.name):
        return node.name.strip('\"')
    
    else:
        return node.name

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
            param_value = eval_node(param_node.children[1])
            named_parameters[param_name] = param_value
        else:
            param_val_node = param_node.children[0]
            anonymous_parameters.append(eval_node(param_val_node) if len(param_val_node.children) == 0 else param_val_node)
            
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

def get_layer_exports(node):
    exports_node = None
    for child in node.children:
        if child.name == 'exports':
            exports_node = child
            break
        
    if exports_node is None:
        return None
    
    return [child.name for child in exports_node.children]
    

def parse_ast(root: Node, subcall=False) -> Layer:        
    semanticAssert(root.name in layer_classes, f'Unknown layer type: {root.name}')
    layer_class = layer_classes[root.name]
    
    if subcall and layer_class == Canvas:
        raise SemanticError('Canvas must be the top-level layer')
    
    named_parameters, anonymous_parameters = get_layer_params(root)
    children = get_layer_children(root)
    exports = get_layer_exports(root)

    if exports is not None:
        named_parameters['_exports'] = exports

    layer = layer_class(*anonymous_parameters, **named_parameters)
    for child in children:
        layer.children.append(parse_ast(child, subcall=True))
        
    return layer