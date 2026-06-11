import os
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from dotenv import load_dotenv
load_dotenv()

from app import create_app

env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    host = "0.0.0.0" if env == "production" else "localhost"
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=app.config.get("DEBUG", False))
