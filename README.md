# Geospatial Data Management Project: R-Tree Implementation

### MSc Data Science & Engineering · Complex Data Management Course · Project 2/4: Geospatial Data

## Overview

This project implements a geospatial data management system using R-Trees for efficient spatial queries. It consists of three main components:
1. **R-Tree construction** via bulk loading using Z-order curves
2. **Range queries** implementation using depth-first search
3. **k-Nearest Neighbor (k-NN) queries** implementation using best-first search

## File Structure

### Data Files:
- `coords.txt` - Contains coordinate data for spatial objects
- `offsets.txt` - Contains grouping information for polygons
- `Rqueries.txt` - Contains range query windows
- `NNqueries.txt` - Contains k-NN query points
- `Rtree.txt` - Output file containing the R-Tree structure (created after program execution)

### Source Code Files:

#### R-Tree Construction:
- `rtree_init_functions.py` - Helper functions for R-Tree construction
- `rtree_init_main.py` - Main program for building the R-Tree

#### Range Queries:
- `range_queries_functions.py` - Helper functions for range queries
- `range_queries_main.py` - Main program for executing range queries

#### k-NN Queries:
- `knn_queries_functions.py` - Helper functions for k-NN queries
- `knn_queries_main.py` - Main program for executing k-NN queries

## Installation & Execution

### Prerequisites:
- Python 3.x
- Required libraries: `pymorton`

### Execution Instructions:

1. **Place all files in the same directory**
2. **Open terminal in the project directory**

#### Build R-Tree:
```bash
python rtree_init_main.py [coords_path] [offsets_path] [output_path]
```
- Default values: `coords.txt`, `offsets.txt`, `Rtree.txt`
- Example: `python rtree_init_main.py coords.txt offsets.txt Rtree.txt`

#### Execute Range Queries:
```bash
python range_queries_main.py [rtree_file] [queries_file]
```
- Default values: `Rtree.txt`, `Rqueries.txt`
- Example: `python range_queries_main.py Rtree.txt Rqueries.txt`

#### Execute k-NN Queries:
```bash
python knn_queries_main.py [rtree_file] [queries_file] [k]
```
- Default values: `Rtree.txt`, `NNqueries.txt`, `10`
- Example: `python knn_queries_main.py Rtree.txt NNqueries.txt 5`

**Note:** File extensions (.txt) are optional in command arguments.

## Implementation Details

### R-Tree Construction:
- Uses Z-order curve for spatial ordering
- Implements bulk loading with node capacity of 20 (max) and 8 (min)
- Creates MBRs (Minimum Bounding Rectangles) for spatial objects
- Stores tree structure in DFS-sorted format

### Range Queries:
- Implements depth-first search with MBR intersection checking
- Efficiently prunes non-intersecting subtrees
- Returns all objects intersecting with query window

### k-NN Queries:
- Implements best-first search using priority queue
- Uses Euclidean distance for proximity calculations
- Efficiently finds k nearest neighbors to query point

## Output

- **Rtree.txt**: Contains the complete R-Tree structure with nodes sorted by ID
- **Range Query Results**: Returns objects intersecting with query windows
- **k-NN Query Results**: Returns k nearest objects to query points

## Testing

The implementation includes verification mechanisms:
- Hash comparison between original and reconstructed trees
- Consistent node structure validation
- Proper handling of edge cases (minimum node capacity, exact ties in distances)

## Notes

- The R-Tree construction uses Z-order curves for spatial clustering
- Leaf nodes contain actual data objects with their MBRs
- Internal nodes contain MBRs that encompass all child nodes
- The implementation ensures data consistency through proper reference handling

## Author

**Konstantinos Vardakas**  

---

*This project demonstrates the effective implementation of R-Trees for spatial data organization and the efficiency of specialized search algorithms for range and k-nearest neighbor queries in geospatial data management.*
