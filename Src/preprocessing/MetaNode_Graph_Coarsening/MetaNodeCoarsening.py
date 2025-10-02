import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
# Defining the Meta-Node
class MetaNode:
    def __init__(self, node_id, original_nodes, demand, ready_time, due_date, service_time, x, y, internal_sequence=None):
        self.id = node_id
        self.nodes = original_nodes
        self.demand = demand
        self.ready_time = ready_time
        self.due_date = due_date
        self.service_time = service_time
        self.x = x
        self.y = y
        self.internal_sequence = internal_sequence if internal_sequence else [node_id]

    def __repr__(self):
        return f"MetaNode(id={self.id}, nodes={self.nodes}, demand={self.demand}, window=[{self.ready_time}, {self.due_date}])"

def load_solomon_data(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    vehicle_info = lines[4].strip().split()
    vehicle_capacity = int(vehicle_info[1])
    data = []
    for line in lines[9:]:
        parts = line.strip().split()
        if not parts:
            continue
        customer_id, x, y, demand, ready_time, due_date, service_time = map(float, parts)
        data.append([int(customer_id), x, y, int(demand), ready_time, due_date, service_time])
    df = pd.DataFrame(data, columns=["id", "x", "y", "demand", "ready_time", "due_date", "service_time"])
    df.set_index("id", inplace=True)
    return df, vehicle_capacity


def coarsen_cvrptw_problem(df, vehicle_capacity, target_node_count):
    # Initializing MetaNodes from the original customer data
    nodes = {}
    for idx, row in df.iterrows():
        node_id = int(idx)
        nodes[node_id] = MetaNode(
            node_id=node_id,
            original_nodes=[node_id],
            demand=row['demand'],
            ready_time=row['ready_time'],
            due_date=row['due_date'],
            service_time=row['service_time'],
            x=row['x'],
            y=row['y']
        )
    
    # Exclude depot
    depot = nodes.pop(0)
    
    # Coarsen until the target size is reached
    iteration = 0
    while len(nodes) > target_node_count:
        iteration += 1
        # Recompute distance matrix for current set of meta-nodes
        current_node_ids = list(nodes.keys())
        coords = np.array([[nodes[nid].x, nodes[nid].y] for nid in current_node_ids])
        dist_matrix = pd.DataFrame(
            np.sqrt(((coords[:, np.newaxis, :] - coords[np.newaxis, :, :]) ** 2).sum(axis=2)),
            index=current_node_ids,
            columns=current_node_ids
        )
        best_merge = {'score': float('inf'), 'pair': None, 'new_node': None}
        for id1, id2 in itertools.combinations(current_node_ids, 2):
            node1, node2 = nodes[id1], nodes[id2]
            
            if node1.demand + node2.demand > vehicle_capacity:
                continue
            p_d = (node1.demand + node2.demand) / vehicle_capacity
            t_12 = dist_matrix.loc[id1, id2]
            cost_12 = node1.service_time + t_12 + node2.service_time
            e_m_12 = node1.ready_time
            l_m_12 = min(node1.due_date, node2.due_date - node1.service_time - t_12) 
            cost_21 = node2.service_time + t_12 + node1.service_time
            e_m_21 = node2.ready_time
            l_m_21 = min(node2.due_date, node1.due_date - node2.service_time - t_12) 
            is_12_feasible = e_m_12 <= l_m_12
            is_21_feasible = e_m_21 <= l_m_21
            if not is_12_feasible and not is_21_feasible:
                continue
            if is_12_feasible and (not is_21_feasible or cost_12 <= cost_21):
                internal_seq = node1.internal_sequence + node2.internal_sequence
                new_service_time = cost_12
                new_ready_time = e_m_12
                new_due_date = l_m_12
            else:
                internal_seq = node2.internal_sequence + node1.internal_sequence
                new_service_time = cost_21
                new_ready_time = e_m_21
                new_due_date = l_m_21
            p_c = t_12 / dist_matrix.max().max() if dist_matrix.max().max() > 0 else 0
            window_span = new_due_date - new_ready_time
            p_t = 1 / (1 + window_span) if window_span > 0 else 1            
            score = 0.4 * p_c + 0.4 * p_t + 0.2 * p_d
            if score < best_merge['score']:
                new_demand = node1.demand + node2.demand
                new_node_id = min(id1, id2)
                new_node = MetaNode(
                    node_id=new_node_id,
                    original_nodes=node1.nodes + node2.nodes,
                    demand=new_demand,
                    ready_time=new_ready_time,
                    due_date=new_due_date,
                    service_time=new_service_time,
                    x=(node1.x * node1.demand + node2.x * node2.demand) / new_demand,
                    y=(node1.y * node1.demand + node2.y * node2.demand) / new_demand,
                    internal_sequence=internal_seq
                )
                best_merge.update({'score': score, 'pair': (id1, id2), 'new_node': new_node})

        # Perform the best merge for this iteration
        if best_merge['pair'] is None:
            print(f"\nStopping at iteration {iteration}: No more feasible merges found.")
            break     
        id1, id2 = best_merge['pair']
        new_node = best_merge['new_node']
        #delete old nodes and add new merged node
        del nodes[id1]
        del nodes[id2]
        nodes[new_node.id] = new_node
        
        if iteration % 10 == 0:
            print(f"Iteration {iteration}: Merged {id1} & {id2} -> New node {new_node.id}. Remaining: {len(nodes)}")
    
    final_nodes = [depot] + list(nodes.values())
    return final_nodes
