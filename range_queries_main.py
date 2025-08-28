# Name: Konstantinos Vardakas 
# AM: 522

from range_queries_functions import *
import sys

def main(rtree_file='Rtree.txt', queries_file='Rqueries.txt'):

    # Φόρτωση του δέντρου από το αρχείο
    rtree = load_tree(rtree_file)

    # αρχικοποίηση λίστας με τα queries
    queries = []
    
    with open(queries_file, 'r') as f:
        for line in f:
            query = list(map(float, line.strip().split()))
            # format xmin, ymin, xmax, ymax
            # μετατρέπεται σε xmin, xmax, ymin, ymax
            query = [query[0], query[2], query[1], query[3]]
            queries.append(query)

    # Για κάθε query βρίσκονται τα δεδομένα που είναι εντός το w
    # και τυπώνονται σε αύξουσα σειρά
    for idx, w in enumerate(queries):
        results = range_query(rtree, w)
        results.sort()
        print(f"{idx} ({len(results)}):", ','.join(map(str, results)))
        print('\n')
        
if __name__ == '__main__':
    # Διάβασμα command line arguments
    args = sys.argv[1:]

    if len(args) > 2:
        print("Usage: python range_queries_main.py [rtree_file_path] [queries_file_path]")
        sys.exit(1)

    args = [arg if arg.endswith('.txt') else arg + '.txt' for arg in args]
        
    main(*args)