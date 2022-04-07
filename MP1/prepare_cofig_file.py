def main():
    port = 1234
    node_ip_mapping = {"node1": "localhost", "node2": "localhost", "node3": "localhost"}
    node_port_mapping = {"node1": 1221, "node2": 1222, "node3": 1223}
    total_num = len(node_ip_mapping.keys())
    for node_name in node_ip_mapping.keys():
        with open(node_name, 'w') as f:
            f.write(str(total_num-1) + '\n')
            for key, value in node_port_mapping.items():
                if key != node_name:
                    f.write(' '.join([key, "localhost", str(value)]) + '\n')
    return


if __name__ == '__main__':
    main()
