#!/usr/bin/env python3

"""
    Cable optimizer.

    Reduces the complexity of network of cables to minimum possible by
    replacing a set of cables in series or parallel with a single cable
    with equivalent delay.

    Correctness of input data assumption:
    1. Graph is connected (связный), any vertex is adjacent to any other
    2. There are no self-connected (замкнутых) edges. e.g. there is no "a a 1"
    3. All weights of edges are positive
"""

###############################################################################
    # Problem:

    # Consider a datacenter that is filled with cables connecting data points.
    # There could be multiple direct cables between any 2 data points.

    # This network of cables could be represented in the form of a graph.
    # Cables may be connected in series or in parallel.

    # Cables connected one after the other through a set of data points without
    # any intervening cables are said to be connected in “series”.
    # In graph terminology, along the “path” of cables,
    # each vertex has “degree” 2.
    # The total delay experienced in cables connected in series is given as:
    #     D = D1 + D2 + D3 + … + Dn

    # Multiple cables between a pair of data points are said to be
    # connected in “parallel”.
    # In graph terminology, there are multiple “edges” between a pair of nodes
    # The total delay experienced in cables connected in parallel is given as:
    #     1/D = 1/D1 + 1/D2 + 1/D3 + … + 1/Dn

    # Objective: Reduce the complexity of network of cables to minimum possible
    # by replacing a set of cables in series or parallel with a single cable
    # with equivalent delay.

    # The network is assumed to have a starting point and an ending point
    # between which these replacements have to be performed.
    # Also, certain cables are super-hyper-conducting cables with 0 delay.

    # Input: First line will specify number of edges to follow as well as the
    # starting point and ending point between which reductions have to be
    # performed.
    # Subsequent lines will be edges in the form <node1> <node2> <delay>
    # Nodes will be represented as single letters, for e.g. ‘a’, ‘z’, etc.

    # Output: The reduced graph as a series of edges one on each line.

    # Example:
    # Input:
    # 6 a b
    # a e 2
    # e b 2
    # a c 0
    # c d 8
    # c d 8
    # d b 0

    # Output:
    # a b 2


    # Detailed Explanation of the example
    # -------------------------------------------------

    # If you draw the graph given in the example, you will see that there is an
    # edge from a to e and an edge from e to b. So edge weight from a to e = 2
    # and edge weight from e to b = 2. These 2 edges are in series. They can be
    # replaced by a single edge from a to b with edge weight = 2 + 2 = 4.

    # Similarly, apply reductions for portion involving c and d of the graph
    # There they are in parallel. So, 1/D = 1/8 + 1/8 = 1/4 and
    # therefore delay = 4

    # Now a->c = 0, c->d = 4 and d->b = 0. Replace there 3 edges by a single
    # edge with weight = 0 + 4 + 0 = 4. Now 2 edges between a and b each
    # with weight 4 and these edges are in parallel. Reduce further to get
    # a single edge with output 2.
###############################################################################


import os
import sys
import unittest
import logging
import logging.config


logging.config.dictConfig({'version': 1,
                           'formatters': {
                               'default': {
                                   'format': '%(message)s'}},
                           'handlers': {
                               'console': {
                                   'class': 'logging.StreamHandler',
                                   'formatter': 'default',
                                   # Set this to DEBUG to see debug messages
                                   # Set level to INFO to work silently
                                   'level': 'INFO',
                                   'stream': 'ext://sys.stdout'}},
                           'root': {
                               'level': 'DEBUG',
                               'handlers': ['console']}
                           })
logger = logging.getLogger(__name__)


def qsort(list):
    """
    Quick sort using list comprehensions
    average complexity: O(n*logn)
    """
    if list == []:
        return []
    else:
        pivot = list[0]
        lesser = qsort([x for x in list[1:] if x < pivot])
        greater = qsort([x for x in list[1:] if x >= pivot])
        return lesser + [pivot] + greater


def redirect_edge_alpabetically(edge):
    """
    Redirect edge to point from first vertex to last according to alphabet
    e.g. "b a 3" will become "a b 3"

    Arguments:
        - edge: list, could be changed
    """
    if edge[0].lower() > edge[1].lower():
        msg = "{} ".format(edge)
        work = edge[0]
        edge[0] = edge[1]
        edge[1] = work
        msg += "-> {}".format(edge)
        logger.debug(msg)


