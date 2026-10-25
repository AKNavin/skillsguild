"""Launch a local-only credential window; expose history, never broker tokens."""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import http.cookies
import http.server
import json
import secrets
import threading
import time
import urllib.parse
import webbrowser

from broker_core import BrokerError, authenticate

MAX_BODY = 16384
STYLE = "body{font:16px/1.5 system-ui,sans-serif;color:#17212f;background:#f5f7fa;margin:0;padding:28px}main{max-width:720px;margin:auto;padding:32px;background:white;border:1px solid #dae1ea;border-radius:14px}h1{font-size:26px;margin-top:0}p{color:#445166}details{padding:16px;border:1px solid #dce3ec;border-radius:8px;margin:14px 0}summary{cursor:pointer;font-weight:650;color:#17212f}input,select{box-sizing:border-box;width:100%;font:inherit;border:1px solid #bcc8d7;border-radius:5px;padding:9px;margin-top:4px}button{font:inherit;color:white;background:#0969da;border:0;border-radius:5px;padding:10px 16px;cursor:pointer}a{color:#0969da}code{word-break:break-all;color:#17212f}"
STYLE_HASH = base64.b64encode(hashlib.sha256(STYLE.encode()).digest()).decode()


class LocalServer(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, port=0, authenticator=authenticate, notify=print, lifetime=43200):
        super().__init__(("127.0.0.1", port), Handler)
        self.origin = "http://127.0.0.1:" + str(self.server_port)
        self.login_key, self.csrf, self.cookie = [secrets.token_urlsafe(32) for _ in range(3)]
        self.session_key = None
        self.session = None
        self.authenticator, self.notify = authenticator, notify
        self.deadline = time.monotonic() + lifetime
        self.state_lock = threading.Lock()

    def handle_error(self, request, client_address):
        # Default socketserver tracebacks could accidentally expose request locals.
        self.notify("A local request failed. No request details were logged.")

    def clear(self):
        with self.state_lock:
            if self.session:
                self.session.clear()
            self.session, self.session_key = None, None

    def server_close(self):
        self.clear()
        super().server_close()


def page(content):
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            "<title>SkillsGuild local broker connection</title><style>" + STYLE + "</style><body><main>"
            "<h1>Connect your broker locally</h1>"
            "<p>This window runs on your computer. Credentials go from this helper to your chosen broker over HTTPS. "
            "They are held in memory until you disconnect or stop the helper. No trading endpoints are available.</p>"
            "<p>Do not paste credentials into agent chat. An AI or another program with access to your operating-system account "
            "can still inspect process memory; this is not a security boundary against that access.</p>"
            + content + "</main></body></html>").encode()


