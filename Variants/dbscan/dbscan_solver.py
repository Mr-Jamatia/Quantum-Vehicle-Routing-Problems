import numpy as np
import pandas as pd
from helper import Helper
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from vehicle_routing_solution import VehicleRoutingSolution
import numpy as np
from FQS.VRP.solvers.vrp_solvers import FullQuboSolver, AveragePartitionSolver
from FQS.VRP.vrp_problem import VRPProblem
import time
from routing_solvers.routing_solvers import RoutingSolvers


######################################################################
####Author: Risav Pokhrel
####Github: https://github.com/Risav25Pokhrel
######################################################################

class DBScanSolver:
    
    def __init__(self,path):
        datapath=self.hp.convertTxToCSV(path=path,fileName="dataset1")
        self.df=pd.read_csv(datapath[0])
        customerPos=self.df.iloc[:,[1,2]].to_numpy()
        self.deport = self.df.iloc[[0]].copy()
        self.deport['cluster'] = -1#For starting point
        self.df = self.df.iloc[1:].reset_index(drop=True)
        self.numberOfVehicles=datapath[2]
        self.vehicleCapacity=datapath[1]
        self.customerPositions=self.df.iloc[:,[1,2]].to_numpy()
        self.numberOfCustomers=len(self.customerPositions)
        print("Data set Loaded")
        plt.figure(figsize=(14, 10))
        plt.scatter(customerPos[:,0],customerPos[:,1],s=10, c= "black")
        plt.title("Customer Positions")
        plt.show()
    
    customerPositions=None
    vehicleCapacity=None
    numberOfVehicles=None
    numberOfCustomers=None
    df=None
    deport=None
    isRecursionInitialized=False

    fig=None
    axes=None
    idx=0

    hp=Helper()

