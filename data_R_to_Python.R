
# ==== Exporting Files ====

## Core Data 

### Network

#### Get nodes data
nodes_geom <- vertex_attr(network, "geometry")
nodes_index <- vertex_attr(network, ".tidygraph_node_index")

#### Create nodes sf object
network_nodes <- data.frame(.tidygraph_node_index = nodes_index) %>%
  st_sf(geometry = nodes_geom)

#### Get edges data  
edges_geom <- edge_attr(network, "geometry")
edges_index <- edge_attr(network, ".tidygraph_edge_index")

# # Check all available attributes (if needed)
# edge_attr_names(network)
# vertex_attr_names(network)

#### Get a few key edge attributes (remove/add more as needed)
edges_osm_id <- edge_attr(network, "osm_id")
edges_highway <- edge_attr(network, "highway")
edges_name <- edge_attr(network, "name")
edges_distance <- edge_attr(network, "distance_m")

#### Create edges sf object
network_edges <- data.frame(
  .tidygraph_edge_index = edges_index,
  osm_id = edges_osm_id,
  highway = edges_highway,
  name = edges_name,
  distance_m = edges_distance
) %>%
  st_sf(geometry = edges_geom)

#### Export: nodes + edges
st_write(network_nodes, "network_nodes.geojson", delete_dsn = FALSE)
st_write(network_edges, "network_edges.geojson", delete_dsn = FALSE)

#### Export: connectivity data
edge_list <- as_data_frame(network, what = "edges")
node_list <- as_data_frame(network, what = "vertices")

write.csv(edge_list, "network_connectivity_edges.csv", row.names = FALSE)
write.csv(node_list, "network_connectivity_nodes.csv", row.names = FALSE)

print("Network data exported successfully!")

### Buildings
st_write(buildings, "buildings.gpkg", delete_dsn = FALSE)

## Municipal Boundaries
st_write(aarhus, "aarhus_mun.geojson", delete_dsn = FALSE)
st_write(aarhus_city1952, "aarhus_city1952.gpkg", delete_dsn = FALSE)

## Combined Shelter Dataset
st_write(shelters, "shelters.gpkg", delete_dsn = FALSE)

## Building-Shelter Pair Data
building_shelter_pairs_csv <- building_shelter_pairs %>%
  st_drop_geometry() # issues occur without dropping geometry here (it is re-merged in Python)

write.csv(building_shelter_pairs_csv, "building_shelter_pairs.csv", row.names = FALSE)

buildings_spatial <- building_shelter_pairs %>%
  select(id_lokalId, byg404Koordinat)

st_write(buildings_spatial, "buildings_from_pairs.gpkg", delete_dsn = FALSE)