"""
Saksham Singh
BocaFinder
"""

import pygame
import sys
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.Font(None, 24)

# Graph variables
vertices = []  
edges = [] 
radius = 15
selected_vertex = None
anchor_point = None
selected_nodes = []
shortest_path = [] 
shortest_distance = float('inf')
phase = "drawing"  

submit_button_rect = pygame.Rect(650, 500, 120, 40)
find_distance_button_rect = pygame.Rect(650, 550, 120, 40)

# Alpha value for weighting distance vs. hops
alpha = 0.7  # Adjust this value between 0 and 1

def draw_grid():
    """Draws a grid as the background for the graph."""
    grid_color = (220, 220, 220)
    grid_size = 40  # Size of each grid cell
    
    # Draw vertical lines
    for x in range(0, 800, grid_size):
        pygame.draw.line(screen, grid_color, (x, 0), (x, 600), 1)
    
    # Draw horizontal lines
    for y in range(0, 600, grid_size):
        pygame.draw.line(screen, grid_color, (0, y), (800, y), 1)

def draw_graph(path=None):
    screen.fill((255, 255, 255))  # Clear screen with white background
    
    # Draw grid behind everything
    draw_grid()

    # Draw edges
    for edge in edges:
        pygame.draw.line(screen, (0, 0, 0), vertices[edge[0]], vertices[edge[1]], 2)
    
    # Highlight the path in a different color, if available
    if path:
        for i in range(len(path) - 1):
            pygame.draw.line(screen, (255, 0, 0), vertices[path[i]], vertices[path[i+1]], 4)
    
    # Draw vertices with visual cues for selected nodes
    for i, (x, y) in enumerate(vertices):
        if i == anchor_point:
            color = (0, 255, 0)  # Green for anchor point
        elif i in selected_nodes:
            color = (0, 0, 255)  # Blue for selected target nodes
        else:
            color = (0, 0, 0)  # Black for other nodes

        pygame.draw.circle(screen, color, (x, y), radius)
        text = font.render(str(i + 1), True, (255, 255, 255))
        screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))
    
    # Draw Submit and Find Distance buttons
    pygame.draw.rect(screen, (0, 200, 0), submit_button_rect)
    submit_text = font.render("Submit", True, (255, 255, 255))
    screen.blit(submit_text, (submit_button_rect.x + 15, submit_button_rect.y + 10))

    pygame.draw.rect(screen, (0, 100, 200), find_distance_button_rect)
    find_distance_text = font.render("Find Distance", True, (255, 255, 255))
    screen.blit(find_distance_text, (find_distance_button_rect.x + 5, find_distance_button_rect.y + 10))

    pygame.display.flip()  # Update the display

def find_vertex(pos):
    """Return the index of the vertex if the pos is within radius, else None."""
    for i, (x, y) in enumerate(vertices):
        if (x - pos[0]) ** 2 + (y - pos[1]) ** 2 <= radius ** 2:
            return i
    return None

def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def build_adjacency_list():
    """Convert edges to an adjacency list with weights based on Euclidean distances."""
    adj_list = {i: [] for i in range(len(vertices))}
    for edge in edges:
        u, v = edge
        distance = calculate_distance(vertices[u], vertices[v])
        adj_list[u].append((v, distance))
        adj_list[v].append((u, distance))  # Since this is an undirected graph
    return adj_list

def dijkstra_with_combined_cost(start, end, alpha):
    adj_list = build_adjacency_list()
    distances = {i: float('inf') for i in range(len(vertices))}
    previous = {i: None for i in range(len(vertices))}
    distances[start] = 0
    unvisited = set(range(len(vertices)))
    hops = {i: 0 for i in range(len(vertices))}
    while unvisited:
        # Find the vertex with the smallest combined cost
        current = min(unvisited, key=lambda vertex: alpha * distances[vertex] + (1 - alpha) * hops[vertex])
        unvisited.remove(current)
        if current == end:
            break
        for neighbor, weight in adj_list[current]:
            new_distance = distances[current] + weight
            new_hops = hops[current] + 1
            new_cost = alpha * new_distance + (1 - alpha) * new_hops
            if new_cost < alpha * distances[neighbor] + (1 - alpha) * hops[neighbor]:
                distances[neighbor] = new_distance
                hops[neighbor] = new_hops
                previous[neighbor] = current
    path = []
    current = end
    while previous[current] is not None:
        path.insert(0, current)
        current = previous[current]
    if path:
        path.insert(0, start)
    return path

def main():
    global anchor_point, selected_nodes, shortest_path, shortest_distance, phase
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Check if Submit button is clicked
                if submit_button_rect.collidepoint(pos):
                    phase = "selecting"  # Change phase to "selecting" for choosing nodes

                # Check if Find Distance button is clicked in selecting phase
                elif find_distance_button_rect.collidepoint(pos) and phase == "selecting":
                    if anchor_point is not None and selected_nodes:
                        shortest_path = None
                        shortest_distance = float('inf')  # Reset shortest distance

                        # Find the shortest path among selected nodes
                        for node in selected_nodes:
                            path = dijkstra_with_combined_cost(anchor_point, node, alpha)
                            path_length = sum(calculate_distance(vertices[path[i]], vertices[path[i+1]]) for i in range(len(path) - 1))
                            
                            if path_length < shortest_distance:
                                shortest_distance = path_length
                                shortest_path = path
                        if shortest_path:
                            print(f"Shortest path to node {selected_nodes[0] + 1}: {shortest_path}, Length: {shortest_distance:.2f}")
                    else:
                        print("Nothing found, please select anchor and target nodes.")

                else:
                    vertex_index = find_vertex(pos)
                    
                    if vertex_index is not None:
                        if phase == "drawing":
                            # Drawing phase: add edges
                            if selected_vertex is None:
                                selected_vertex = vertex_index
                            else:
                                if selected_vertex != vertex_index and (selected_vertex, vertex_index) not in edges:
                                    edges.append((selected_vertex, vertex_index))
                                    edges.append((vertex_index, selected_vertex))  # Add both directions
                                selected_vertex = None
                        elif phase == "selecting":
                            # Selecting phase: choose anchor point or multiple target nodes
                            if anchor_point is None:
                                anchor_point = vertex_index  # Set anchor point
                            elif vertex_index not in selected_nodes:
                                selected_nodes.append(vertex_index)  # Add node to selected nodes
                    elif phase == "drawing":
                        # If clicking empty space, create a new vertex in drawing phase
                        vertices.append(pos)
                        selected_vertex = None  # Reset selected vertex

        draw_graph(path=shortest_path)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