###########################################~~~~~DBSCAN SOLVER~~~~~#################################################
    def dbScan(self, min_radius: float, max_radius: float, max_cluster_size_const: int,solver:str="FQS"):
        final_cluster = None
        best_average_cluster_size = 0
        best_radius = 0
        
        # Store original bounds for debugging
        original_min = min_radius
        original_max = max_radius
        
        while min_radius < max_radius:
            radius = (min_radius + max_radius) / 2
            clusters = self.hp.DBScan(self.customerPositions, radius, min_samples=5)
            
            # Handle case where no clusters are formed (all points are noise)
            unique_clusters = np.unique(clusters)
            if len(unique_clusters) == 1 and unique_clusters[0] == -1:  # Only noise points
                max_radius = radius-1
                print(f"\nNo clusters formed at radius {radius}, reducing max_radius to {max_radius}")
                continue
                
            cluster_counts = np.unique(clusters, return_counts=True)[1]
            # Filter out noise points (cluster label -1) when calculating max size
            if -1 in unique_clusters:
                noise_idx = np.where(unique_clusters == -1)[0][0]
                cluster_counts = np.delete(cluster_counts, noise_idx)
            
            if len(cluster_counts) == 0:  # All points are noise
                max_radius = radius-1
                print(f"\nAll points are noise at radius {radius}, reducing max_radius")
                continue
                
            max_cluster_size = np.max(cluster_counts)
            num_actual_clusters = len(cluster_counts)  # Exclude noise
            
            print(f"Radius: {radius:.3f}, Max cluster size: {max_cluster_size}, Num clusters: {num_actual_clusters}")
            
            if max_cluster_size > max_cluster_size_const:
                max_radius = radius-1
                print(f"Max cluster size {max_cluster_size} exceeds limit {max_cluster_size_const}, reducing max_radius to {max_radius}")
            else:
                # Valid clustering found
                average_cluster_size = self.numberOfCustomers / num_actual_clusters
                
                if average_cluster_size > best_average_cluster_size:
                    best_average_cluster_size = average_cluster_size
                    final_cluster = clusters.copy()
                    best_radius = radius
                    print(f"\nNew best solution: radius {radius:.3f}, avg cluster size {average_cluster_size:.2f}")
                
                min_radius = radius+1
                print(f"Valid clustering found, increasing min_radius to {min_radius}\n")
            
            # Convergence check to prevent infinite loops
            if abs(max_radius - min_radius) < 0.001:  # Small epsilon
                print(f"Converged: min_radius={min_radius:.3f}, max_radius={max_radius:.3f}")
                break
        
        if final_cluster is None:
            print(f"No Solution Found...")
            print(f"Searched radius range: [{original_min:.3f}, {original_max:.3f}]")
            print(f"Final radius: {radius:.3f}")
            print("Try adjusting parameters: increase max_cluster_size_const or adjust radius range")
            return None
        
        print("\n~~~~~~~~~~~Cluster Formed~~~~~~~~~~~\n")
        print(f"Best radius: {best_radius:.3f} with average cluster size: {int(best_average_cluster_size)}\n")
        print(f"Checking Capacity Constraints, vehicle capacity: {self.vehicleCapacity}\n")
        
        # Work with a copy to avoid modifying the original DataFrame
        df_copy = self.df.copy()
        df_copy['cluster'] = pd.Series(final_cluster)
        clusteredResult = df_copy.groupby('cluster')
        
        isCapacityExceedByAnyCluster = False
        cluster_stats = []
        
        for cluster_label, group in clusteredResult:
            # Skip noise points (cluster label -1)
            if cluster_label == -1:
                print(f"Noise points: {len(group)} customers (will need individual handling)")
                continue
                
            total_demand = group['DEMAND'].sum()
            cluster_size = len(group)
            isCapacityExceeded = total_demand > self.vehicleCapacity
            
            if isCapacityExceeded:
                isCapacityExceedByAnyCluster = True
                
            status = "Vehicle Capacity Exceeded" if isCapacityExceeded else "OK"
            utilization="" if isCapacityExceeded else f", Utilization: {(total_demand*100/self.vehicleCapacity)}" 
            print(f"Cluster {cluster_label} - Size: {cluster_size}, Demand: {total_demand}, Status: {status} {utilization}")
            
            cluster_stats.append({
                'cluster_label': cluster_label,
                'size': cluster_size,
                'demand': total_demand,
                'capacity_exceeded': isCapacityExceeded
            })
        
        # Handle capacity constraint violations
        if isCapacityExceedByAnyCluster:
            print("\nCapacity constraints violated!")
            exceeded_clusters = [stat for stat in cluster_stats if stat['capacity_exceeded']]
            print(f"Clusters exceeding capacity: {[c['cluster_label'] for c in exceeded_clusters]}")
            print("Consider:")
            print("- Reducing max_cluster_size_const")
            print("- Using the recursive DBSCAN approach")
            print("- Increasing vehicle capacity")
            return None
        
        df_copy=pd.concat([self.deport,df_copy],ignore_index=True)
        print(f"\nAll capacity constraints satisfied! Proceeding with TSP optimization...")
        return self.applySolver(df_copy,solver)  # Use the copy with cluster labels
    

