"""
☀ HELIOS — Neural Field Protocol
A private network where human connections inject energy
and the protocol distributes it according to physics, not position.

heliosdigital.xyz
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone
from flask import Flask, render_template, request, g, jsonify, abort, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from config import HeliosConfig
from core.build_manifest import get_build_manifest
from models.member import Base

# Validate config on startup — fails fast if protocol rules are broken
HeliosConfig.validate()

log = logging.getLogger('helios')


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(HeliosConfig)

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=[limit.strip() for limit in HeliosConfig.RATE_LIMIT_DEFAULT.split(';') if limit.strip()],
        storage_uri=HeliosConfig.RATE_LIMIT_STORAGE_URI,
    )

    if HeliosConfig.SENTRY_DSN:
        sentry_sdk.init(
            dsn=HeliosConfig.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment="development" if HeliosConfig.DEBUG else "production",
        )

    @app.context_processor
    def inject_build_id():
        manifest = get_build_manifest()
        return {
            "helios_build_id": manifest["build_id"],
            "helios_build_watermark": manifest["watermark"],
            "helios_build_fingerprint": manifest["fingerprint"],
            "helios_deployment_route": manifest["route"],
            "helios_build_owner": manifest["owner"],
            "helios_watermark_mode": manifest["mode"],
            "helios_watermark_enabled": manifest["watermark_enabled"],
            "helios_show_simple_watermark": manifest["show_simple_watermark"],
            "helios_show_visible_watermark": manifest["show_visible_watermark"],
            "helios_version": "3.0.0",
            "helios_year": datetime.now(timezone.utc).year,
        }

    # ─── Security Headers ─────────────────────────────────────────
    @app.after_request
    def security_headers(response):
        manifest = get_build_manifest()
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Build-Fingerprint'] = manifest['fingerprint']
        response.headers['X-Deployment-Route'] = manifest['route']
        if manifest['build_id']:
            response.headers['X-Build-Id'] = manifest['build_id']
        if manifest['watermark']:
            response.headers['X-Build-Watermark'] = manifest['watermark']
        if not HeliosConfig.DEBUG:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # ─── CORS (allow Netlify preview deploys) ─────────────────────
    @app.after_request
    def cors_headers(response):
        origin = request.headers.get('Origin', '')
        allowed = (
            origin.endswith('.netlify.app') or
            origin.endswith('.heliosdigital.xyz') or
            origin == 'https://heliosdigital.xyz' or
            origin.endswith('.xxxiii.io') or
            origin == 'https://xxxiii.io' or
            HeliosConfig.DEBUG
        )
        if allowed:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

    # ─── Request Logging ──────────────────────────────────────────
    @app.before_request
    def log_request():
        g._request_start = time.time()

    @app.after_request
    def log_response(response):
        duration = time.time() - getattr(g, '_request_start', time.time())
        if request.path.startswith('/static/'):
            return response  # Don't log static assets
        log.info('%s %s %s %.0fms',
                 request.method, request.path, response.status_code,
                 duration * 1000)
        return response

    # ─── Error Handlers ───────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
        return render_template('error.html', code=404,
                               message='This route does not exist in the Helios protocol.'), 404

    @app.errorhandler(500)
    def server_error(e):
        log.exception('Internal server error on %s', request.path)
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Internal protocol error'}), 500
        return render_template('error.html', code=500,
                               message='An internal protocol error occurred.'), 500

    @app.errorhandler(429)
    def rate_limited(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Rate limited — slow down'}), 429
        return render_template('error.html', code=429,
                               message='Too many requests. Please wait before trying again.'), 429

    # ─── Database ─────────────────────────────────────────────────
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    engine = create_engine(
        HeliosConfig.DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )

    # Import ALL models so their tables get created
    from models.bond import Bond  # noqa: F401 — required for table creation
    from models.vault_receipt import VaultReceipt  # noqa: F401
    from models.certificate import Certificate  # noqa: F401
    from models.energy_event import EnergyEvent  # noqa: F401
    from models.credential import Credential  # noqa: F401
    from models.space import Space, SpaceEvent  # noqa: F401
    from models.subscription import Subscription  # noqa: F401
    from models.payment_event import PaymentEvent  # noqa: F401
    from models.node_event import NodeEvent  # noqa: F401 — QR node telemetry
    Base.metadata.create_all(engine)

    SessionFactory = sessionmaker(bind=engine)
    Session = scoped_session(SessionFactory)

    @app.before_request
    def before_request():
        g.db_session = Session()

    @app.teardown_request
    def teardown_request(exception=None):
        session = g.pop('db_session', None)
        if session:
            if exception:
                session.rollback()
            session.close()

    # ─── Register Blueprints ──────────────────────────────────────
    from api.routes import (
        identity_bp, field_bp, network_bp, energy_bp,
        wallet_bp, token_bp, chat_bp,
        voice_bp, sms_bp, infra_bp, handoff_bp,
        treasury_bp, certificates_bp,
        funding_bp,
        spaces_bp, metrics_bp, rewards_bp,
        nodes_bp
    )
    app.register_blueprint(identity_bp)
    app.register_blueprint(field_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(energy_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(token_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(voice_bp)
    app.register_blueprint(sms_bp)
    app.register_blueprint(infra_bp)
    app.register_blueprint(handoff_bp)
    app.register_blueprint(treasury_bp)
    app.register_blueprint(certificates_bp)
    app.register_blueprint(funding_bp)
    app.register_blueprint(spaces_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(nodes_bp)

    # ─── Page Routes ──────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/enter")
    @app.route("/enter/<referrer>")
    def enter(referrer=None):
        return render_template("join.html", referrer=referrer)

    @app.route("/join")
    @app.route("/join/<referrer>")
    def join(referrer=None):
        return render_template("join.html", referrer=referrer)

    @app.route("/qr")
    @app.route("/qr/<helios_id>")
    def qr_page(helios_id=None):
        return render_template("qr.html", helios_id=helios_id)

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/field")
    def field():
        return render_template("network.html")

    @app.route("/network")
    def network():
        return render_template("network.html")

    @app.route("/ask")
    def ask():
        return render_template("ask.html")

    @app.route("/guide")
    def guide():
        return render_template("guide.html")

    @app.route("/start")
    @app.route("/handoff")
    def handoff():
        from core.handoff import get_handoff_manifest, list_handoff_docs

        return render_template("handoff.html", manifest=get_handoff_manifest(), docs=list_handoff_docs())

    @app.route("/handoff/docs/<slug>")
    def handoff_doc_page(slug):
        from core.handoff import get_handoff_doc

        document = get_handoff_doc(slug)
        if not document:
            abort(404)
        return render_template("handoff_doc.html", doc=document)

    @app.route("/handoff/docs/<slug>/raw")
    def handoff_doc_raw(slug):
        from core.handoff import get_handoff_doc

        document = get_handoff_doc(slug)
        if not document:
            abort(404)
        return Response(document["content"], mimetype="text/markdown; charset=utf-8")

    @app.route("/handoff/docs/<slug>/download")
    def handoff_doc_download(slug):
        from core.handoff import get_handoff_doc

        document = get_handoff_doc(slug)
        if not document:
            abort(404)
        response = Response(document["content"], mimetype="text/markdown; charset=utf-8")
        response.headers["Content-Disposition"] = f"attachment; filename={slug}.md"
        return response

    @app.route("/protocol")
    def protocol():
        return render_template("status.html")

    @app.route("/status")
    def status():
        return render_template("status.html")

    @app.route("/treasury")
    def treasury():
        return render_template("treasury.html")

    @app.route("/vault")
    def vault():
        return render_template("vault.html")

    @app.route("/vault/gold")
    def vault_gold():
        return render_template("vault_gold.html")

    @app.route("/activate")
    @app.route("/activate/<referrer>")
    def activate(referrer=None):
        return render_template("activate.html", referrer=referrer)

    @app.route("/earnings")
    def earnings():
        return render_template("earnings.html")

    @app.route("/certificates")
    def certificates():
        return render_template("certificates.html")

    @app.route("/opportunity")
    @app.route("/recruit")
    def opportunity():
        return render_template("recruit.html")

    @app.route("/metrics")
    def metrics():
        return render_template("metrics.html")

    @app.route("/launch")
    @app.route("/token-offering")
    def launch():
        return render_template("launch.html")

    @app.route("/tokenomics")
    def tokenomics():
        return render_template("tokenomics.html")

    @app.route("/web3")
    def web3():
        return render_template("web3.html")

    # ─── Health Check ─────────────────────────────────────────────
    @app.route("/health")
    @app.route("/api/health")
    def health():
        return {
            "status": "ok",
            "system": "helios",
            "version": "3.0.0",
            "paradigm": "energy_exchange",
            "domain": HeliosConfig.DOMAIN
        }

    # ─── Initialize Token Pools (first-run) ───────────────────────
    with app.app_context():
        session = Session()
        from models.token_pool import TokenPool
        if not session.query(TokenPool).first():
            from core.token import TokenEngine
            engine_t = TokenEngine(session)
            try:
                result = engine_t.initialize_pools()
                print(f"  ☀ Genesis — Token pools initialized: {result['total_supply']:,.0f} HLS")
            except ValueError:
                pass  # Already initialized
            finally:
                session.close()

    return app


# ─── Entry Point ──────────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║   ☀  HELIOS v3.0.0 — Allocation Protocol         ║
    ║                                                  ║
    ║   Smart contracts.  Gold-backed certificates.     ║
    ║   XRPL + Stellar.  Deterministic math.           ║
    ║                                                  ║
    ║   Guide:       http://localhost:{HeliosConfig.PORT}/guide         ║
    ║   Treasury:    http://localhost:{HeliosConfig.PORT}/treasury      ║
    ║   Gold Vault:  http://localhost:{HeliosConfig.PORT}/vault/gold    ║
    ║   Metrics:     http://localhost:{HeliosConfig.PORT}/metrics       ║
    ║   Advisory:    http://localhost:{HeliosConfig.PORT}/ask           ║
    ║   Domain:      {HeliosConfig.DOMAIN}                      ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)
    app.run(
        host=HeliosConfig.HOST,
        port=HeliosConfig.PORT,
        debug=HeliosConfig.DEBUG
    )
