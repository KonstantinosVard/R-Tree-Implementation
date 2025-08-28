# Name: Konstantinos Vardakas 
# AM: 522

import heapq

def point_to_mbr_distance(q, mbr):
    '''
    Υπολογίζει την ελάχιστη ευκλείδεια απόσταση από το σημείο q σε ένα MBR.
    '''
    # Συντεταγμένες σημείου και mbr
    x, y = q
    min_x, max_x, min_y, max_y = mbr

    # Υπολογισμός μικρότερης απόστασης στους άξονες x και y
    # του σημείου από το mbr
    dx = max(min_x - x, 0, x - max_x)
    dy = max(min_y - y, 0, y - max_y)

    # Επιστροφή Ευκλείδειας απόστασης
    return (dx**2 + dy**2)**0.5

def knn_query(root, q, k):
    '''
    Εκτελεί best-first search για εύρεση k πλησιέστερων αντικειμένων προς το σημείο q.
    '''
    
    heap = []
    results = []
    
    # Counter για να μη χρειαστεί να συγκριθούν λεξικά,
    # tie-breaker όταν το distance είνιαι ίδιο
    counter = 0
    
    # Βάζουμε στο heap: (distance, counter, is_leaf, node)
    heapq.heappush(heap, (point_to_mbr_distance(q, root['mbr']), counter, 0, root))
    counter += 1
    
    while heap and len(results) < k: # όσο το heap δεν είναι άδειο και δεν έχουν βρεθεί τα k best
        dist, cnt, is_leaf, node = heapq.heappop(heap)
        
        # Αν είναι leaf, πρόσθεσε τα παιδιά στα results
        if is_leaf:
            results.append(node['id'])
        else: # Αλλιώς προσθεσε τα παιδια στο heap και έλεξχε αν τα child nodes έχουν child nodes (αν είναι leafs ή nodes)
            for child in node.get('children', []):
                is_leaf_child = int('children' not in child)  # 1 αν είναι leaf, 0 αν είναι node
                child_dist = point_to_mbr_distance(q, child['mbr'])
                heapq.heappush(heap, (child_dist, counter, is_leaf_child, child))
                counter += 1

    return results