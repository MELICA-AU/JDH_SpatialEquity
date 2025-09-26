
# ==== Exporting Files ====

## Core Data -- to be saved within the "script" folder of the JDH article repo

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
st_write(network_nodes, "script/network_nodes.geojson", delete_dsn = FALSE)
st_write(network_edges, "script/network_edges.geojson", delete_dsn = FALSE)

#### Export: connectivity data
edge_list <- as_data_frame(network, what = "edges")
node_list <- as_data_frame(network, what = "vertices")

write.csv(edge_list, "script/network_connectivity_edges.csv", row.names = FALSE)
write.csv(node_list, "script/network_connectivity_nodes.csv", row.names = FALSE)

print("Network data exported successfully!")

### Buildings
st_write(buildings, "script/buildings.gpkg", delete_dsn = FALSE)

## Municipal Boundaries
st_write(aarhus, "script/aarhus_mun.geojson", delete_dsn = FALSE)
st_write(aarhus_city1952, "script/aarhus_city1952.gpkg", delete_dsn = FALSE)

## Combined Shelter Dataset
st_write(shelters, "script/shelters.gpkg", delete_dsn = FALSE)

## Building-Shelter Pair Data
building_shelter_pairs_csv <- building_shelter_pairs %>%
  st_drop_geometry() # issues occur without dropping geometry here (it is re-merged in Python)

write.csv(building_shelter_pairs_csv, "script/building_shelter_pairs.csv", row.names = FALSE)

buildings_spatial <- building_shelter_pairs %>%
  select(id_lokalId, byg404Koordinat)

st_write(buildings_spatial, "script/buildings_from_pairs.gpkg", delete_dsn = FALSE)