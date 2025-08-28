# Name: Konstantinos Vardakas 
# AM: 522

from pymorton import interleave_latlng
from collections import deque

def read_data(coords_path, offsets_path):
    '''
    Διαβασμα των αρχείων coords.txt και offsets.txt σε δύο λίστες 
    coords = [[x1,y1], [x2,y2], ...]
    offsets = [[id1, start_idx1, end_idx1], ...]
    '''
    with open(coords_path, 'r') as f:
        coords = [line.strip().split(',') for line in f.readlines()]
    coords = [[float(x), float(y)] for x, y in coords]  # Μετατροπή σε float

    with open(offsets_path, 'r') as f:
        offsets = [line.strip().split(',') for line in f.readlines()]
    offsets = [[int(id), int(start), int(end)] for id, start, end in offsets]  # Μετατροπή σε ακέραιους

    return coords, offsets


def compute_mbr(coords):
    '''
    Υπολογίζει το MBR ενός πολυγώνου με coords [[x1,y1], [x2,y2], ...]
    δηλαδή coords[i][0] -> συντεταγμένες x, coords[i][1] -> συντεταγμένες y

    Helper που χρησιμοποιείται στην ακόλουθη συνάρτηση build_mbrs
    '''
    x_vals = [coord[0] for coord in coords]
    y_vals = [coord[1] for coord in coords]
    
    return [min(x_vals), max(x_vals), min(y_vals), max(y_vals)]


def mbr_center(mbr):
    '''
    Υπολογίζει το κέντρο ενός mbr
    (x_center, y_center) = (x_min+x_max)/2, (y_min+y_max)/2

    Helper που χρησιμοποιείται στην ακόλουθη συνάρτηση build_mbrs
    '''
    x_center = (mbr[0] + mbr[1]) / 2
    y_center = (mbr[2] + mbr[3]) / 2
    
    return x_center, y_center


def build_mbrs(coords, offsets):
    '''
    Δημιουργείται κάθε πολύγωνο, υπολογίζονται το mbr και το κέντρο του
    και υπολογίζεται z-order curve τιμή βάσει της συνάρτησης που δίνεται
    από τη βιβλιοθήκη pymorton.
    Επιστρέφεται μία λίστα (objects) με λεξικά που περιέχουν το id, το mbr 
    και η τιμή z order curve για κάθε πολύγωνο
    '''
    objects = []
    for row in offsets:
        obj_id, start, end = row[0], row[1], row[2]
        
        # Συντεταγμένες του πολυγώνου
        poly_coords = coords[start:end]
        # MBR του πολυγώνου
        mbr = compute_mbr(poly_coords)
        # κέντρο του MBR
        center = mbr_center(mbr)
        #  Z-order για το κέντρο του MBR
        z_val = interleave_latlng(center[1], center[0])
        
        # αποθήκευση δεδομένων στη ΄λίστα
        objects.append({"id": obj_id, "mbr": mbr, "z": z_val})

    # επιστροφή ταξινόμημένης λίστας βάση Z-order
    return sorted(objects, key=lambda x: x["z"]) 


def delete_z(objects):
    '''
    Διαγραφή του z order αφού έχει γίνει ήδη η ταξινόμηση
    '''
    for obj in objects:
        del(obj['z'])
        
    return objects


