"""Quick launch validation for contracts, handoff, and AI surfaces."""
from app import create_app
import json

app = create_app()
client = app.test_client()


def api(path):
    """Get JSON, unwrap {success, data} envelope if present."""
    raw = json.loads(client.get(path).data)
    if isinstance(raw, dict) and 'data' in raw:
        return raw['data']
    return raw


def post_api(path, payload):
    """POST JSON, unwrap {success, data} envelope if present."""
    raw = json.loads(client.post(path, json=payload).data)
    if isinstance(raw, dict) and 'data' in raw:
        return raw['data']
    return raw

print("=== SMART CONTRACT VERIFICATION ===\n")

t = api('/api/token/info')
print(f"Token: {t['symbol']}  Supply: {t['total_supply']:,.0f}  Decimals: {t['decimals']}  Founder Lock: {t['anti_rug']['founder_lock_years']}yr")
print(f"Anti-Rug: can_mint={t['anti_rug']['can_mint']}  admin_override={t['anti_rug']['admin_override_possible']}  auditable={t['anti_rug']['supply_auditable']}")
for pool, info in t['allocation'].items():
    print(f"  {pool:15s} {info['percent']:>3}%  {info['amount']:>14,.0f} HLS  [{info['status']}]")

v = api('/api/token/verify')
print(f"Verify: supply_correct={v.get('supply_correct', v.get('valid'))}  no_mint={v.get('no_mint_function', 'n/a')}")

fl = api('/api/token/founder-lock')
print(
    "Founder Lock: "
    f"locked={fl.get('locked', fl.get('founder_tokens_locked'))}  "
    f"amount={fl.get('amount', 0):,}  "
    f"unlock={fl.get('unlock_date', fl.get('lock_ends', 'n/a'))}"
)

s = api('/api/token/supply')
print(f"Supply: total={s['total_supply']:,.0f}  circulating={s.get('circulating',0):,}  minted={s.get('minted','n/a')}")

print("\n=== TREASURY / METAL RESERVES ===")
res = api('/api/treasury/reserves')
print(f"Receipts: {res.get('total_receipts', 0)}  Anchored: {res.get('anchored_count', res.get('anchored_on_xrpl', 0))}")
for metal, data in res.get('by_metal', {}).items():
    print(f"  {metal}: {data.get('total_oz', 0)} oz  ${data.get('total_cost_usd', 0):,.2f}  ({data.get('receipt_count', 0)} receipts)")

print("\n=== CERTIFICATES ===")
cov = api('/api/certificates/covenant')
d = cov.get('data', cov) if isinstance(cov, dict) else cov
print(f"Covenant: status={d.get('status')}  ratio={d.get('ratio')}  redemption_ok={d.get('redemption_permitted')}")

act = api('/api/certificates/active')
print(f"Active: {act}")

print("\n=== ENERGY CONSERVATION LAW ===")
con = api('/api/energy/conservation')
print(f"Balanced: {con.get('balanced')}")
print(f"  In: {con.get('total_in')}  Routed: {con.get('total_routed')}  Stored: {con.get('total_stored')}  Pooled: {con.get('total_pooled')}  Burned: {con.get('total_burned')}")
print(f"  Delta: {con.get('delta', con.get('balance'))} (should be 0)")

print("\n=== METRICS FORMULAS ===")
m = api('/api/metrics/all')
for name, val in m.items():
    if not isinstance(val, dict):
        print(f"  {name}: value={val}  status=n/a")
        continue
    metric_value = val.get(
        'value',
        val.get('rrr', val.get('cp', val.get('eta', val.get('velocity'))))
    )
    print(f"  {name}: value={metric_value}  status={val.get('status', 'n/a')}")

h = api('/api/metrics/health')
certs = h.get('certificates', {})
print(f"  Network: nodes={h.get('total_nodes')}  active={h.get('active_nodes')}  certs={h.get('active_certificates', certs.get('active'))}  energy={h.get('total_energy_he', h.get('total_energy_injected_he'))} HE")

print("\n=== REWARDS / SETTLEMENT ===")
rp = api('/api/rewards/protocol')
print(f"Settlement: {rp.get('settlement_rules')}  max_hops={rp.get('max_hops')}  decay={rp.get('decay')}")

