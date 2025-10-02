import os
import time
import pandas as pd
from MetaNodeCoarsening import load_solomon_data, coarsen_cvrptw_problem

def process_all_instances(data_dir, output_csv, target_size=20):
    results = []

    for filename in os.listdir(data_dir):
        if filename.lower().endswith(".txt"):
            filepath = os.path.join(data_dir, filename)
            try:
                start_time = time.time()

                df, vehicle_capacity = load_solomon_data(filepath)
                reduced_nodes = coarsen_cvrptw_problem(df, vehicle_capacity, target_size)

                elapsed_time = time.time() - start_time

                for node in reduced_nodes:
                    results.append({
                        "instance": filename,
                        "node_id": node.id,
                        "original_nodes": node.nodes,
                        "num_original_nodes": len(node.nodes),
                        "demand": node.demand,
                        "ready_time": node.ready_time,
                        "due_date": node.due_date,
                        "service_time": node.service_time,
                        "x": node.x,
                        "y": node.y,
                        "processing_time_sec": elapsed_time
                    })

                print(f"Processed {filename}: reduced to {len(reduced_nodes)} nodes in {elapsed_time:.2f} sec.")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_csv, index=False)
    print(f"\nAll results saved to {output_csv}")

if __name__ == "__main__":
    process_all_instances(data_dir="Data\Global_Datasets\Solomon", output_csv="coarsening_results_2.csv", target_size=2)