def login_form(server):
    def form(broker, mode, fields, button):
        hidden = "".join("<input type='hidden' name='" + k + "' value='" + html.escape(v, quote=True) + "'>" for k, v in {"csrf": server.csrf, "broker": broker, "mode": mode}.items())
        inputs = "".join("<p><label>" + label + "<br><input autocomplete='off' spellcheck='false' type='password' name='" + name + "' required maxlength='6000'></label></p>" for name, label in fields)
        plan = "<p><label>Data plan <select name='plan'><option value='standard'>Standard</option><option value='prime'>Prime (only if subscribed)</option></select></label></p>" if broker == "fyers" else ""
        return "<form method='post' action='/authenticate' autocomplete='off'>" + hidden + inputs + plan + "<button>" + button + "</button></form>"
    return page(
        "<p>Choose your broker below. Broker passwords, PINs and OTPs belong only on the broker's own login page.</p>"
        "<details><summary>Zerodha Kite</summary><p>Complete Kite Connect login using your API app. Paste its fresh request_token here with the matching app key and secret.</p>"
        "<p><a rel='noreferrer noopener' target='_blank' href='https://kite.trade/docs/connect/v3/user/'>Official Kite login instructions</a></p>"
        + form("zerodha", "code", [("client_id", "API key"), ("secret", "API secret"), ("code", "Fresh request token")], "Exchange request token")
        + "<details><summary>Use an existing Kite access token</summary>"
        + form("zerodha", "token", [("client_id", "API key"), ("access_token", "Access token")], "Connect Kite") + "</details></details>"
        + "<details><summary>Dhan</summary><p>In Dhan Web, open My Profile → Access DhanHQ APIs and generate an access token. Historical data needs the appropriate data subscription.</p>"
        "<p><a rel='noreferrer noopener' target='_blank' href='https://web.dhan.co/'>Open Dhan Web</a></p>"
        + form("dhan", "token", [("client_id", "Dhan client ID"), ("access_token", "Access token")], "Connect Dhan") + "</details>"
        + "<details><summary>FYERS</summary><p>Complete your individual app's broker login using its registered redirect URL. Paste the fresh auth_code with your app ID and secret.</p>"
        "<p><a rel='noreferrer noopener' target='_blank' href='https://fyers.in/api-docs/v3/api/authentication/individual-app/'>Official FYERS login instructions</a></p>"
        + form("fyers", "code", [("client_id", "App ID (including suffix)"), ("secret", "App secret"), ("code", "Fresh auth code")], "Exchange auth code")
        + "<details><summary>Use an existing FYERS access token</summary>"
        + form("fyers", "token", [("client_id", "App ID (including suffix)"), ("access_token", "Access token")], "Connect FYERS") + "</details></details>")


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "SkillsGuildLocal/1.0"
    sys_version = ""
    protocol_version = "HTTP/1.0"

    def log_message(self, *args):
        pass

    def send(self, code, data, content_type="application/json", cookie=False):
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'sha256-" + STYLE_HASH + "'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
        if cookie:
            self.send_header("Set-Cookie", "sg_local=" + self.server.cookie + "; HttpOnly; SameSite=Strict; Path=/")
        self.end_headers()
        self.wfile.write(data)

    def boundary(self):
        if self.client_address[0] != "127.0.0.1" or self.headers.get_all("Host", []) != ["127.0.0.1:" + str(self.server.server_port)]:
            self.send(403, {"error": "Invalid local host."})
            return False
        origin = self.headers.get("Origin")
        if origin is not None and origin != self.server.origin:
            self.send(403, {"error": "Cross-origin requests are not allowed."})
            return False
        if self.headers.get("Sec-Fetch-Site") == "cross-site":
            self.send(403, {"error": "Cross-site requests are not allowed."})
            return False
        if time.monotonic() >= self.server.deadline:
            self.server.clear()
            self.send(410, {"error": "Helper expired. Restart it."})
            return False
        return True

    def read_body(self, content_type):
        if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length", [])) != 1:
            raise BrokerError("A bounded Content-Length is required.")
        if self.headers.get("Content-Type", "").split(";", 1)[0] != content_type:
            raise BrokerError("Unsupported request content type.")
        try:
            size = int(self.headers["Content-Length"])
        except (TypeError, ValueError):
            raise BrokerError("Invalid request length.") from None
        if not 0 < size <= MAX_BODY:
            raise BrokerError("Request exceeded the local size limit.")
        self.connection.settimeout(5)
        raw = self.rfile.read(size)
        if len(raw) != size:
            raise BrokerError("Incomplete local request.")
        return raw

    def browser_form(self):
        if self.headers.get("Origin") != self.server.origin:
            raise BrokerError("The login form must be submitted from this local window.")
        cookie = http.cookies.SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
        except http.cookies.CookieError:
            raise BrokerError("Invalid local browser session.") from None
        if "sg_local" not in cookie or not secrets.compare_digest(cookie["sg_local"].value, self.server.cookie):
            raise BrokerError("Open the original local login window first.")
        values = urllib.parse.parse_qs(self.read_body("application/x-www-form-urlencoded").decode("utf-8"), max_num_fields=12)
        if any(len(v) != 1 for v in values.values()):
            raise BrokerError("Duplicate form fields are not accepted.")
        fields = {k: v[0] for k, v in values.items()}
        if not secrets.compare_digest(fields.pop("csrf", ""), self.server.csrf):
            raise BrokerError("Local form verification failed. Reopen the login window.")
        return fields

    def capability(self, suffix):
        key = self.server.session_key
        expected = "/session/" + key + suffix if key else ""
        if not key or not secrets.compare_digest(self.path, expected) or not self.server.session:
            self.send(404, {"error": "No active session at this URL."})
            return None
        if self.headers.get("X-SkillsGuild-Request") != "history-client":
            self.send(403, {"error": "Use the packaged local downloader."})
            return None
        return self.server.session

    def do_GET(self):
        if not self.boundary():
            return
        if secrets.compare_digest(self.path, "/login/" + self.server.login_key):
            self.send(200, login_form(self.server), "text/html; charset=utf-8", cookie=True)
        elif self.path.endswith("/status"):
            session = self.capability("/status")
            if session:
                self.send(200, {"broker": session.broker, "plan": session.plan, "connected": session.active, "permissions": ["daily-history"]})
        else:
            self.send(404, {"error": "Unknown local route."})

    def do_POST(self):
        if not self.boundary():
            return
        fields = None
        try:
            if self.path == "/authenticate":
                fields = self.browser_form()
                session = self.server.authenticator(fields)
                self.server.clear()
                with self.server.state_lock:
                    self.server.session = session
                    self.server.session_key = secrets.token_urlsafe(32)
                    url = self.server.origin + "/session/" + self.server.session_key
                self.server.notify("Connected " + session.broker + ". Local read-only session: " + url)
                content = "<h2>Connected to " + html.escape(session.broker) + "</h2><p>Give your agent this local session reference. It contains no broker credential and permits only historical-data requests while this process runs.</p><p><code>" + url + "</code></p><p>Keep this helper running while downloading. Stop it with Ctrl+C afterward.</p><form method='post' action='/disconnect'><input type='hidden' name='csrf' value='" + self.server.csrf + "'><button>Disconnect and discard session</button></form>"
                self.send(200, page(content), "text/html; charset=utf-8")
            elif self.path == "/disconnect":
                fields = self.browser_form()
                self.server.clear()
                self.send(200, page("<h2>Disconnected</h2><p>The helper no longer retains your broker session. This does not revoke the token at the broker; use the broker portal for revocation.</p>"), "text/html; charset=utf-8")
            elif self.path.endswith("/history"):
                session = self.capability("/history")
                if not session:
                    return
                body = json.loads(self.read_body("application/json"))
                if not isinstance(body, dict) or set(body) != {"instrument", "from", "to"} or not isinstance(body["instrument"], dict):
                    raise BrokerError("Invalid history request.")
                rows = session.history(body["instrument"], body["from"], body["to"])
                self.send(200, {"candles": rows})
            else:
                self.send(404, {"error": "Unknown local route."})
        except BrokerError as exc:
            self.send(400, {"error": str(exc)})
        except (ValueError, UnicodeError, TypeError, OSError):
            self.send(400, {"error": "Malformed or incomplete local request."})
        except Exception:
            self.send(500, {"error": "Local request failed. No request details were logged."})
        finally:
            if fields is not None:
                fields.clear()

    def do_OPTIONS(self):
        if self.boundary():
            self.send(403, {"error": "Cross-origin access is disabled."})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=0, help="Default: random local port")
    args = parser.parse_args()
    server = LocalServer(args.port)
    url = server.origin + "/login/" + server.login_key
    print("Open the local credential window: " + url, flush=True)
    print("Keep this process running. Stop with Ctrl+C to discard credentials.", flush=True)
    if not args.no_browser:
        webbrowser.open(url, new=1)
    timer = threading.Timer(43200, server.shutdown)
    timer.daemon = True
    timer.start()
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        timer.cancel()
        server.server_close()


if __name__ == "__main__":
    main()
