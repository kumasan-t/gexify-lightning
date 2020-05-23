import networkx as nx
import argparse
import os
import json


def clean_isolated_nodes(graph):
    """
    Removes nodes without edges from the graph
    :param graph: a networkx graph
    :return:
    """
    graph.remove_nodes_from(list(nx.isolates(graph)))


def fix_connectivity(graph):
    """
    Select the largest connected subgraph among the set of connected subgraph.
    :param graph: a networkx graph
    :return: the largest subgraph
    """
    connected = nx.is_connected(graph)
    if not connected:
        # Cut out the largest set of connected components and return it as a subgraph
        return max(nx.connected_component_subgraphs(graph), key=len)


def parse_graph_from_json(json_graph):
    """
    Converts the Lightning Network JSON representation to a networkx representation.
    :param json_graph: a JSON file
    :return: a networkx undirected graph
    """
    graph = nx.Graph()

    # Add each node in the graph
    for node in json_graph['nodes']:
        graph.add_node(node['pub_key'], last_update=node['last_update'])

    # Add each edge in the graph
    # Some edges are missing the node1 and node2 policy fields,
    # so a check is needed before processing it
    for edge in json_graph['edges']:
        if edge['node1_policy'] is not None and \
                edge['node2_policy'] is not None:
            graph.add_edge(edge['node1_pub'],
                           edge['node2_pub'],
                           capacity=int(edge['capacity']),
                           #weight=10000.0/float(edge['capacity']),
                           last_update=int(edge['last_update']),
                           channel_id=edge['channel_id'],
                           chan_point=edge['chan_point'],
                           node1_timelock_delta=int(edge['node1_policy']['time_lock_delta']),
                           node1_min_htlc=int(edge['node1_policy']['min_htlc']),
                           node1_fee_base_msat=int(edge['node1_policy']['fee_base_msat']),
                           node1_fee_rate_milli_msat=int(edge['node1_policy']['fee_rate_milli_msat']),
                           node2_timelock_delta=int(edge['node2_policy']['time_lock_delta']),
                           node2_min_htlc=int(edge['node2_policy']['min_htlc']),
                           node2_fee_base_msat=int(edge['node2_policy']['fee_base_msat']),
                           node2_fee_rate_milli_msat=int(edge['node2_policy']['fee_rate_milli_msat'])
                           )
    return graph


def is_valid_file_path(parser, fp):
    """
    Check if the filepath provided from command line is valid. If not prints
    an error, if True returns an handle to an opened file.
    :param parser: parser object for error handling
    :param fp: filepath to check validity
    :return: a handler to the file
    """
    if not os.path.isfile(fp):
        parser.error('The file %s does not exist!' % fp)
    else:
        return open(fp, 'r', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(prog='Gexify',
                                     description='Convert a LND .json file to a .gexf file  for Gephi visualization')
    parser.add_argument('-i', '--isolated', action='store_true',
                        default=False, help='Removes nodes without edges')
    parser.add_argument('-C', '--connected', action='store_true',
                        default=False, help='Returns the largest component set')
    parser.add_argument('filepath', metavar='PATH',
                        type=lambda x: is_valid_file_path(parser, x), help='Filepath to JSON file')
    parser.add_argument('-o', '--output', required=False, type=str, default='full_graph.gexf',
                        nargs='?', help='Output file location')

    args = parser.parse_args()
    print(args)
    json_graph = json.load(args.filepath)
    graph = parse_graph_from_json(json_graph)
    if args.isolated is True:
        clean_isolated_nodes(graph)
    if args.connected is True:
        graph = fix_connectivity(graph)

    nx.write_gexf(graph, args.output)


if __name__ == '__main__':
    main()
