# -*- coding: utf-8 -*-
# Copyright (c) 2015 – Thomson Licensing, SAS                                                   
#                                                                                               
# Redistribution and use in source and binary forms, with or without modification,              
# are permitted (subject to the limitations in the disclaimer below) provided that              
# the following conditions are met:                                                             
#                                                                                               
# * Redistributions of source code must retain the above copyright notice, this                 
# list of conditions and the following disclaimer.                                              
#                                                                                               
# * Redistributions in binary form must reproduce the above copyright notice,                   
# this list of conditions and the following disclaimer in the documentation                     
# and/or other materials provided with the distribution.                                        
#                                                                                               
# * Neither the name of Thomson Licensing, or Technicolor, nor the names of its                 
# contributors may be used to endorse or promote products derived from this                     
# software without specific prior written permission.                                           
#                                                                                               
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS               
# LICENSE.  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS                 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,                 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE                
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE               
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL                    
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR                    
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER                    
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR              
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF                 
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  
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
