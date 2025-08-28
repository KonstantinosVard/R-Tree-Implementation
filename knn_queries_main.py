# Name: Konstantinos Vardakas 
# AM: 522

from knn_queries_functions import *
from range_queries_functions import load_tree
import sys

def main(rtree_file = 'Rtree.txt', queries_file = 'NNqueries.txt', k=10):
    # φόρτωση του δέντρου
    rtree = load_tree(rtree_file)
    
    # Διάβασμα των queries και μετατροπή σε float
    with open(queries_file, 'r') as f:
        queries = [list(map(float, line.strip().split())) for line in f]

    # Εύρεση k κοντινότερων γειτόνων για κάθε query
    for idx, q in enumerate(queries):
        q_point = (q[0], q[1])
        results = knn_query(rtree, q_point, k)
        print(f"Query {idx}:", ','.join(map(str, results)))


if __name__ == "__main__":
    # Διάβασμα command line arguments
    args = sys.argv[1:]

    if len(args) > 3:
        print("Usage: python knn_queries_main.py [rtree_file_path] [queries_file_path] [k]")
        sys.exit(1)

    if len(args) == 3:
        args[-1] = int(args[-1])
        
    args = [arg if type(arg) == int or arg.endswith('.txt') else arg + '.txt' for arg in args]

    main(*args)