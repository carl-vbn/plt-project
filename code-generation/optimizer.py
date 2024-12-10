import xml.etree.ElementTree as ET

# Remove groups that don't have any attributes
# Move their children to the parent group
def remove_redundant_groups(root: ET) -> ET:
    for group in root.findall('.//g'):
        if not group.attrib:  # Check if the group has no attributes
            for child in list(group):
                root.append(child)
            
            if group in root:
                root.remove(group)

    return root

# If a group only has one child, remove the group and move the child to the parent group
# Apply the group's attributes to the child
def remove_single_child_groups(root: ET) -> ET:
    for group in root.findall('.//g'):
        if len(group) == 1:
            child = group[0]
            for key, value in group.attrib.items():
                child.set(key, value)
            
            root.append(child)
            root.remove(group)
    
    return root

def optimize_svg(svg_tree: ET) -> ET:
    original_svg_str = ET.tostring(svg_tree).decode('utf-8')
    
    svg_tree = remove_redundant_groups(svg_tree)    
    svg_tree = remove_single_child_groups(svg_tree)
    
    new_svg_str = ET.tostring(svg_tree).decode('utf-8')
    
    # If the SVG tree has changed, re-run the optimizer
    if original_svg_str != new_svg_str:
        return optimize_svg(svg_tree)
    
    return svg_tree
    