###########################################~~~~~Recursive DBSCAN~~~~~#################################################
    def recursiveDBScan(self, min_radius: float, max_radius: float, min_no_clusters: int, df: pd.DataFrame):
        print(f"Radius range: [{min_radius:.3f}, {max_radius:.3f}], min_clusters: {min_no_clusters}")
        self._initializeRecursion()
        isRecursionCalled=False
        best_clusters = None
        min_radius_const = min_radius
        orders = df.iloc[:, [1, 2]].to_numpy() 
        numberOfOrders = len(orders)
        best_average_cluster_size = 0
        best_radius = 0
        
        # Store original bounds
        original_min = min_radius
        original_max = max_radius
        
        # Binary search for optimal radius
        while min_radius < max_radius:
            radius = (min_radius + max_radius) * 0.5
            clusters = self.hp.DBScan(orders, radius, min_samples=5)
            
            # Count actual clusters (excluding noise points labeled -1)
            unique_clusters = np.unique(clusters)
            actual_clusters = unique_clusters[unique_clusters != -1]  # Remove noise
            noOfClusters = len(actual_clusters)
            
            print(f"\nRadius {radius:.3f}: {noOfClusters} clusters, {np.sum(clusters == -1)} noise points")
            
            if noOfClusters < min_no_clusters:
                max_radius = radius-1
                print(f"reducing max_radius to {max_radius:.3f}")
            else:
                min_radius = radius+1
                average_cluster_size = numberOfOrders / noOfClusters if noOfClusters > 0 else 0
                if average_cluster_size > best_average_cluster_size:
                    best_average_cluster_size = average_cluster_size
                    best_clusters = clusters.copy()
                    best_radius = radius
                    print(f"\nNew best: {noOfClusters} clusters, avg size {average_cluster_size:.1f}")
            
            # Convergence check
            if abs(max_radius - min_radius) < 0.01:
                break
        
        if best_clusters is None: 
            print(f"No solution found in range [{original_min:.3f}, {original_max:.3f}]")
            # Return original dataframe with single cluster label if no clustering works
            df_result = df.copy()
            df_result['cluster'] = 0  # Assign all points to cluster 0
            return df_result
        
        print(f"Best clustering: radius {best_radius:.3f}, {len(np.unique(best_clusters[best_clusters != -1]))} clusters")
        
        # Create working dataframe with cluster assignments
        df_working = df.copy()
        df_working['cluster'] = best_clusters
        
        # Process each cluster
        final_clusters = []
        next_cluster_id = 0  # Start fresh cluster numbering
        
        # Handle noise points first (cluster == -1)
        noise_points = df_working[df_working['cluster'] == -1].copy()
        if len(noise_points) > 0:
            print(f"\nProcessing {len(noise_points)} noise points as individual clusters")
            for _, point in noise_points.iterrows():
                point_df = point.to_frame().T
                point_df['cluster'] = next_cluster_id
                final_clusters.append(point_df)
                next_cluster_id += 1
        self._addToGraph(df_working)
        # Process actual clusters
        clustered_data = df_working[df_working['cluster'] != -1]
        if len(clustered_data) > 0:
            clusteredResult = clustered_data.groupby('cluster')
            
            for cluster_label, cluster in clusteredResult:
                cluster_demand = cluster['DEMAND'].sum()
                cluster_size = len(cluster)
                print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                print(f"Cluster {cluster_label}: {cluster_size} points, demand {cluster_demand}")
                if cluster_demand > self.vehicleCapacity:
                    print(f"\nCapacity exceeded ({cluster_demand} > {self.vehicleCapacity})")
                    print("################...recursing...########################")
                    # Prepare data for recursion (remove cluster column)
                    cluster_for_recursion = cluster.drop('cluster', axis=1, errors='ignore')
                    
                    # Recursive call with adjusted parameters
                    sub_result = self.recursiveDBScan(
                        min_radius=min_radius_const * 0.8,
                        max_radius=best_radius * 0.9,  # Slightly smaller than current radius
                        min_no_clusters=2,
                        df=cluster_for_recursion
                    )
                    
                    if sub_result is not None and len(sub_result) > 0:
                        # Relabel clusters to avoid conflicts
                        sub_result = sub_result.copy()
                        sub_result['cluster'] = sub_result['cluster'] + next_cluster_id
                        next_cluster_id = sub_result['cluster'].max() + 1
                        final_clusters.append(sub_result)
                        isRecursionCalled=True
                        print(f"\nRecursion successful: split into {len(sub_result['cluster'].unique())} subclusters")
                        
                    else:
                        print(f"\nRecursion failed, keeping single overloaded cluster")
                        cluster_copy = cluster.copy()
                        cluster_copy['cluster'] = next_cluster_id
                        final_clusters.append(cluster_copy)
                        next_cluster_id += 1
                    print("="*60)
                else:
                    # Cluster satisfies capacity constraint
                    print(f"\nCapacity OK, keeping cluster")
                    cluster_copy = cluster.copy()
                    cluster_copy['cluster'] = next_cluster_id
                    final_clusters.append(cluster_copy)
                    next_cluster_id += 1
        
        # Combine all processed clusters
        if final_clusters:
            final_result = pd.concat(final_clusters, ignore_index=True)
            print(f"\nFinal result: {len(final_result)} points in {len(final_result['cluster'].unique())} clusters")
        else:
            print(f"\nNo clusters processed, returning original data")
            final_result = df.copy()
            final_result['cluster'] = 0
        
        # Final capacity check and reporting
        print("-"*60)
        print(f"\n--- Final Capacity Check ---")
        isCapacityExceedByAnyCluster = False
        
        for cluster_id in final_result['cluster'].unique():
            cluster_data = final_result[final_result['cluster'] == cluster_id]
            total_demand = cluster_data['DEMAND'].sum()
            isCapacityExceeded = total_demand > self.vehicleCapacity
            if isCapacityExceeded:
                isCapacityExceedByAnyCluster = True
            status = "EXCEEDED" if isCapacityExceeded else "OK"
            utilization="" if isCapacityExceeded else f", Utilization: {(total_demand*100/self.vehicleCapacity)}"
            print(f"Cluster {cluster_id}: {len(cluster_data)} points, demand {total_demand}, status {status} {utilization}")
        print("-"*60)

        if isCapacityExceedByAnyCluster:
            print("\nSome clusters still exceed capacity constraints")
        else:
            print("\nAll capacity constraints satisfied")
            
        if(isRecursionCalled):
            self._addToGraph(final_result)
        return final_result
    