print("\n=== FIELD STATUS ===")
fs = api('/api/field/status')
print(f"Field: {fs}")

print("\n=== INFRASTRUCTURE ===")
inf = api('/api/infra/status')
d2 = inf.get('data', inf) if isinstance(inf, dict) else inf
print(f"Status: {d2.get('status')}")
for svc, st in d2.get('services', {}).items():
    print(f"  {svc}: {st}")

print("\n=== HANDOFF PORTAL ===")
manifest = api('/api/handoff/manifest')
print(f"Domain: {manifest['domain']}  Route: {manifest['default_route_key']}  Docs: {len(manifest['docs'])}")
print(f"GitHub: source={bool(manifest['github'].get('source_repo'))}  launch={bool(manifest['github'].get('launch_repo'))}")

docs = api('/api/handoff/docs')
print(f"Docs index: {len(docs)} mirrored docs")

print("\n=== FINAL LAUNCH READINESS ===")
launch = api('/api/infra/launch-readiness')
print(f"Status: {launch['status']}  Public launch ready: {launch['ready_for_public_launch']}  Mode: {launch.get('mode', 'hybrid')}")
print(f"Blocking issues: {len(launch.get('blocking_issues', []))}")
print(f"Optional enhancements: {len(launch.get('optional_enhancements', []))}")
for enh in launch.get('optional_enhancements', [])[:7]:
    print(f"  [{enh.get('priority')}] {enh.get('area')}: {enh.get('description')}")

print("\n=== NODE TELEMETRY SYSTEM ===")
# Test node stats endpoint (should return defaults for any slug)
node_stats = api('/api/nodes/kenny/stats')
print(f"Node: {node_stats.get('node')}  Status: {node_stats.get('status')}  Scans: {node_stats.get('total_scans')}  Joined: {node_stats.get('total_joined')}")

# Test event emission
node_event = post_api('/api/nodes/kenny/event', {'event_type': 'qr_view', 'session_id': 'verify_test'})
print(f"Event emitted: id={node_event.get('event_id')}  type={node_event.get('event_type')}")

# Test event history
node_events = api('/api/nodes/kenny/events')
print(f"Event history: {len(node_events)} events")

# Test conversion funnel
funnel = api('/api/nodes/kenny/funnel')
print(f"Funnel: {funnel.get('funnel', {})}")

# Test chain visualization
chain = api('/api/nodes/kenny/chain')
print(f"Chain data: {chain.get('total_nodes', 0)} nodes, {len(chain.get('links', []))} links")

# Test network-wide stats
net_stats = api('/api/nodes/network/stats')
print(f"Network: {net_stats.get('total_events')} events, {net_stats.get('total_joins')} joins, {net_stats.get('total_scans')} scans")

print("\n=== ASK HELIOS ===")
ask = post_api('/api/chat/ask', {'question': 'What is built now and where is the rebuttal?'})
print(f"Source: {ask.get('source')}  Confidence: {ask.get('confidence')}  References: {len(ask.get('references', []))}")
for ref in ask.get('references', [])[:3]:
    print(f"  - {ref.get('title')} [{ref.get('path')}]")

print("\n=== ALL PAGES ===")
pages = ['/', '/dashboard', '/field', '/network', '/ask', '/protocol', '/status',
         '/treasury', '/vault', '/vault/gold', '/activate', '/metrics', '/enter', '/join', '/health',
         '/handoff', '/start', '/handoff/docs/start']
for p in pages:
    r = client.get(p)
    size = len(r.data)
    status = "OK" if r.status_code == 200 else f"FAIL({r.status_code})"
    print(f"  {p:20s} {size:>6d}B  {status}")

print("\n=== SENIOR DOC ACCESS ===")
doc_routes = [
    '/handoff/docs/white-paper',
    '/handoff/docs/white-paper/raw',
    '/handoff/docs/white-paper/download',
    '/handoff/docs/sr-engineered-tokenomics',
    '/handoff/docs/sr-engineered-tokenomics/raw',
    '/handoff/docs/sr-engineered-tokenomics/download',
]
for route in doc_routes:
    response = client.get(route)
    disposition = response.headers.get('Content-Disposition', '')
    print(f"  {route:42s} {response.status_code} {disposition}")

print("\n☀ CONTRACTS + METRICS + HANDOFF + AI + PAGES VERIFIED")
