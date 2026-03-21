"""
Founding Network Bootstrap — Direct DB insertion for founding links.
Bypasses cooldown because these are pre-existing paid members 
being loaded into the system retroactively.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timezone, timedelta
from app import create_app
from models.member import Member
from models.link import Link
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

# Link pairs — building a connected mesh
# Chain links connect everyone in sequence
# Cross links strengthen the topology
link_pairs = [
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
    # Cross links — strengthen the mesh (respecting max 5 per node)
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
    
    # First, clean up any links from the earlier partial attempt
    existing_links = db.query(Link).all()
    if existing_links:
        print(f"\nClearing {len(existing_links)} existing links from partial attempt...")
        for b in existing_links:
            db.delete(b)
        # Reset all founder link counts
        for hid in founders:
            m = db.query(Member).filter_by(helios_id=hid).first()
            if m:
                m.link_count = 0
                m.node_state = "instantiated"
        db.commit()
        print("  Cleared.")
    
    # Backdate by 48 hours so cooldown doesn't apply
    base_time = datetime.now(timezone.utc) - timedelta(hours=48)
    
    formed = 0
    skipped = 0
    link_counts = {hid: 0 for hid in founders}
    
    print("\nForming links:\n")
    
    for idx, (i, j) in enumerate(link_pairs):
        a_id = founders[i]
        b_id = founders[j]
        
        # Respect max 5 links per node
        if link_counts[a_id] >= 5:
            print(f"  FULL    {a_id:<24} (5/5, skipping)")
            skipped += 1
            continue
        if link_counts[b_id] >= 5:
            print(f"  FULL    {b_id:<24} (5/5, skipping)")
            skipped += 1
            continue
        
        node_a, node_b = Link.ordered_pair(a_id, b_id)
        
        # Check no duplicate
        existing = db.query(Link).filter_by(node_a=node_a, node_b=node_b).first()
        if existing:
            print(f"  EXISTS  {a_id:<24} ↔ {b_id}")
            skipped += 1
            continue
        
        # Stagger timestamps so cooldown logic is satisfied
        link_time = base_time + timedelta(minutes=idx * 5)
        
        link = Link(
            node_a=node_a,
            node_b=node_b,
            state=HeliosConfig.LINK_STATE_ACTIVE,
            initiated_by=a_id,
            created_at=link_time,
            activated_at=link_time,
        )
        db.add(link)
        link_counts[a_id] += 1
        link_counts[b_id] += 1
        formed += 1
        print(f"  LINKED  {a_id:<24} ↔ {b_id:<24} [{link_counts[a_id]}/{link_counts[b_id]}]")
    
    # Update member records
    print("\nUpdating member link counts and node states:\n")
    for hid in founders:
        m = db.query(Member).filter_by(helios_id=hid).first()
        if m:
            m.link_count = link_counts[hid]
            m.update_node_state()
            print(f"  {hid:<28} links={m.link_count}  state={m.node_state}")
    
    db.commit()
    
    print(f"\nLinks formed: {formed}")
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
    print(f"  Total links: {formed}")
    
    db.close()
