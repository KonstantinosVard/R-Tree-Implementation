# Name: Konstantinos Vardakas 
# AM: 522

from rtree_init_functions import *
import sys

def main(coords_path = 'coords.txt', offsets_path = 'offsets.txt', output_path='Rtree.txt'):
    # Δίαβασμα αρχείων σε δύο λίστες
    coords, offsets = read_data(coords_path, offsets_path)

    # Δημιουργία της λίστας objects
    objects = build_mbrs(coords, offsets)
    objects = delete_z(objects)

    # Δημιουργία του rtree
    rtree_root = build_rtree(objects)

    # Εκτύπωση των στατιστικών του δέντρου
    tree_stats(rtree_root)

    # Αποθήκευση των δεδομένων σε αρχείο
    write_rtree_to_file_dfs_sorted(rtree_root, output_path)
    

if __name__ == "__main__":
    # Διάβασμα command line arguments
    args = sys.argv[1:]

    if len(args) > 3:
        print("Usage: python rtree_init_main.py [coords_path] [offsets_path] [output_file]")
        sys.exit(1)

    args = [arg if arg.endswith('.txt') else arg + '.txt' for arg in args]
        
    main(*args)