def group_entries(entries):
    '''
    Ομαδικοποίηση της λίστας entries (αρχικά entries==objects) σε υποομάδες
    με μέγιστο αριθμό ανά υποομάδα 20, και ελάχιστο 8. 

    Helper που χρησιμοποιείται στην ακόλουθη συνάρτηση build_nodes
    '''
    
    max_entries = 20
    min_entries = 8
    length = len(entries) 
    
    if length < min_entries:
        print(f'Number of avalailable data ({length}) less that the minimum data allowed per node {min_entries}')
        return []

    # Αριθμός 'εικοσάδων' (ή ομάδες των max entries)
    iterations = length // max_entries
    # Περισσευούμενα δεδομένα
    remainder = length % max_entries
    
    # Δημιουργία αρχικής λίστας μόνο με τις λίστες των εικοσάδων
    groups = [entries[max_entries * i: max_entries * (i + 1)] for i in range(iterations)]
    
    # Σε περίπτωση που η τελευταία ομάδα έχει λιγότερο από min entries
    if 0 < remainder < min_entries:
        # Αφα΄ίρεση της τελευταίας ομάδας που μπήκε
        groups.pop()
        # Αριθμός των δεδομένων που απομένουν να εισαχθούν
        last_batch = max_entries + remainder
        # start index του entries που αρχίζουν τα δεδομένα που θα εισαχθούν 
        start_index = length - last_batch
        # mid index ώστε να απομένουν 8 δεδομένα στο τελευταίο node
        mid_index = length - 8
        # Προσθήκη των δύο τελευταίων nodes 
        groups.append(entries[start_index:mid_index])
        groups.append(entries[mid_index:length])

    # Αν απομένουν δεδομένα που είναι παραπάνω από MIN ENTRIES 
    elif remainder != 0:
        # αρκετά δεδομένα για επιτρεπόμενο node
        groups.append(entries[iterations * max_entries: length])
        
    return groups

def compute_union_mbr(mbr_list):
    '''
    Παίρνει μία λίστα με mbrs (min_entries <= len(mbr_list) <= max_entries) 
    και υπολογίζει τα min(xmins), max(xmaxs), min(ymins), max(ymaxs) ώστε να
    περιλαμβάνονται όλα τα δεδομένα

    Helper που χρησιμοποιείται στην ακόλουθη συνάρτηση build_nodes
    Χρησιμοποιείται και στην τελική build_rtree, για τον υπολογισμό mbr του root
    '''
    xmins = [mbr[0] for mbr in mbr_list]
    xmaxs = [mbr[1] for mbr in mbr_list]
    ymins = [mbr[2] for mbr in mbr_list]
    ymaxs = [mbr[3] for mbr in mbr_list]
    return [min(xmins), max(xmaxs), min(ymins), max(ymaxs)]


def build_nodes(entries, node_type):
    '''
    Δημιουργεί μία λίστα με nodes, όπου κάθε node είναι ένα λεξικό με
    type (root/node/leaf), με τα children του, και με το mbr 
    που περιλαμβάνει όλα τα children του 

    Helper που χρησιμοποιείται στην ακόλουθη συνάρτηση build_rtree
    '''
    # Δημιουργία των nodes
    grouped = group_entries(entries)
    nodes = []
    for group in grouped:
        # εξαγωγή όλων των mbrs του group
        mbrs = [entry['mbr'] for entry in group]

        # υπολογισμός του μεγαλύτερου mbr 
        # που περιλαμβάνει όλα τα μικρότερα mbr του group
        node_mbr = compute_union_mbr(mbrs)
        # Δημιουργία του κόμβου
        node = {
            'type': node_type,
            'children': group,
            'mbr': node_mbr,
        }
        nodes.append(node)
        
    return nodes


def assign_node_ids(nodes, count):
    '''
    Αναθέτει unique id σε κάθε κόμβο 
    κατά τη δημιουργία του δέντρου

    Helper που χρησιμοποιείται στην ακόλουθη συνάρτηση build_rtree
    '''
    for node in nodes:
        node['id'] = count
        count += 1
        
    return count

    
def build_rtree(entries, count=0):
    '''
    Δημιουργία αναδρομικά το Rtree, αρχίζοντας από τα leaves
    και ομαδικοποιεί σε parent nodes τα nodes του current levels
    μέχρι να τα node του επιπέδου που απομένουν να είναι στο εύρος
    min_entries < n_nodes <= max_entries που ομαδικοποιούνται στο root node
    '''
    min_entries = 2
    max_entries = 20

    # Αρχικό επίπεδο, δημιουργία κόμβων των leaves
    current_level = build_nodes(entries, node_type='leaf')
    # Ανάθεση unique ids για τα leaves, αρχίζοντας από count = 0
    count = assign_node_ids(current_level, count)
    
    while True: # Σπάει όταν φτάσει στο return
        # Φτάνει στο return όταν ο αριθμός των nodes ε΄ίναι min_entries < n_nodes <= max_entries
        # oπ΄ότε ομαδικοποιούνται κάτω από τον root node
        if len(current_level) <= max_entries:
            
            if len(current_level) < min_entries:
                raise ValueError("Not enough entries for root.")
                
            root_node = {
                'type': 'root',
                'children': current_level,
                'mbr': compute_union_mbr([n['mbr'] for n in current_level]),
                'id': count
            }
            return root_node

        # Χτίζουμε το επόμενο επίπεδο μέχρι να μπεί στην προηγούμενη συνθήκη if
        next_level = build_nodes(current_level, node_type='node')
        count = assign_node_ids(next_level, count)
        current_level = next_level

    