###########################################~~~~~Recursive DBSCAN SOLVER~~~~~#################################################
    def applyRecursiveDBScan(self,min_radius:float,max_radius:float,min_no_clusters:int,solver:str="FQS"):
        print(f"Vehicle Capacity: {self.vehicleCapacity}")
        cluster =self.recursiveDBScan(min_radius=min_radius,max_radius=max_radius,min_no_clusters=min_no_clusters,df=self.df)
        if cluster is not None:
            return self.applySolver(clusters=cluster,solver=solver)
    
############################################################################################
    def _initializeRecursion(self):
        if self.isRecursionInitialized:
            return
        self.isRecursionInitialized=True
        # Store plot data instead of creating plots immediately
        self.plot_data = []

    def _addToGraph(self, df):
        """Store clustering data for later visualization"""
        if not hasattr(self, 'plot_data'):
            self.plot_data = []
            
        # Store the dataframe for this clustering step
        plot_step = {
            'step': self.idx,
            'data': df.copy(),
            'title': f'Clustering Step {self.idx + 1}'
        }
        self.plot_data.append(plot_step)
        
        print(f"Stored visualization data for step {self.idx + 1}")
        # Increment index for next plot
        self.idx += 1
############################################################################################
    def visualizeRecursion(self):
        """Show all the clustering steps visualized during recursive DBSCAN"""
        if not self.isRecursionInitialized or not hasattr(self, 'plot_data') or len(self.plot_data) == 0:
            print("No recursion visualization data available. Run applyRecursiveDBScan first.")
            return
        
        num_plots = len(self.plot_data)
        print(f"Visualizing {num_plots} clustering steps...")
        
        # Calculate optimal subplot layout
        if num_plots == 1:
            rows, cols = 1, 1
        elif num_plots <= 4:
            rows, cols = 2, 2
        elif num_plots <= 6:
            rows, cols = 2, 3
        elif num_plots <= 9:
            rows, cols = 3, 3
        elif num_plots <= 12:
            rows, cols = 3, 4
        else:
            rows, cols = 4, 4  # Maximum 16 plots
            if num_plots > 16:
                print(f"Warning: Only showing first 16 of {num_plots} plots")
                num_plots = 16
        
        # Create figure with appropriate size
        _, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
        
        # Handle single subplot case
        if rows == 1 and cols == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        # Plot each clustering step
        for i, plot_info in enumerate(self.plot_data[:num_plots]):
            ax = axes[i]
            df = plot_info['data']
            
            # Get unique clusters
            unique_clusters = sorted(df['cluster'].unique())
            colors = plt.cm.tab10(np.linspace(0, 1, len(unique_clusters)))
            
            # Plot each cluster with different colors
            for j, cluster_id in enumerate(unique_clusters):
                cluster_data = df[df['cluster'] == cluster_id]
                
                # Try different column name possibilities
                x_coords, y_coords = None, None
                             

                x_coords = cluster_data['XCOORD'].values
                y_coords = cluster_data['YCOORD'].values
                        
                

                if x_coords is None and len(cluster_data.columns) >= 3:
                    x_coords = cluster_data.iloc[:, 1].values  
                    y_coords = cluster_data.iloc[:, 2].values 
                
                if x_coords is not None and y_coords is not None:
                    ax.scatter(x_coords, y_coords, 
                              c=[colors[j]], 
                              label=f'Cluster {cluster_id}' if len(unique_clusters) <= 10 else None,
                              s=18, linewidth=0.5)
                else:
                    print(f"Warning: Could not find coordinate columns in step {i+1}")
            
            ax.set_title(plot_info['title'])
            ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for i in range(num_plots, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.show()
############################################################################################
    def resetVisualization(self):
        """Reset visualization state for new runs"""
        self.isRecursionInitialized = False
        self.idx = 0
        self.fig = None
        self.axes = None

###########################################~~~~~Call DIFFERENT SOlver~~~~~#################################################

    def applySolver(self, clusters: pd.DataFrame,solver:str="FQS"):
        """
        Apply solver to each cluster
        Returns: tuple of (clusters DataFrame, list of VehicleRoutingSolution objects)
        """
        print(f"\n~~~~~~~~~~~Applying {solver}~~~~~~~~~~~")
        
        # Group clusters (excluding depot if it exists)
        cluster_data = clusters[clusters['cluster'] != -1]  # Exclude depot cluster
        clusterList = cluster_data.groupby('cluster')
        
        routingSolution: list[VehicleRoutingSolution] = []
        total_clusters = len(clusterList)
        
        print(f"Processing {total_clusters} clusters for {solver}...")
        
        for cluster_id, cluster_group in clusterList:
            print(f"\n--- Processing Cluster {cluster_id} ---")
            
            # Create a copy to avoid modifying original data
            cluster_df = cluster_group.copy()
            
            # Add depot as the starting/ending point for this route
            # The depot should be the first point (index 0) in the route
            route_data = pd.concat([self.deport, cluster_df], ignore_index=True)
            
            # Extract coordinates - try different column name possibilities
            routingSolver=RoutingSolvers(cluster=route_data,vehicleCapacities=[self.vehicleCapacity])

            # Solve TSP starting and ending at depot (index 0)
            try:
                # path, total_cost = self.hp.solve_tsp(dist_matrix)
                solution=routingSolver.applySolver(solver=solver)
                print(f"Cluster {cluster_id} - Path: {solution.path}")
                # print(f"Cluster {cluster_id} - Total Cost: {total_cost:.2f}")
                
                # Calculate cluster statistics
                cluster_demand = cluster_df['DEMAND'].sum()
                cluster_size = len(cluster_df)
                utilization = (cluster_demand / self.vehicleCapacity) * 100
                
                print(f"Cluster {cluster_id} - Customers: {cluster_size}")
                print(f"Cluster {cluster_id} - Total Demand: {cluster_demand}")
                print(f"Cluster {cluster_id} - Vehicle Utilization: {utilization:.1f}%")
                
                routingSolution.append(solution)
                
            except Exception as e:
                print(f"Error solving ${solver} for cluster {cluster_id}: {str(e)}")
                continue
        
        print(f"\n~~~~~~~~~~~{solver} Complete~~~~~~~~~~~")
        print(f"Successfully processed {len(routingSolution)} out of {total_clusters} clusters")
        
        # Calculate and display summary statistics
        if routingSolution:
            total_distance = sum(sol.totalCost for sol in routingSolution)
            total_vehicles_used = len(routingSolution)
            
            print(f"\n--- Solution Summary ---")
            print(f"Total Vehicles Used: {total_vehicles_used}/{self.numberOfVehicles}")
            print(f"Total Distance: {total_distance:.2f}")
            print(f"Average Distance per Vehicle: {total_distance/total_vehicles_used:.2f}")
            
            # Check if we have enough vehicles
            if total_vehicles_used > self.numberOfVehicles:
                print(f"Warning: Solution requires {total_vehicles_used} vehicles but only {self.numberOfVehicles} available!")
        
        return clusters, routingSolution
    
#########################################~~~~~~~~~~~~~~~~SPS~~~~~~~~~~~~~~~~~#################################
    def visualizeVRPSolution(self, routing_solutions: list[VehicleRoutingSolution], title_prefix="VRP Solution"):
        """Visualize VRP solution with enhanced plotting"""
        if not routing_solutions:
            print("No routing solutions to visualize")
            return
            
        plt.figure(figsize=(14, 10))
        colors = plt.cm.tab10.colors
        
        # Calculate total cost
        total_cost = sum(sol.totalCost for sol in routing_solutions)
        total_vehicles = len(routing_solutions)
        
        # Get depot coordinates from first solution
        depot_coords = None
        all_coords = []
        all_demands = []
        
        # Collect all coordinates and find depot
        for solution in routing_solutions:
            cluster_data = solution.cluster

            coords = cluster_data[['XCOORD', 'YCOORD']].values

            if depot_coords is None:
                depot_coords = coords[0]  # First point is depot
            
            # Collect customer coordinates (excluding depot)
            customer_coords = coords[1:]
            all_coords.extend(customer_coords)
            
            # Collect demands for customers

            customer_data = cluster_data.iloc[1:]  # Skip depot
            if 'DEMAND' in customer_data.columns:
                all_demands.extend(customer_data['DEMAND'].values)
        
        # Convert to numpy array for easier handling
        all_coords = np.array(all_coords)
        
        # Plot all customer nodes
        if len(all_coords) > 0:
            demands = getattr(self, 'all_demands', [10] * len(all_coords))
            plt.scatter(
                all_coords[:, 0], all_coords[:, 1],
                s=np.array(demands) * 15,
                c='blue',
                alpha=0.8,
                edgecolors='black',
                label='Customers'
            )
        
        # Plot depot
        if depot_coords is not None:
            plt.scatter(
                depot_coords[0], depot_coords[1],
                s=400,
                c='red',
                marker='s',
                edgecolors='black',
                label='Depot'
            )
        
        # Annotate customer demands
        for solution in routing_solutions:
            cluster_data = solution.cluster
            customer_data = cluster_data.iloc[1:]  # Skip depot
            
            for _, customer in customer_data.iterrows():

                x, y = customer['XCOORD'], customer['YCOORD']

                demand = customer.get('DEMAND', 10)
                plt.annotate(
                    f"{int(demand)}",
                    (x, y),
                    xytext=(0, 8),
                    textcoords='offset points',
                    ha='center',
                    fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7)
                )
        
        # Plot routes
        for i, solution in enumerate(routing_solutions):
            cluster_data = solution.cluster
            path = solution.path
            
            if len(path) > 2:  # Skip empty routes
                # Get coordinates for this route

                coords = cluster_data[['XCOORD', 'YCOORD']].values

                route_coords = coords[path]
                
                # Calculate total demand for this vehicle
                customer_data = cluster_data.iloc[1:]  # Skip depot
                total_demand = customer_data['DEMAND'].sum() if 'DEMAND' in customer_data.columns else 0
                
                # Plot route line
                plt.plot(
                    route_coords[:, 0], route_coords[:, 1],
                    'o-',
                    color=colors[i % len(colors)],
                    linewidth=2.5,
                    markersize=4,
                    markerfacecolor='white',
                    markeredgewidth=1.5,
                    label=f"Vehicle {i+1} ({int(total_demand)} cap)"
                )
                
                # Add direction arrows
                for j in range(1, len(route_coords)):
                    start = route_coords[j-1]
                    end = route_coords[j]
                    plt.annotate(
                        "",
                        xy=end,
                        xytext=start,
                        arrowprops=dict(
                            arrowstyle="->",
                            color=colors[i % len(colors)],
                            lw=2,
                            shrinkA=8,
                            shrinkB=8
                        )
                    )
        
        # Format total cost display
        cost_str = f"{total_cost:.2f}" if total_cost != float('inf') else "inf"
        
        plt.title(f"{title_prefix} | Total Cost: {cost_str} | Vehicles: {total_vehicles}", fontsize=14)
        plt.xlabel("X Coordinate", fontsize=12)
        plt.ylabel("Y Coordinate", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='best', fontsize=10)
        plt.tight_layout()
        plt.show()
        