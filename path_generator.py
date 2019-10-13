def get_paths(county_name):
    name = county_name
    shape_name = name + 'Precinct'
    shape_path = './NCElectionData/ClusterData/ShapeFiles/' + shape_name + '/' + shape_name
    data_path = './NCElectionData/ClusterData/ExtractedData/' + shape_name
    election_path = 'NCElectionData/ElectionData/results_pct_20121106.txt'
    centroid_data_file = 'CumberlandPrecinct_CENTROIDS.txt'
    return (name, shape_name, data_path, shape_path, election_path)