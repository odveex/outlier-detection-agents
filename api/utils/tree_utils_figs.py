class TreeNode:
    """
    Represents a node in a binary decision tree.

    Attributes:
        value (str): The data or condition stored in the node.
        left (TreeNode): Left child node.
        right (TreeNode): Right child node.
        root (bool): Flag indicating if this node is the tree's root.
    """
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.root = False

def trunc_output(input_str):
    """
    Truncate the first five lines from the input string, typically used to remove model headers.

    Args:
        input_str (str): The output string from a model.

    Returns:
        str: The truncated string.
    """
    lines = input_str.splitlines()
    return "\n".join(lines[5:])

def create_tree(lines, parent=None):
    """
    Recursively construct a binary tree from a list of lines describing nodes and their structure.

    The root node is identified by "(Tree #0 root)", and split nodes by "(split)".
    Lines are indented with '\t' to indicate tree depth.

    Args:
        lines (list of str): Lines representing nodes in a decision tree.
        parent (TreeNode, optional): The parent node for the current node; defaults to None.

    Returns:
        TreeNode: The root node of the constructed binary tree.
    """
    first_line = lines[0].strip()
    if first_line.endswith("(Tree #0 root)") or first_line.endswith("(split)"):
        node_value = lines[0].replace('(Tree #0 root)', '').replace('(split)', '').rstrip()
        current_node = TreeNode(node_value)

        # Mark node as root if applicable
        if first_line.endswith("(Tree #0 root)"):
            current_node.root = True

        # Move to subsequent lines
        lines = lines[1:]
        # Remove one level of indentation
        lines = [line[1:] for line in lines]

        # Identify child positions (lines without a leading '\t')
        child_indices = [i for i, line in enumerate(lines) if not line.startswith('\t')]
        if len(child_indices) > 1:
            right_index = child_indices[1]
            current_node.left = create_tree(lines[:right_index], current_node)
            current_node.right = create_tree(lines[right_index:], current_node)
        else:
            # Handle case with only one child
            current_node.left = create_tree(lines, current_node)
    else:
        # Leaf node or simple node
        current_node = TreeNode(lines[0])
        current_node.left = None
        current_node.right = None

    return current_node

def invert_comparison_operators(input_str):
    """
    Invert comparison operators in a given string.

    Rules:
        >= becomes <
        <= becomes >
        > becomes <=
        < becomes >=

    Args:
        input_str (str): Input string containing a comparison operator.

    Returns:
        str: String with the inverted comparison operator.
    """
    if ' >= ' in input_str:
        return input_str.replace(' >= ', ' < ')
    elif ' <= ' in input_str:
        return input_str.replace(' <= ', ' > ')
    elif ' > ' in input_str:
        return input_str.replace(' > ', ' <= ')
    elif ' < ' in input_str:
        return input_str.replace(' < ', ' >= ')
    return input_str

def extract_rules(node, rules, rule):
    """
    Recursively traverse a binary decision tree and build human-readable decision rules.

    Args:
        node (TreeNode): The current tree node.
        rules (list of str): Accumulator for storing generated rules.
        rule (str): Current rule string being built.

    Returns:
        None: Appends generated rules directly to the 'rules' list.
    """
    if node.root is True:
        # Start rule building from the root, generating branches
        extract_rules(node.left, rules, f"IF {invert_comparison_operators(node.value)}")
        extract_rules(node.right, rules, f"IF {node.value}")
    elif not node.root and node.left is not None:
        # Internal node with conditions
        extract_rules(node.left, rules, f"{rule} AND {invert_comparison_operators(node.value)}")
        extract_rules(node.right, rules, f"{rule} AND {node.value}")
    elif node.left is None and node.value == 'Val: 1.000 (leaf)':
        rules.append(f"{rule} THEN OUTLIER")
    elif node.left is None and node.value == 'Val: 0.000 (leaf)':
        rules.append(f"{rule} THEN INLIER")