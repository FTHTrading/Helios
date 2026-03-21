"""Form founding bonds — building the initial Helios network topology."""
import requests

BASE = 'http://localhost:5050'

# Bond strategy: Create a connected founding network.
# Each member bonds with their neighbors to form a chain,
# then cross-bonds to strengthen the mesh.
# Max 5 bonds per node, 24h cooldown between NEW bonds per pair.
# Since these are all new, we can form them all now.

founders = [
    'elliot-a.helios',      # 0
    'aaron-w.helios',       # 1
    'ryan-a.helios',        # 2
    'veunca-j.helios',      # 3
    'nicholas-w.helios',    # 4
    'paul-w.helios',        # 5
    'eddie-m.helios',       # 6
    'dan-morgan.helios',    # 7
    'neandria-p.helios',    # 8
    'joseph-d.helios',      # 9
    'brian-rawlston.helios', # 10
    'blyss-w.helios',       # 11
    'nakia-r.helios',       # 12
]

# Bond pairs — building a connected mesh
# Chain bonds (each member to next): 12 bonds
# Cross bonds to strengthen topology: select extras
bonds = [
    # Chain — connects everyone in sequence
    (0, 1),   # elliot ↔ aaron
    (1, 2),   # aaron ↔ ryan
    (2, 3),   # ryan ↔ veunca
    (3, 4),   # veunca ↔ nicholas
    (4, 5),   # nicholas ↔ paul
    (5, 6),   # paul ↔ eddie
    (6, 7),   # eddie ↔ dan
    (7, 8),   # dan ↔ neandria
    (8, 9),   # neandria ↔ joseph
    (9, 10),  # joseph ↔ brian
    (10, 11), # brian ↔ blyss
    (11, 12), # blyss ↔ nakia
    # Cross bonds — strengthen the mesh
    (0, 3),   # elliot ↔ veunca
    (0, 7),   # elliot ↔ dan
    (1, 5),   # aaron ↔ paul
    (2, 6),   # ryan ↔ eddie
    (3, 8),   # veunca ↔ neandria
    (4, 9),   # nicholas ↔ joseph
    (5, 10),  # paul ↔ brian
    (6, 11),  # eddie ↔ blyss
    (7, 12),  # dan ↔ nakia
    (1, 9),   # aaron ↔ joseph
    (2, 10),  # ryan ↔ brian
    (4, 12),  # nicholas ↔ nakia
    (0, 12),  # elliot ↔ nakia (closing the ring)
]

print("FOUNDING BOND FORMATION")
print("=" * 60)

formed = 0
failed = 0
saturated = 0

for i, j in bonds:
    a = founders[i]
    b = founders[j]
    r = requests.post(f'{BASE}/api/field/bond', json={
        'initiator_id': a,
        'peer_id': b,
    })
    d = r.json()
    if r.status_code == 201:
        istate = d['data'].get('initiator_state', '?')
        pstate = d['data'].get('peer_state', '?')
        print(f"  BONDED    {a:<24} ↔ {b:<24} [{istate}/{pstate}]")
        formed += 1
    elif 'saturated' in str(d.get('error', '')).lower() or 'maximum' in str(d.get('error', '')).lower():
        print(f"  FULL      {a:<24} ↔ {b:<24} (max 5 bonds reached)")
        saturated += 1
    else:
        print(f"  SKIP      {a:<24} ↔ {b:<24} → {d.get('error', d)}")
        failed += 1

print(f"\nBonds formed: {formed}")
print(f"Saturated (max 5): {saturated}")
print(f"Other skips: {failed}")

# Check node states
print("\n" + "=" * 60)
print("FOUNDING MEMBER STATUS")
print("=" * 60)
for hid in founders:
    r = requests.get(f'{BASE}/api/field/stats/{hid}')
    d = r.json()['data']
    bc = d.get('bond_count', 0)
    ns = d.get('node_state', '?')
    print(f"  {hid:<28} bonds={bc}  state={ns}")
