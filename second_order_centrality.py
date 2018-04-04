# -*- coding: utf-8 -*-
# /********** COPYRIGHT AND CONFIDENTIALITY INFORMATION NOTICE *************
# ** Copyright (c) 2017 Thomson Licensing – a Technicolor Group Company  **
# ** All Rights Reserved                                                  **
# ** Technicolor hereby informs you that the following portions of this   **
# ** open source module and/or Work are distributed and not sub-licensed  **
# ** by Technicolor, under the terms of the applicable open source        **
# ** software license terms (available from the Readme files).            **     
# ** This Work may or may not include modifications or additions.         **
# ** Technicolor modifications and/or additions shall in no event be      **
# ** deemed construed or otherwise considered as being a "Contribution"   **
# ** to such third party Apache 2.0 open source software code.            **
# ** Distribution and copying of all such modifications are reserved      **
# ** to Technicolor and/or its affiliates, and are not permitted without  **
# ** express written authorization from Technicolor.                      **
# ** Technicolor is registered trademark and trade name of Technicolor,   **
# ** and shall not be used in any manner without express written          **
# ** authorization from Technicolor                                       **
# **************************************************************************/
#
# Authors: Erwan Le Merrer (erwan.lemerrer@technicolor.com)
''' Second order centrality measure.'''
import networkx as nx
import numpy as np
import copy

__all__ = ['second_order_centrality']

@nx.not_implemented_for('directed')
def second_order_centrality(G):
    """Compute the second order centrality for nodes of G.

    The second order centrality of a given node is the standard deviation of 
    the return times to that node of a perpetual random walk on G:

    Parameters
    ----------
    G : graph
      A NetworkX connected and undirected graph.

    Returns
    -------
    nodes : dictionary
       Dictionary keyed by node with second order centrality as the value.

    Examples
    --------
    >>> G = nx.star_graph(10)
    >>> soc = second_order_centrality(G)
    >>> print(sorted(soc.items(), key=lambda x:x[1])[0][0]) # pick first id
    0  # most central node

    See Also
    --------
    betweenness_centrality

    Notes
    -----
    Lower values of second order centrality indicate higher centrality.
    
    The algorithm is from Kermarrec, Le Merrer, Sericola and Trédan [1]_.
    
    This code implements the analytical version of the algorithm, i.e., 
    there is no simulation of a random walk process involved. The random walk
    is here biased (corresponding to eq(4) of the paper [1]_).
    
    Complexity of this implementation, made to run locally on a single machine, 
    is O(n^3), with n the size of G, which makes it viable only for small 
    graphs.

    References
    ----------
    .. [1] Anne-Marie Kermarrec, Erwan Le Merrer, Bruno Sericola, Gilles Trédan
       "Second order centrality: Distributed assessment of nodes criticity in
       complex networks", Elsevier Computer Communications 34(5):619-628, 2011.
    """
    n = len(G)

    if n == 0:
        raise nx.NetworkXException("Empty graph.")
    if not nx.is_connected(G):
        raise nx.NetworkXException("Non connected graph.")
    
    P = nx.to_numpy_matrix(G)
    P = P / P.sum(axis=1)  # to transition probability matrix
    
    def _Qj(P, j):
        P = copy.deepcopy(P)
        P[:, j] = 0
        return P
    
    M = np.empty([n, n])
    H = np.empty([n, n])
    for i in range(n):
        M[:, i] = np.linalg.solve(np.identity(n) - _Qj(P, i),
                                  np.ones([n, 1])
                                 )[0]# eq(3)
        H[:, i] = np.linalg.solve((np.identity(n) - _Qj(P, i)),
                                 (np.identity(n) + _Qj(P, i)) * 
                                    np.reshape(M[:, i], [n, 1])
                                 )[0]
        
    return {k: v for k, v in enumerate(np.sqrt(H - np.square(M))[0, :])}# eq(4)


if __name__ == '__main__':

    G=nx.star_graph(10)
    soc = second_order_centrality(G)
    print("Most central node id: %d" % sorted(soc.items(), key=lambda x:x[1])[0][0])
