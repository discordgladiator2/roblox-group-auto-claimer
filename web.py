import shared
import os
import logging

def get_blob(cookie):
    shared.sock.send(
        f"POST /v1/groups/142336/users HTTP/1.1\n"
        "Host:groups.roblox.com\n"
        "Content-Type:application/json\n"
        "Content-Length:78\n"
        f"X-CSRF-TOKEN:{shared.csrf_token}\n"
        f"Cookie:.ROBLOSECURITY={cookie}\n"
        "\n"
        '{"captchaId":"\\n","captchaToken":"x","captchaProvider":"PROVIDER_ARKOSE_LABS"}'.encode())
    return shared.sock.recv(1024**2).split(b'dxBlob\\":\\"', 1)[1].split(b'\\', 1)[0].decode()

def create_app(**kwargs):
    globals().update(kwargs)

    app = Flask("x")
    app.jinja_env.filters["urlencode"] = urlencode
    os.environ["WERKZEUG_RUN_MAIN"] = "true"
    logging.getLogger("werkzeug").disabled = True

    @app.route("/")
    def view_dashboard():
        return render_template(
            "dashboard.html")

    @app.route("/webhook", methods=["POST"])
    def post_webhook():
        data = request.get_json()
        group_id = int(data["embeds"][0]["fields"][0]["value"])
        group_queue.put(group_id)
        return "", 204

    @app.route("/captcha")
    def view_captcha():
        return render_template(
            "captcha.html",
            public_key="63E4117F-E727-42B4-6DAA-C8448E9B137F",
            service_url="https://roblox-api.arkoselabs.com",
            data={"blob": get_blob(cookie)}
        )

    @app.route("/api/token-queue", methods=["POST"])
    def post_captcha():
        token = request.get_json()["token"]
        token_queue.put(token)
        return "", 204

    @app.route("/api/stats")
    def view_stats():
        return {
            "tokenQueueLength": token_queue.size(),
            "tokenQueueExpiringIn": token_queue.earliest_expiry()
        }

    @app.route("/api/logs")
    def view_logs():
        return jsonify(list(logs))

    return app