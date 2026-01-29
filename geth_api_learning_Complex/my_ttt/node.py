# my_ttt/node.py

class DTNode:
    """
    Discrimination Tree Node.

    - Leaf node:
        is_leaf=True
        rep: list (representative access string)
        children: empty

    - Internal node:
        is_leaf=False
        discriminator: list (suffix used to distinguish)
        children: dict {True: DTNode, False: DTNode}
    """

    def __init__(self, value=None, is_leaf=False):
        self._is_leaf = is_leaf

        # for leaf
        self.rep = None

        # for internal
        self.discriminator = None

        self.children = {}

        if is_leaf:
            # value is representative
            self.rep = value if value is not None else []
        else:
            # value is discriminator
            self.discriminator = value if value is not None else []

    def is_leaf(self):
        return self._is_leaf

    def become(self, other_node):
        """
        Replace this node in-place with other_node's content.
        This is what learner expects: leaf.become(new_internal_node).
        """
        self._is_leaf = other_node._is_leaf
        self.rep = other_node.rep
        self.discriminator = other_node.discriminator
        self.children = other_node.children

    def __repr__(self):
        if self._is_leaf:
            return f"DTLeaf(rep={self.rep})"
        return f"DTNode(disc={self.discriminator}, children={list(self.children.keys())})"
