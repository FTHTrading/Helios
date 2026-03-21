/**
 * ☀ Helios OS — Static Fallback Layer
 * ═══════════════════════════════════════════════════════════════
 * When pages are served from static hosting (Netlify) where no
 * Flask backend exists, this script intercepts /api/ and /health
 * fetch calls and returns realistic demo data so every page
 * renders with content instead of blank "Loading…" states.
 *
 * On the live Flask server the real APIs respond with JSON and
 * this layer never activates — it only kicks in when the
 * response is NOT valid JSON (i.e. a 404 HTML page or network error).
 * ═══════════════════════════════════════════════════════════════
 */
(function () {
    'use strict';

    window.__HELIOS_STATIC_FALLBACK_ACTIVE__ = true;
    try { console.log('🔥 static-fallback ACTIVE'); } catch (_) {}

    window.onerror = function (msg, src, line, col, err) {
        try {
            console.error('🔥 HELIOS JS ERROR:', msg, src, line + ':' + col, err);
        } catch (_) {}
        return false;
    };

    window.onunhandledrejection = function (evt) {
        try {
            console.error('🔥 HELIOS UNHANDLED REJECTION:', evt && evt.reason ? evt.reason : evt);
        } catch (_) {}
    };

    // Ensure a helios_id exists so pages don't redirect to /join
    if (!localStorage.getItem('helios_id')) {
        localStorage.setItem('helios_id', 'founder.helios');
    }

    const _fetch = window.fetch;

    window.fetch = async function (url, opts) {
        const u = typeof url === 'string' ? url : url.toString();

        // Only intercept protocol API and health calls
        if (!u.startsWith('/api/') && u !== '/health') {
            return _fetch.apply(this, arguments);
        }

        try {
            const res = await _fetch.apply(this, arguments);
            const ct = res.headers.get('content-type') || '';
            if (ct.includes('application/json')) return res;   // Real backend
            throw new Error('non-json');
        } catch (_) {
            // Static hosting — return demo data
            return demoResponse(u, opts);
        }
    };

    // ─── Demo Data Factory ───────────────────────────────────────

    function demoResponse(url, opts) {
        const body = route(url, opts);
        return new Response(JSON.stringify(body), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
        });
    }

    function route(url, opts) {
        // ── Health ──
        if (url === '/health')
            return { status: 'ok', version: '3.0.0', protocol: 'Helios Neural Field' };

        // ── Wallet ──
        if (url.match(/\/api\/wallet\/balance\//))
            return { success: true, data: { display: '247.50 HLS', balance: 247.5, earned: 247.5, sent: 12.0, received: 35.0 } };

        if (url.match(/\/api\/wallet\/history\//))
            return { success: true, data: [
                { type: 'received', display: 'Energy propagation from alpha.helios — hop 1', date: '2026-02-09T14:30:00Z' },
                { type: 'received', display: 'Energy propagation from sierra.helios — hop 2', date: '2026-02-08T09:15:00Z' },
                { type: 'earned', display: 'Settlement reward — 4.25 HLS', date: '2026-02-07T18:00:00Z' },
                { type: 'sent', display: 'Sent 10.00 HLS to nova.helios', date: '2026-02-06T11:20:00Z' },
                { type: 'received', display: 'Energy propagation from echo.helios — hop 1', date: '2026-02-05T16:45:00Z' },
                { type: 'earned', display: 'Settlement reward — 3.80 HLS', date: '2026-02-04T18:00:00Z' },
                { type: 'received', display: 'Certificate redemption — 50.00 HE', date: '2026-02-03T10:00:00Z' }
            ]};

        if (url === '/api/wallet/send')
            return { success: true, data: { message: 'Demo mode — live transfers require the running protocol.' } };

        if (url.match(/\/api\/wallet\/receive-qr\//))
            return { success: true, data: { helios_id: 'founder.helios', qr_code: 'data:image/png;base64,DEMO' } };

        if (url === '/api/wallet/xaman/payload') {
            const request = parseBody(opts);
            return {
                success: true,
                data: {
                    created: false,
                    simulation: true,
                    action: request.action || 'signin',
                    txjson: buildXamanTx(request),
                    message: 'Add Xaman credentials to enable wallet signing.',
                    payload_uuid: 'demo-xaman-payload'
                }
            };
        }

        if (url.match(/\/api\/wallet\/xaman\/payload\//))
            return { success: true, data: { resolved: false, signed: false, expired: false, simulation: true, payload_uuid: 'demo-xaman-payload' } };

        // ── Identity ──
        if (url.match(/\/api\/identity\/verify\//))
            return { success: true, data: { exists: true, display_name: 'founder', helios_id: 'founder.helios', member_since: '2025-01-15T00:00:00Z', phone_verified: true } };

        if (url === '/api/identity/create')
            return { success: true, data: { helios_id: 'demo.helios', _key: 'demo_key_static', recovery_phrase: ['solar','field','energy','protocol','link','treasury','metal','reserve','vault','certificate','helios','network'], qr_code: '' } };

        // ── Network ──
        if (url.match(/\/api\/network\/stats\//))
            return { success: true, data: { total_network: 23, direct_connections: 4, health: 'healthy', your_activity: 72 } };

        if (url.match(/\/api\/network\/graph\//))
            return { success: true, data: demoNetworkGraph() };

        // ── Rewards ──
        if (url.match(/\/api\/rewards\/total\//))
            return { success: true, data: { grand_total: 247.5, token: 'HLS' } };

        if (url === '/api/rewards/pool')
            return { success: true, data: { pool_balance: 1250.00, distributed_total: 4800.00 } };

        // ── Metrics ──
        if (url === '/api/metrics/all')
            return {
                reserve_ratio: { value: 4.2, status: 'healthy' },
                flow_efficiency: { value: 0.973, status: 'healthy' },
                churn_pressure: { value: 0.008, status: 'healthy' },
                energy_velocity: { value: 0.38, status: 'healthy' }
            };

        if (url === '/api/metrics/health')
            return { total_nodes: 147, active_nodes: 132, active_certificates: 28, total_energy_he: 8420.50, total_stored_he: 3150.00, total_vault_receipts: 6 };

        if (url === '/api/metrics/rrr')
            return { success: true, ratio: 4.2, status: 'healthy' };

        // ── Energy / Conservation ──
        if (url === '/api/energy/conservation')
            return { balanced: true, total_in: 14700.0, total_routed: 6615.0, total_stored: 3150.0, total_pooled: 4882.0, total_burned: 53.0, delta: 0.0 };

        if (url.match(/\/api\/energy\/balance\//))
            return { energy_balance_he: 185.25 };

        // ── Certificates / Covenant ──
        if (url === '/api/certificates/covenant')
            return { success: true, data: { status: 'healthy', ratio: '4.20', redemption_permitted: true, warning: false } };

        if (url.match(/\/api\/certificates\/portfolio\//))
            return { active_count: 3, active_energy_he: 150.0, active_value_usd: 1275.0, redeemed_count: 1, cancelled_count: 0, total_friction_paid: 0 };

        if (url.match(/\/api\/certificates\/list/))
            return { certificates: [
                { certificate_id: 'HC-a7f3e2b1c9d845e6abcdef1234567890', state: 'active', energy_amount_he: '75.00', energy_value_usd: '637.50', mint_rate: '8.5000' },
                { certificate_id: 'HC-b8c4d3e2f0a956f7bcde01234567890a', state: 'active', energy_amount_he: '50.00', energy_value_usd: '425.00', mint_rate: '8.5000' },
                { certificate_id: 'HC-c9d5e4f301ba67a8cdef12345678901b', state: 'active', energy_amount_he: '25.00', energy_value_usd: '212.50', mint_rate: '8.5000' },
                { certificate_id: 'HC-d0e6f5a412cb78b9def0234567890abc', state: 'redeemed', energy_amount_he: '100.00', energy_value_usd: '850.00', mint_rate: '8.5000', redemption_type: 'gold', redemption_amount: '850.00' }
            ]};

        if (url === '/api/certificates/mint')
            return { success: true, certificate_id: 'HC-demo00000000000000000000000000', energy_amount_he: 10.0 };

        if (url.match(/\/api\/certificates\/redeem/))
            return { success: true, redemption_amount: '85.00' };

        if (url === '/api/certificates/cancel')
            return { success: true, friction_burned: '0.20' };

        // ── Burned ──
        if (url === '/api/certificates/burned')
            return { success: true, data: { total_burned: 53.0 } };

        // ── Infrastructure / Status ──
        if (url === '/api/infra/status')
            return { success: true, data: { status: 'hybrid', zone: { name: 'heliosdigital.xyz' }, services: { xrpl: 'simulated', ipfs: 'not_configured', cloudflare: 'active', apmex: 'manual', stripe: 'not_configured' } } };

        if (url === '/api/infra/readiness')
            return { success: true, data: { mode: 'hybrid', production_ready: false, recommended_chain: 'XRPL', recommended_certificate_standard: 'XLS-20', recommended_token_model: 'XRPL issued fungible token' } };

        if (url === '/api/funding/catalog')
            return { success: true, data: demoFundingCatalog() };

        if (url === '/api/voice/status')
            return { success: true, data: { status: 'active', tier: 'Professional', remaining: '287,400 chars', voice: 'Drew' } };

        if (url === '/api/funding/checkout') {
            const request = parseBody(opts);
            const catalog = demoFundingCatalog();
            const offer = (catalog.offers || []).find(item => item.code === request.offer_code) || catalog.featured_offer;
            return {
                success: true,
                data: {
                    status: 'not_configured',
                    offer,
                    member_id: request.member_id || 'founder.helios',
                    amount_total_usd: offer ? offer.amount_usd : 500,
                    message: 'Stripe is not configured in static mode.',
                }
            };
        }

        if (url === '/api/funding/webhook/stripe')
            return { success: true, data: { received: true, fulfilled: false, event_type: 'checkout.session.completed' } };

        if (url.match(/\/api\/funding\/events\//))
            return { success: true, data: { external_id: 'demo_event', provider: 'stripe', status: 'received', offer_code: 'protocol' } };
        if (url === '/api/sms/status')
            return { success: true, data: { status: 'active', from_number: '+1 (833) XXX-XXXX', balance: '24.50', currency: 'USD' } };

        // ── Treasury ──
        if (url === '/api/treasury/reserves')
            return {
                total_receipts: 6, anchored_count: 5,
                by_metal: {
                    Gold: { total_oz: 3.42, total_cost_usd: 10260.00, receipt_count: 5 },
                    Silver: { total_oz: 50.0, total_cost_usd: 1550.00, receipt_count: 1 }
                }
            };

        if (url === '/api/treasury/receipts')
            return { receipts: [
                { mvr_id: 'MVR-a1b2c3d4e5f67890abcdef1234567890', metal: 'Gold', form: 'Bar', weight_oz: '1.000', quantity: 1, total_oz: '1.000', total_cost_usd: '3200.00', custody_status: 'secured', is_anchored: true },
                { mvr_id: 'MVR-b2c3d4e5f67890abcdef1234567890a1', metal: 'Gold', form: 'Bar', weight_oz: '0.321', quantity: 3, total_oz: '0.964', total_cost_usd: '2890.00', custody_status: 'secured', is_anchored: true },
                { mvr_id: 'MVR-c3d4e5f67890abcdef1234567890a1b2', metal: 'Gold', form: 'Bar', weight_oz: '0.161', quantity: 5, total_oz: '0.804', total_cost_usd: '2410.00', custody_status: 'secured', is_anchored: true },
                { mvr_id: 'MVR-d4e5f67890abcdef1234567890a1b2c3', metal: 'Gold', form: 'Round', weight_oz: '0.100', quantity: 3, total_oz: '0.300', total_cost_usd: '960.00', custody_status: 'secured', is_anchored: true },
                { mvr_id: 'MVR-e5f67890abcdef1234567890a1b2c3d4', metal: 'Gold', form: 'Bar', weight_oz: '0.355', quantity: 1, total_oz: '0.355', total_cost_usd: '1065.00', custody_status: 'in_transit', is_anchored: false },
                { mvr_id: 'MVR-f67890abcdef1234567890a1b2c3d4e5', metal: 'Silver', form: 'Bar', weight_oz: '10.000', quantity: 5, total_oz: '50.000', total_cost_usd: '1550.00', custody_status: 'secured', is_anchored: true }
            ]};

        // ── Chat / Ask Helios ──
        if (url === '/api/chat/quick-answers')
            return { success: true, data: [
                { icon: '⬡', question: 'What is Helios?' },
                { icon: '⚡', question: 'How does energy propagation work?' },
                { icon: '🥇', question: 'What backs the treasury?' },
                { icon: '🔋', question: 'What are certificates?' },
                { icon: '⚖', question: 'Is the conservation law real?' },
                { icon: '🔒', question: 'How is supply fixed?' }
            ]};

        if (url === '/api/chat/ask')
            return { success: true, data: {
                answer: "Helios is a private network protocol where human connections inject energy and the system distributes it according to physics, not position.\n\nEvery node holds a maximum of 5 links. Energy radiates outward — strongest at direct connections, halving at each hop, up to 15 hops deep. The remainder absorbs into protocol pools.\n\nThe treasury is backed by physical metal purchased through APMEX. Every receipt is anchored on XRPL with SHA-256 proof. Certificates store energy and can be redeemed for gold or stablecoin at any time.\n\n$100 entry. Conservation law enforced. Verifiable by anyone.",
                follow_up: ['How does the reserve ratio work?', 'What happens when I cancel a certificate?', 'Tell me about the Power of 5']
            }};

        if (url === '/api/voice/speak')
            return { success: false, data: { audio: null, message: 'Voice available on live protocol.' } };

        // ── SMS Verification ──
        if (url === '/api/sms/verify/send')
            return { success: true, data: { sent: true, verification_id: 'demo_verify', phone_masked: '+1 (***) ***-**00' } };

        if (url === '/api/sms/verify/confirm')
            return { success: true, data: { verified: true } };

        // ── Token Info (footer links) ──
        if (url === '/api/token/info')
            return { token: 'HLS', total_supply: 100000000, decimals: 8, founder_lock_years: 3 };

        if (url === '/api/token/supply')
            return { total_supply: 100000000, circulating: 14700, locked: 20000000, minted: false };

        if (url === '/api/token/verify')
            return { valid: true, supply_correct: true, no_mint_function: true };

        if (url === '/api/token/founder-lock')
            return { locked: true, amount: 20000000, unlock_date: '2028-01-15', years_remaining: 1.93 };

        if (url.match(/\/api\/rewards\/protocol/))
            return { settlement_rules: 'hop_decay', max_hops: 15, decay: '1/2^hop' };

        // ── Field Status ──
        if (url === '/api/field/status')
            return { success: true, data: { total_nodes: 147, total_links: 312, active_links: 289, avg_link_strength: 0.72, field_health: 'stable' } };

        // ── Certificates Active ──
        if (url === '/api/certificates/active')
            return { success: true, data: { active_count: 28, total_energy_locked: 2100.0 } };

        // ── System Status (catch-all) ──
        if (url === '/api/status')
            return { success: true, status: 'operational', version: '3.0.0', protocol: 'Helios Neural Field', domain: 'heliosdigital.xyz' };

        // Fallback
        return { success: true, data: {} };
    }

    // ─── Demo Network Graph ──────────────────────────────────────
    // Creates a realistic-looking 23-node network with the viewer
    // at the center, 4 direct connections, and 2nd/3rd hop nodes.

    function demoNetworkGraph() {
        const nodes = [
            { id: 'founder.helios', name: 'founder', hops: 0, node_state: 'stable', link_count: 4, activity: 92, is_origin: true, energy_weight: 1.0 },
            // Hop 1 — direct links
            { id: 'alpha.helios', name: 'alpha', hops: 1, node_state: 'stable', link_count: 3, activity: 78, is_origin: false, energy_weight: 0.5 },
            { id: 'sierra.helios', name: 'sierra', hops: 1, node_state: 'stable', link_count: 5, activity: 85, is_origin: false, energy_weight: 0.5 },
            { id: 'echo.helios', name: 'echo', hops: 1, node_state: 'propagating', link_count: 2, activity: 64, is_origin: false, energy_weight: 0.5 },
            { id: 'nova.helios', name: 'nova', hops: 1, node_state: 'stable', link_count: 4, activity: 71, is_origin: false, energy_weight: 0.5 },
            // Hop 2
            { id: 'vega.helios', name: 'vega', hops: 2, node_state: 'connected', link_count: 2, activity: 55, is_origin: false, energy_weight: 0.25 },
            { id: 'orion.helios', name: 'orion', hops: 2, node_state: 'stable', link_count: 3, activity: 68, is_origin: false, energy_weight: 0.25 },
            { id: 'luna.helios', name: 'luna', hops: 2, node_state: 'propagating', link_count: 4, activity: 74, is_origin: false, energy_weight: 0.25 },
            { id: 'sol.helios', name: 'sol', hops: 2, node_state: 'connected', link_count: 1, activity: 42, is_origin: false, energy_weight: 0.25 },
            { id: 'zephyr.helios', name: 'zephyr', hops: 2, node_state: 'stable', link_count: 3, activity: 60, is_origin: false, energy_weight: 0.25 },
            { id: 'atlas.helios', name: 'atlas', hops: 2, node_state: 'connected', link_count: 2, activity: 51, is_origin: false, energy_weight: 0.25 },
            { id: 'iris.helios', name: 'iris', hops: 2, node_state: 'stable', link_count: 3, activity: 63, is_origin: false, energy_weight: 0.25 },
            { id: 'bolt.helios', name: 'bolt', hops: 2, node_state: 'acknowledged', link_count: 1, activity: 30, is_origin: false, energy_weight: 0.25 },
            // Hop 3
            { id: 'drift.helios', name: 'drift', hops: 3, node_state: 'connected', link_count: 2, activity: 40, is_origin: false, energy_weight: 0.125 },
            { id: 'flux.helios', name: 'flux', hops: 3, node_state: 'acknowledged', link_count: 1, activity: 28, is_origin: false, energy_weight: 0.125 },
            { id: 'ember.helios', name: 'ember', hops: 3, node_state: 'stable', link_count: 3, activity: 55, is_origin: false, energy_weight: 0.125 },
            { id: 'wave.helios', name: 'wave', hops: 3, node_state: 'connected', link_count: 2, activity: 44, is_origin: false, energy_weight: 0.125 },
            { id: 'peak.helios', name: 'peak', hops: 3, node_state: 'propagating', link_count: 2, activity: 50, is_origin: false, energy_weight: 0.125 },
            { id: 'core.helios', name: 'core', hops: 3, node_state: 'instantiated', link_count: 1, activity: 15, is_origin: false, energy_weight: 0.125 },
            { id: 'spark.helios', name: 'spark', hops: 3, node_state: 'connected', link_count: 2, activity: 38, is_origin: false, energy_weight: 0.125 },
            { id: 'reef.helios', name: 'reef', hops: 3, node_state: 'stable', link_count: 3, activity: 52, is_origin: false, energy_weight: 0.125 },
            { id: 'glow.helios', name: 'glow', hops: 3, node_state: 'acknowledged', link_count: 1, activity: 22, is_origin: false, energy_weight: 0.125 },
            { id: 'tide.helios', name: 'tide', hops: 3, node_state: 'connected', link_count: 2, activity: 35, is_origin: false, energy_weight: 0.125 }
        ];

        const edges = [
            // Origin links
            { source: 'founder.helios', target: 'alpha.helios' },
            { source: 'founder.helios', target: 'sierra.helios' },
            { source: 'founder.helios', target: 'echo.helios' },
            { source: 'founder.helios', target: 'nova.helios' },
            // Hop 1 → 2
            { source: 'alpha.helios', target: 'vega.helios' },
            { source: 'alpha.helios', target: 'orion.helios' },
            { source: 'sierra.helios', target: 'luna.helios' },
            { source: 'sierra.helios', target: 'sol.helios' },
            { source: 'sierra.helios', target: 'zephyr.helios' },
            { source: 'echo.helios', target: 'atlas.helios' },
            { source: 'nova.helios', target: 'iris.helios' },
            { source: 'nova.helios', target: 'bolt.helios' },
            // Cross links (non-hierarchical — peers connect to peers)
            { source: 'orion.helios', target: 'luna.helios' },
            { source: 'zephyr.helios', target: 'iris.helios' },
            // Hop 2 → 3
            { source: 'vega.helios', target: 'drift.helios' },
            { source: 'orion.helios', target: 'flux.helios' },
            { source: 'luna.helios', target: 'ember.helios' },
            { source: 'luna.helios', target: 'wave.helios' },
            { source: 'zephyr.helios', target: 'peak.helios' },
            { source: 'atlas.helios', target: 'core.helios' },
            { source: 'iris.helios', target: 'spark.helios' },
            { source: 'iris.helios', target: 'reef.helios' },
            { source: 'bolt.helios', target: 'glow.helios' },
            { source: 'bolt.helios', target: 'tide.helios' },
            // Cross links at hop 3
            { source: 'ember.helios', target: 'reef.helios' },
            { source: 'drift.helios', target: 'spark.helios' }
        ];

        return { total_members: 23, total_connections: edges.length, nodes: nodes, edges: edges };
    }

    function parseBody(opts) {
        if (!opts || !opts.body) return {};
        if (typeof opts.body === 'string') {
            try { return JSON.parse(opts.body); } catch (_) { return {}; }
        }
        return opts.body || {};
    }

    function buildXamanTx(request) {
        if (request.action === 'trustline') {
            return {
                TransactionType: 'TrustSet',
                Account: request.account || 'rDemoAccount',
                LimitAmount: {
                    currency: 'HLS',
                    issuer: 'rHeliosIssuerDemo',
                    value: '1000000000'
                }
            };
        }
        return { TransactionType: 'SignIn' };
    }

    function demoFundingCatalog() {
        const offers = [
            { code: 'entry', name: 'Atomic Entry', amount_usd: 100, mode: 'payment', category: 'activation', token_amount: 2000, token_price_usd: 0.05 },
            { code: 'builder', name: 'Builder Activation', amount_usd: 250, mode: 'payment', category: 'activation', token_amount: 5000, token_price_usd: 0.05 },
            { code: 'protocol', name: 'Protocol Contract', amount_usd: 500, mode: 'payment', category: 'activation', token_amount: 10000, token_price_usd: 0.05, featured: true },
            { code: 'accelerator', name: 'Accelerator Activation', amount_usd: 1000, mode: 'payment', category: 'activation', token_amount: 20000, token_price_usd: 0.05 },
            { code: 'architect', name: 'Protocol Architect Activation', amount_usd: 5000, mode: 'payment', category: 'activation', token_amount: 100000, token_price_usd: 0.05 },
            { code: 'plus', name: 'Plus Membership', amount_usd: 20, mode: 'subscription', category: 'subscription' },
            { code: 'pro', name: 'Pro Membership', amount_usd: 99, mode: 'subscription', category: 'subscription' },
            { code: 'operator', name: 'Operator Membership', amount_usd: 499, mode: 'subscription', category: 'subscription' }
        ];
        return {
            recommended_stack: { chain: 'XRPL', wallet: 'Xaman / XUMM', payments: 'Stripe', evidence: 'Pinata + IPFS' },
            featured_offer: offers[2],
            offers,
            activation_tiers: offers.filter(item => item.category === 'activation'),
            best_funding_mix: ['Atomic entry conversions', 'Recurring Plus/Pro/Operator subscriptions', 'Annual operator/vendor/host credentials', 'Paid spaces and events after launch']
        };
    }
})();