def get_transition_vertexes(dd, start, end):
    """
    Get transition vertexes with edges indexes from degrees dictionary

    Arguments:
        - dd: degrees dictionary
        - start: starting vertex (is not transitional)
        - end: ending vertex (not transitional)

    Returns:
        - list of lists of transition vertexes with indexes of edges,
            e.g.  { 'e':[0, 1], 'd': [3, 4]},
                where 0,1,3,4 - indexes of edges
                not tuples because they are going to updated
    """
    # from degrees dictionary choose vertexes with degree == 2
    # except for start and end vertex, combine a list of
    # such vertexes with indexes of their edges in edges list

    v_indexes = {}
    for v in dd:
        if dd[v][0] == 2 and v != start and v != end:
            v_indexes[v] = [dd[v][1], dd[v][2]]

    return v_indexes


def arrange_merge_pair(dd, c, start, end):
    """
    Choose best vertex between two to be eliminated

    Criteria:
        1. not @start or @end
        2. has less edges than competitor

    Arguments:
        - list of 2 nodes where 1 should be merged with another

    Returns:
        - list of 2 nodes, where 1st will be kept, 2nd - merged
    """
    logger.debug("arrange merge pair: {}".format(c))
    if c[0] == start or c[0] == end:
        if c[1] == start or c[1] == end:
            return None  # this is start-end edge, shouldn't be merged
        else:
            # c[0] is critical, c[1] - not, eliminate c1
            return c[0], c[1]
    elif c[1] == start or c[1] == end:
            # c[1] is critical, c[0] - not, eliminate c0
            return c[1], c[0]
    else:
        # none of them are critical,
        # choose one that has smaller weight
        # to reduce amount of edges affected
        if dd[c[0]][0] > dd[c[1]][0]:
            return c[0], c[1]
        else:
            return c[1], c[0]  # it is ok if their weights are equal


def merge(to, _from, dd, edges):
    """
    Merge all connections from @from vertex to @to vertex
    Will keep empty (cycled) edge in edges left after reconnection.
    E.g. k-m edge with zero delay after substitution will become m-m edge.
    It should be removed later

    Arguments:
        - to: vertex name to be kept
        - from: vertex name whose connection are going to be
            merged with "to"
    """
    # find all edges with @from in it.
    for i in dd[_from][1:]:
        # for each edge substitute vertex with @to
        e = edges[i]
        e[e.index(_from)] = to

    # at this point one closed edge is going to appear


def reduce_parallel(edges):
    """ Find and reduces parallel edges in the list

    Sorts list.

    Arguments:
        - edges: list of edges, e.g. [['a', 'b', 5], ['a', 'c', 5], ... ]
    """
    edges[:] = qsort(edges)
    logger.debug("Performing parallel optimization\n")
    e = edges  # use shorter name for edges

    l = 0  # l stands for left and points to left side of comparison
    # r stands for right and points to the right side of comparison
    # items are sorted in the list, so parallel
    # edges are going to be next to each other
    for r in range(1, len(e)):
        logger.debug("CMP e[{}]:{} to e[{}]:{}".format(l, e[l], r, e[r]))
        if (e[l][0] == e[r][0] and e[l][1] == e[r][1]):
            # for parallel edges - overwrite left delay with balanced delay
            # except if one of the edges is zero = set zero
            if(e[r][2] == 0):
                e[l][2] = 0
            else:
                e[l][2] = (e[l][2] * e[r][2]) / (e[l][2] + e[r][2])

            # keep right edge value unchanged as
            # it is going to be overwritten later,
            # when not parallel edges is going to be found
            logger.debug(" Parallel: new value e[{}]:{}".format(l, e[l]))
        else:
            # for not equal edges
            # copy right component to the place right after left.
            # e.g.: with l=0, r=1 this is going to be self assignment,
            # with l=3, r=5 this is going to overwrite one of old parallels
            # that were merged with their lefts
            l += 1
            e[l] = e[r]
            logger.debug("     NOT Parallel: e[{}]:{} <= e[{}]:{}".format(
                l, e[l], r, e[r]))

    # by the time this loop is ended l is going to point
    # to last meaningful edge in the list
    kept = l + 1
    removed = len(e) - kept
    logger.debug("\n{} parallels removed\n".format(removed))

    e[:] = e[:kept]
    logger.debug("Parallel reduce result edges: {}\n".format(e))

    return removed


