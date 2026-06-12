import pandas as pd
import numpy as np

class Helper:
##########################################################################################
    def convertTxToCSV(self, path, fileName):
        # Read the file
        with open(path, "r") as file:
            lines = file.readlines()

        # Extract vehicle capacity and number of vehicles
        vehicle_info_found = False
        vehicle_capacity = None
        num_vehicles = None
        for i, line in enumerate(lines):
            if line.strip().startswith("NUMBER") and "CAPACITY" in line:
                # The next line should contain the values
                values = lines[i + 1].strip().split()
                if len(values) == 2:
                    num_vehicles = int(values[0])
                    vehicle_capacity = int(values[1])
                    vehicle_info_found = True
                    break

        if not vehicle_info_found:
            raise ValueError("Vehicle information not found in the file.")

        # Find the start of the customer data
        start_index = None
        for i, line in enumerate(lines):
            if line.strip().startswith("CUST NO."):
                start_index = i + 1  # Data starts after the header
                break

        # Clean and parse the data lines
        customer_data = []
        for line in lines[start_index:]:
            if line.strip() == "":
                continue
            parts = line.strip().split()
            if len(parts) == 7:
                customer_data.append(parts)

        # Create a DataFrame
        columns = ["CUST_NO", "XCOORD", "YCOORD", "DEMAND", "READY_TIME", "DUE_DATE", "SERVICE_TIME"]
        df = pd.DataFrame(customer_data, columns=columns)

        # Convert to appropriate data types
        df = df.astype({
            "CUST_NO": int,
            "XCOORD": int,
            "YCOORD": int,
            "DEMAND": int,
            "READY_TIME": int,
            "DUE_DATE": int,
            "SERVICE_TIME": int
        })

        # Save to CSV
        df.to_csv(f"{fileName}.csv", index=False)
        print(f"CSV file '{fileName}.csv' created successfully.")
        return f"{fileName}.csv", vehicle_capacity, num_vehicles
    
###################################################################################################
    def DBScan(self,X:np.ndarray, eps:float, min_samples:float):
        n_points = X.shape[0]
        labels = np.full(n_points, -1, dtype=int)  # Initialize all points as noise
        cluster_id = 0
        
        def get_nearby(point_id):
            distances = np.linalg.norm(X - X[point_id], axis=1)
            return np.where(distances <= eps)[0]
        
        def expand_cluster(point_id, nearby, cluster_id):
            labels[point_id] = cluster_id
            
            i = 0
            while i < len(nearby):
                neighbor = nearby[i]
                
                if labels[neighbor] == -1:
                    labels[neighbor] = cluster_id
                    new_nearby = get_nearby(neighbor)
                    
                    if len(new_nearby) >= min_samples:
                        nearby = np.concatenate((nearby, new_nearby))
                
                i += 1
        
        for point_id in range(n_points):
            if labels[point_id] != -1:  # Skiping already processed points
                continue
            
            nearby = get_nearby(point_id)
            
            if len(nearby) >= min_samples:
                cluster_id += 1
                expand_cluster(point_id, nearby, cluster_id)
        
        return labels
    
##################################################################################################

    def solve_tsp(self, dist_matrix):
        """Solve TSP using nearest neighbor heuristic"""
        n = dist_matrix.shape[0]
        unvisited = set(range(n))
        current = 0  # Start at depot
        path = [current]
        unvisited.remove(current)
        total_cost = 0
        
        while unvisited:
            # Find nearest unvisited neighbor
            nearest = min(unvisited, key=lambda x: dist_matrix[current][x])
            total_cost += dist_matrix[current][nearest]
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Return to depot
        total_cost += dist_matrix[current][0]
        path.append(0)
        return path, total_cost
    
##################################################################################################
