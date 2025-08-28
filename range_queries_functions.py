# Name: Konstantinos Vardakas 
# AM: 522

import ast
from rtree_init_functions import compute_union_mbr

def load_tree(filename='Rtree.txt'):
    '''
    Διαβάζει το αρχείο που αποθηκεύτηκε στο τέλος του πρώτου μέρους 
    και αναδημιουργεί το rtree
    Αρχικά δημιουργεί το λεξικό nodes με key το node_id και values type, children και id
    Μετά συνδέει κάθε node με τα παιδιά του, προς αναδημιουργία του δέντρου
    '''
    nodes = {}
    
    # 1. Διαβάζονται όλα τα nodes από το αρχείο
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            # αποδομεί τη λίστα που δημιουργήθηκε στη τελευταία συνάρτηση του πρώτου μέρους
            isnonleaf, node_id, entries = ast.literal_eval(line)
            
            # Το root θα ξαναονομαστεί αργότερα ως node_type = 'root'
            node_type = 'leaf' if not isnonleaf else 'node' 
            nodes[node_id] = {
                'type': node_type,
                'children': entries.copy(), 
                'id': node_id,
            }

    if not nodes:
        return None

    # 2. Linking βάσει των child_id
    for node in nodes.values():
        # λίστα για τα child nodes του node
        new_children = []

        # Για κάθε child node (αρχικά αποτελείται από child id και mbr)
        for child in node['children']:
            child_id, mbr = child
            # Αν είναι node έχει και άλλα children nodes
            if node['type']=='node':
                child_node = nodes[child_id]
                new_children.append({
                    'type': child_node['type'],
                    'children': child_node['children'], # Δεν γίνεται deepcopy — κάθε κόμβος έχει μία κοινή αναφορά.
                                                        # Οποιαδήποτε αλλαγή στον κόμβο φαίνεται και στους γονείς του.
                    'mbr': mbr,
                    'id': child_node['id'],
                })
                
            else:
                # Είναι φύλλο, δεν εχει παιδια 
                new_children.append({
                    'id': child_id,
                    'mbr': mbr
                })
        node['children'] = new_children

    # 3. Ορίζουμε τον root node
    root_id = max(nodes.keys())
    root = nodes[root_id]
    root_mbrs = [child['mbr'] for child in root['children']]
    # Υπολογισμός του mbr του root καθώς δεν το αποθηκεύουμε
    root['mbr'] = compute_union_mbr(root_mbrs)
    root['type'] = 'root'

    return root

def mbrs_intersect(w, mbr):
    '''
    Ελέγχει αν το MBR τέμνει το παράθυρο ερώτησης W.
    Αν το max του ενός είναι μικρότερο από το min του άλλου σε κάθε άξονα
    αυτόματα δεν είναι δυνατό να τέμνονται
    '''
    return not (w[1] <= mbr[0] or w[0] >= mbr[1] or w[3] <= mbr[2] or w[2] >= mbr[3])


def range_query(rtree, w):
    """Επιστρέφει όλα τα IDs των φύλλων που τέμνονται με το παράθυρο W."""
    results = []
    
    def traverse(node):
        # Αν είναι leaf ελέγχεται κάθε δεδομένο και αν το mbr είναι μέσα
        # συνεπώς είναι και το πολύγωνο, οπότε προστίθεται το δεδομένο
        if node['type'] == 'leaf':
            for child in node['children']:
                if mbrs_intersect(w, child['mbr']):
                    results.append(child['id'])
        else:  # node['type'] == 'node'
            # Για κάθε child node, ελέγχεται αν τέμνονται τα παράθυτα w και mbr
            # και αν ναι, καλείται αναδρομικά η συνάρτηση μέχρι να φτάσει στα leaves
            for child in node['children']:
                if mbrs_intersect(w, child['mbr']):
                    traverse(child)
    
    traverse(rtree)
    return results