def eliminate_zero_edges(edges, start, end):
    """
    Merge vertexes connected by zero delay edge.
    do not merge start with end
    Assumed that parallels are already removed

    Arguments:
        - edges: list of edges, e.g. [['a', 'b', 5], ['a', 'c', 5], ... ]
        - start: start vertex, e.g. 'a'
        - end: end vertex, e.g. 'b'

    """
    # Gathers indexes of zeroed edges and merges vertexes connected by edges
    # with 0 delay
    # During connection edges with 0 delay become cycled,
    # they are removed later

    dd = get_degrees_dictionary(edges)

    # get zeroed edges with indexes
    zero_edges_indices = []
    for i in range(len(edges)):
        if edges[i][2] == 0:  # if delay is zero
            zero_edges_indices.append(i)

    for i in zero_edges_indices:

        # eliminate vertex with smaller weight
        candidates = edges[i][0:2]

        if candidates[0] == candidates[1]:
            #edge was processed already
            continue

        keep, eliminate = arrange_merge_pair(dd, candidates, start, end)
        if eliminate is None:
            continue  # this is start-end edge, keep it
        merge(keep, eliminate, dd, edges)

        # at this point one closed edge is going to appear
        # k-m edge with zero delay after substitution will become m-m edge.
        # we will remove it later

    for i in reversed(sorted(zero_edges_indices)):
        logger.debug("removing zero edge: {}: {}".format(i, edges[i]))
        edges.pop(i)

    logger.debug("\neliminate zero result edges:  {}\n".format(edges))


def reduce_sequential(edges, start, end):
    """
    Reduces transitional vertexes in graph described in edges

    Arguments:
       - edges: list of edges, e.g. [['e', 'd', d], ...]
       - start: start edge, e.g. 'a'
       - end: end edge, e.g. 'b'

    Returns:
        - amount of edges reduces

     Reduce each vertex v with 2 edges [ei1, ei2]
     e.g. for vertex 'v' there are
     - edge to source 'v1' vertex: edges[ei1], e.g. ['v1', 'v', 3]
     - edge to destination vertex 'v2': edges[ei2] == e.g. ['v2', 'v', 5]

     - replace source edge ei1 vertex 'v' with destination edge ei2 'v2'
      (arrange them if needed)
     - update the source edge delay as sum of delays
     - cycle destination edge to itself
     - remove cycled edges

     edges[ei1] == ['v1', 'v2', 8] #
     edges[ei2] == ['v', 'v', 5] #  delay not changed
    """
    dd = get_degrees_dictionary(edges)  # O(len(edges))
    tvs = get_transition_vertexes(dd, start, end)  # O(len(dd))
    logger.debug("dd: {}".format(dd))
    logger.debug("tvs: {}".format(tvs))

    for v in tvs:  # for each vertex in transitional vertexes
        # edges
        ei1 = tvs[v][0]
        ei2 = tvs[v][1]

        e1 = edges[ei1]  # e1 is going to save resulted edge
        e2 = edges[ei2]  # e2 is going to become cycled and then removed

        # vertexes
        # v - vertex to be removed
        # v1 - vertex, connected to v by e1 edge (unchanged)
        # v2 - vertex, connected to v by e2 edge
        #      will be moved to e1 substituting v there
        #      edges list in transitional vertex dictionary will be updated

        logger.debug("Substituted {}: {}:{}, {}:{} -> ".format(
            v, ei1, e1, ei2, e2))

        # v is going to be substituted in e1 by value of "not v" vertex in e2
        substitute_index_in_ei2 = 1 - e2.index(v)  # if vi=0 s=1; v=1 s=0

        # replace v in ei1 by substitute from ei2
        v2 = e2[substitute_index_in_ei2]

        e1[e1.index(v)] = v2
        e2[substitute_index_in_ei2] = v

        # here we will have 2 edges
        # edges[ei1] -> ['v1', 'v2', ?] #
        # edges[ei2] -> ['v', 'v', 5] #  delay not changed

        # updated edges for substituted vertex in tvs dict to point to
        # ei1 edge instead of ei2
        # e.g. 'v2' was connected by ei2, now is connected by ei1

        if v2 != start and v2 != end:
            # v2 is not present in tvi and shouldn't be updated
            v2ei = tvs[v2]  # list of edges indexes for v2
            vei = tvs[v]    # list of edges indexes for v
            v2ei[v2ei.index(ei2)] = ei1

            logger.debug("tvs[{}][2] = t[1] : {} = {}".format(
                v2,
                tvs[v2][2],
                t[1]))

        # update weight
        new_weight = e1[2] + e2[2]
        e1[2] = new_weight

        # normalize result edge
        redirect_edge_alpabetically(e1)

        # here we will have 2 edges
        # edges[ei1] -> ['v1', 'v2', 8] #
        # edges[ei2] -> ['v', 'v', 5] #  delay not changed

        # only thing left is to remove the ei2 edge, this will be done later
        # not to break iteration over edges

        logger.debug("{}:{}, {}:{}".format(ei1, e1, ei2, e2))

    # get indexes of edges to be removed
    indexes = [i for i in reversed(sorted([tvs[v][1] for v in tvs]))]
    logger.debug("Edges index removed after sequential update: {}".format(
        indexes))

    for i in indexes:
        edges.pop(i)

    return len(tvs)  # amount of edges removed


