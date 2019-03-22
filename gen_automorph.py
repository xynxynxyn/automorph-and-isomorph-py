from graph import *
from fast_col_ref import color_refinement
from enum import Enum
from collections import Counter
from permv2 import *


def is_unbalanced(A, B):
    a = Counter([v.color for v in A.vertices])
    b = Counter([v.color for v in B.vertices])
    return not a == b


def is_bijective(A, B):
    a = Counter([v.color for v in A.vertices])
    b = Counter([v.color for v in B.vertices])
    return a == b and len(a) == len(A.vertices) and len(b) == len(B.vertices)


class Case(Enum):
    UNBALANCED = 1
    IN_AUT = 2
    NOT_IN_AUT = 3


# X keeps track of the non trivial mappings performed
# G is the Generating set for Aut(G)
# is_trivial shows whether the current step is trivial
def gen_rec(A: "Graph",
            B: "Graph",
            X: "List" = [],
            is_trivial=False,
            G: "permutation" = permutation()):
    # Do coloring
    U = A + B
    color_refinement(U, reset_colors=False)
    A, B = U.split_disjoint()

    if is_unbalanced(A, B):
        return Case.UNBALANCED
    if is_bijective(A, B):
        # Check whether the current mapping is already in the powerset
        if len(X) == 0:
            # Mapping is completely trivial
            return Case.IN_AUT
        # TODO check if X is already a member of the generating set
        elif is_member_of(X, G):
            # Is already member
            return Case.IN_AUT
        else:
            # If not in the generating set add it
            # TODO add the new mapping X to the generating set
            return Case.NOT_IN_AUT

    c_classes = [
        c for c, n in Counter([v.color for v in A.vertices]).items() if n >= 2
    ]

    c_class = max(c_classes)

    v = [v for v in A.vertices if v.color == c_class][0]

    v.color = A.max_color + 1
    v.colornum = v.color

    for u in [k for k in B.vertices if k.color == ref_c]:
        old_u_col = u.color
        u.color = v.color
        u.colornum = v.colornum

        resp = None
        old_x = X
        if u.label == v.label:
            resp = gen_rec(A, B, X=X, is_trivial=True, G=G)
        else:
            X.append((v.label, u.label))
            resp = gen_rec(A, B, X=X, is_trivial=False, G=G)

        if resp == Case.IN_AUT:
            # Just return
            # After resetting all the values
            X = old_x
            u.color = old_u_col
            u.colornum = old_u_col
            return Case.IN_AUT
        elif resp == Case.NOT_IN_AUT:
            # Return to the latest trivial
            if not is_trivial:
                # If the current node is not trivial go higher up the tree
                return Case.NOT_IN_AUT
            # Else just continue with the other vertices

        X = old_x
        u.color = old_u_col
        u.colornum = old_u_col

    # If no automorphisms are found or all of them are already in the power set
    # Return UNBALANCED
    return Case.UNBALANCED


# Generate a permutation powerset for the automorphism
# of graph G
def gen_auto_set(G: "Graph"):
    # Do initial coloring by degree to speed up initial step
    for v in G.vertices:
        v.color = v.degree

    X = list()
    gen_rec(G, G, X)
    return X
