class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
    
def print_tree(root):
    print(root.name)
    
    for i, child in enumerate(root.children):
        print_tree_branch(child, '', i == len(root.children) - 1)
    
def print_tree_branch(node, prefix='', is_tail=True):
    print(prefix + ('└── ' if is_tail else '├── ') + node.name)
    for i, child in enumerate(node.children):
        print_tree_branch(child, prefix + ('    ' if is_tail else '│   '), i == len(node.children) - 1)