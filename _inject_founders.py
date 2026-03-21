"""Register founding members — energy injection."""
import requests

BASE = 'http://localhost:5050'

founders = [
    'elliot-a.helios',
    'aaron-w.helios',
    'ryan-a.helios',
    'veunca-j.helios',
    'nicholas-w.helios',
    'paul-w.helios',
    'eddie-m.helios',
    'dan-morgan.helios',
    'neandria-p.helios',
    'joseph-d.helios',
    'brian-rawlston.helios',
    'blyss-w.helios',
    'nakia-r.helios',
]

print("ENERGY INJECTION - $100 ATOMIC ENTRY PER FOUNDER")
print("=" * 60)

for hid in founders:
    r = requests.post(f'{BASE}/api/energy/inject', json={'member_id': hid})
    d = r.json()
    if r.status_code == 201:
        alloc = d['data']['allocation']
        p = alloc['propagation']
        l = alloc['liquidity']
        t = alloc['treasury_surplus']
        i = alloc['infrastructure']
        b = alloc['buffer']
        print(f"  INJECTED  {hid:<28} prop={p} liq={l} tres={t} infra={i} buf={b}")
    else:
        print(f"  FAILED    {hid}: {d}")

r = requests.get(f'{BASE}/api/energy/conservation')
data = r.json()["data"]
print(f"\nEnergy conservation: {data}")
print("Total injected: 13 x $100 = $1,300")