def tree_stats(root):
    '''
    Δημιουργεί ένα λεξικό (level_counts) με keys τα level του δέντρου
    και keys των αριθμό των κόμβων σε αυτό το επίπεδο
    Στο τέλος τυπώνονται τα περιεχόμενα του λεξικού αυτού
    '''
    # αρχικοποίηση ουράς με tuples δομής (node, level)
    queue = deque([(root, 0)])
    level_counts = {}

    # Όσο αυτή η λίστα δεν είναι άδεια
    while queue:
        # εξαγωγή πρώτου element της ουράς
        node, level = queue.popleft() 

        # Καταγραφή του node στο επίπεδο που αντιστοιχεί
        if level not in level_counts:
            level_counts[level] = 0
        level_counts[level] += 1

        # Αν έχει παιδιά, προσθέτουμε όλα τα παιδιά στην ουρά
        # τα οπο΄ία θα καταγραφούν με τη σειρά τους
        if 'children' in node:
            for child in node['children']:
                if 'children' in child:
                    queue.append((child, level + 1))

    # Καθώς η μέτρηση ΄έχει γίνει από πάνω (root) προς τα κάτω (children)
    # Γίνεται loop σε reversed λίστα ώστε να τυπωθούν από τα childern προς το root
    # Και enumerate αυτών για το level
    for i, level in enumerate(reversed(level_counts)):
        print(f"{level_counts[level]} nodes at level {i}")


def write_rtree_to_file_dfs_sorted(root, filename='Rtree.txt'):
    '''
    Αρχίζοντας από το root, καταγράφεται κάθε κόμβος σε μία λίστα (entries)
    Μετά την ταξινόμηση της λίστας βάση του id του,
    αποθηκεύεται σε ένα αρχείο `filename`
    '''
    
    # Λίστα για αποθήκευση των δεδομένων του R-tree
    entries = []

    def dfs_traverse_and_collect(node):
        # Ελέγχουμε αν ο κόμβος δεν είναι δεδομένο (δεν διαθέτει type)
        if 'type' in node:
            # αν είναι leaf 
            isnonleaf = 0
            if node['type'] != 'leaf':
                # αν είναι root ή node
                isnonleaf = 1
                
            # Προσθήκη των δεδομένων του κόμβου
            children_data = [[child['id'], child['mbr']] for child in node['children']]
            entries.append([isnonleaf, node['id'], children_data])
            # Η λίστα δεν χρειάζεται να επιστραφεί κα΄θώς είναι τοπική μεταβλητή
            # της συνάρτησης 'write_rtree_to_file_dfs_sorted'
        
        # Εάν έχει παιδιά, καλούμε αναδρομικά τη συνάρτηση
        if 'children' in node:
            for child in node['children']:
                dfs_traverse_and_collect(child)

    # Ξεκινάμε την αναδρομή από τη ρίζα του δέντρου
    dfs_traverse_and_collect(root)

    # Ταξινομούμε τα δεδομένα με βάση το id του κόμβου
    entries.sort(key=lambda x: x[1])

    # Άνοιγμα του αρχείου για εγγραφή και αποθήκευση των ταξινομημένων δεδομένων
    with open(filename, 'w') as file:
        for entry in entries:
            # Αποθηκεύουμε τις πληροφορίες του κόμβου με τα δεδομένα του
            file.write(f"[{entry[0]}, {entry[1]}, {entry[2]}]\n")