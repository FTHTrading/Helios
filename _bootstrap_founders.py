"""
Founding Network Bootstrap — Direct DB insertion for founding bonds.
Bypasses cooldown because these are pre-existing paid members 
being loaded into the system retroactively.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timezone, timedelta
from app import create_app
from models.member import Member
from models.bond import Bond
from config import HeliosConfig

app = create_app()

founders = [
    'elliot-a.helios',       # 0
    'aaron-w.helios',        # 1
    'ryan-a.helios',         # 2
    'veunca-j.helios',       # 3
    'nicholas-w.helios',     # 4
    'paul-w.helios',         # 5
    'eddie-m.helios',        # 6
    'dan-morgan.helios',     # 7
    'neandria-p.helios',     # 8
    'joseph-d.helios',       # 9
    'brian-rawlston.helios',  # 10
    'blyss-w.helios',        # 11
    'nakia-r.helios',        # 12
]

# Bond pairs — building a connected mesh
# Chain bonds connect everyone in sequence
# Cross bonds strengthen the topology
bond_pairs = [
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
    # Cross bonds — strengthen the mesh (respecting max 5 per node)
    (0, 6),   # elliot ↔ eddie
    (0, 12),  # elliot ↔ nakia
    (1, 7),   # aaron ↔ dan
    (2, 8),   # ryan ↔ neandria
    (3, 9),   # veunca ↔ joseph
    (4, 10),  # nicholas ↔ brian
    (5, 11),  # paul ↔ blyss
    (6, 12),  # eddie ↔ nakia
    (1, 4),   # aaron ↔ nicholas
    (2, 5),   # ryan ↔ paul
    (7, 10),  # dan ↔ brian
    (8, 11),  # neandria ↔ blyss
    (3, 12),  # veunca ↔ nakia
    (9, 12),  # joseph ↔ nakia
]

with app.app_context():
    from flask import g
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(HeliosConfig.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("=" * 60)
    print("FOUNDING NETWORK BOOTSTRAP")
    print("=" * 60)
    
    # First, clean up any bonds from the earlier partial attempt
    existing_bonds = db.query(Bond).all()
    if existing_bonds:
        print(f"\nClearing {len(existing_bonds)} existing bonds from partial attempt...")
        for b in existing_bonds:
            db.delete(b)
        # Reset all founder bond counts
        for hid in founders:
            m = db.query(Member).filter_by(helios_id=hid).first()
            if m:
                m.bond_count = 0
                m.node_state = "instantiated"
        db.commit()
        print("  Cleared.")
    
    # Backdate by 48 hours so cooldown doesn't apply
    base_time = datetime.now(timezone.utc) - timedelta(hours=48)
    
    formed = 0
    skipped = 0
    bond_counts = {hid: 0 for hid in founders}
    
    print("\nForming bonds:\n")
    
    for idx, (i, j) in enumerate(bond_pairs):
        a_id = founders[i]
        b_id = founders[j]
        
        # Respect max 5 bonds per node
        if bond_counts[a_id] >= 5:
            print(f"  FULL    {a_id:<24} (5/5, skipping)")
            skipped += 1
            continue
        if bond_counts[b_id] >= 5:
            print(f"  FULL    {b_id:<24} (5/5, skipping)")
            skipped += 1
            continue
        
        node_a, node_b = Bond.ordered_pair(a_id, b_id)
        
        # Check no duplicate
        existing = db.query(Bond).filter_by(node_a=node_a, node_b=node_b).first()
        if existing:
            print(f"  EXISTS  {a_id:<24} ↔ {b_id}")
            skipped += 1
            continue
        
        # Stagger timestamps so cooldown logic is satisfied
        bond_time = base_time + timedelta(minutes=idx * 5)
        
        bond = Bond(
            node_a=node_a,
            node_b=node_b,
            state=HeliosConfig.BOND_STATE_ACTIVE,
            initiated_by=a_id,
            created_at=bond_time,
            activated_at=bond_time,
        )
        db.add(bond)
        bond_counts[a_id] += 1
        bond_counts[b_id] += 1
        formed += 1
        print(f"  BONDED  {a_id:<24} ↔ {b_id:<24} [{bond_counts[a_id]}/{bond_counts[b_id]}]")
    
    # Update member records
    print("\nUpdating member bond counts and node states:\n")
    for hid in founders:
        m = db.query(Member).filter_by(helios_id=hid).first()
        if m:
            m.bond_count = bond_counts[hid]
            m.update_node_state()
            print(f"  {hid:<28} bonds={m.bond_count}  state={m.node_state}")
    
    db.commit()
    
    print(f"\nBonds formed: {formed}")
    print(f"Skipped (full/duplicate): {skipped}")
    
    # Summary
    states = {}
    for hid in founders:
        m = db.query(Member).filter_by(helios_id=hid).first()
        if m:
            states[m.node_state] = states.get(m.node_state, 0) + 1
    
    print(f"\nNetwork topology:")
    for state, count in sorted(states.items()):
        print(f"  {state}: {count} nodes")
    print(f"  Total bonds: {formed}")
    
    db.close()