def get_degrees_dictionary(edges):
    """
    Scans edges list and calculates degree for each vertex,
    also saving indexes of related edges for each vertex

    Arguments:
        - List of edges

    Returns:
        - Degrees Dictionary, e.g.
        {'x': [2, 3, 9], 'y': [5, 1, 2, 3, 4, 5], *... ]
        where for x 2 - amount of edges,
                    3 and 9 - indexes of edges in edge list
    """
    dd = {}  # degrees dictionary for vertexes

    def append_vertex(vertex, edge_index):
        if vertex not in dd.keys():
            dd[vertex] = [1, edge_index]
        else:
            dd[vertex][0] += 1
            dd[vertex].append(edge_index)

    e = edges
    for i in range(len(e)):
        append_vertex(e[i][0], i)
        append_vertex(e[i][1], i)

    return dd


def optimize(edges, start, end):
    """
    Optimize graph

    Arguments:
        - edges: list of edges
        - start: starting edges
        - end: ending edge
    """
    for edge in edges:
        redirect_edge_alpabetically(edge)

    reduce_parallel(edges)
    eliminate_zero_edges(edges, start, end)
    reduce_sequential(edges, start, end)

    while True:
        if reduce_parallel(edges) == 0:
            break

        if reduce_sequential(edges, start, end) == 0:
            break

    logger.debug("Optimization finished.")


def scan_edges(edges_count):
    """ scans edges data from user input

    Arguments:
        - edges amount to scan

    Returns:
        - list of edges, example: [["a", "e", 2], ["e", "b", 2], ...]
    """

    edges = []
    for _ in range(edges_count):
        edge = input("Enter edge:").split(" ")

        try:
            edge[2] = int(edge[2])
        except ValueError:
            raise ValueError("Input data parsing error, "
                             "the format should be like \"s s 3\"")

        edges.append(edge)

    return edges


def print_output(edges):
    """ prints output in format of edge input """
    for edge in edges:
        print("{} {} {}".format(edge[0], edge[1], int(edge[2])))


def run(version=1):
    """ Main method ask for user input, perform task, print output """

    # scan header to define our graph parameters
    try:
        header = input("Enter graph header:")
        edges_count, start_edge, finish_edge = header.split(" ")
        edges_count = int(edges_count)
        logger.debug("Scanned edges count: {}; Start:{}, End:{}".format(
            edges_count, start_edge, finish_edge))
    except ValueError:
        raise ValueError("Input data parsing error, "
                         "the format should be like \"3 a b\"")

    # scan edges
    edges = scan_edges(edges_count)
    logger.debug("Scanned edges: {}".format(edges))

    optimize(edges, start_edge, finish_edge)

    print_output(edges)


if __name__ == "__main__":
    run()
