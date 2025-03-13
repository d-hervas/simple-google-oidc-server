import http.client as http_client
import logging
import os
import secrets

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, redirect, session, url_for
from pythonjsonlogger import jsonlogger

from flask_session import Session

# Configure custom logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

load_dotenv()

# Remove default handlers
logger.handlers = []


# Custom JSON formatter
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["level"] = record.levelname
        log_record["message"] = record.getMessage()


# Create and configure handler
handler = logging.StreamHandler()
formatter = CustomJsonFormatter("%(level)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Enable HTTP debugging with custom logging
http_client.HTTPConnection.debuglevel = 1


# Custom logging filter for HTTP requests
class HTTPFilter(logging.Filter):
    def filter(self, record):
        # Only log relevant HTTP-related messages
        if (
            "send:" in record.getMessage()
            or "reply:" in record.getMessage()
            or "header:" in record.getMessage()
        ):
            # Pretty-print and filter request/response details
            msg = record.getMessage()
            if "send:" in msg:
                # Extract method, URL, and body
                parts = msg.split("\r\n")
                method_url = parts[0].replace("send: b'", "").split(" ")[0:2]
                body = next(
                    (
                        p.split(": ")[1]
                        for p in parts
                        if "Content-Length" not in p and ": " in p
                    ),
                    "",
                )
                record.msg = {
                    "request": {
                        "method": method_url[0],
                        "url": method_url[1],
                        "body": body,
                    }
                }
            elif "reply:" in msg:
                record.msg = {"response": {"status": msg.split("'")[1]}}
            elif "header:" in msg:
                header = msg.split("header: ")[1]
                record.msg = {"response_header": header}
            return True
        return False


# Apply filter to urllib3 logger
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.addFilter(HTTPFilter())

app = Flask(__name__)
app.secret_key = "dumb-secret"

app.config["SESSION_TYPE"] = "filesystem"
Session(app)

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid profile email",
        "response_type": "code",
    },
)


@app.route("/")
def home():
    return """
        <html>
            <body>
                <a href="/auth/google">
                    <img src="https://developers.google.com/identity/images/btn_google_signin_light_normal_web.png" 
                         alt="Sign in with Google">
                </a>
            </body>
        </html>
    """


@app.route("/auth/google")
def login():
    nonce = secrets.token_urlsafe(16)
    session["nonce"] = nonce
    redirect_uri = url_for("callback", _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce, prompt="select_account")


@app.route("/auth/google/callback")
def callback():
    try:
        token = google.authorize_access_token()

        print("ID Token:", token.get("id_token"))
        print("Access Token:", token.get("access_token"))
        print("Refresh Token:", token.get("refresh_token", "Not provided"))

        nonce = session.pop("nonce", None)
        user_info = google.parse_id_token(token, nonce=nonce)
        print("User Info:", user_info)

        return "Authentication successful! Check your server console for token details."
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(port=3000, debug=True)
