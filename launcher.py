"""
Entry point for the PyInstaller-frozen Django backend.
Runs migrations, then serves the app via waitress (production WSGI server).
Tauri spawns this as a sidecar process and points its webview at the port below.
"""
import os
import sys

# When frozen by PyInstaller, base_dir is the temp extraction folder (_MEIPASS).
# Use a writable, persistent location for the SQLite DB instead - the user's
# AppData folder on Windows - so data survives across app restarts/updates.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    DATA_DIR = os.path.join(os.environ.get("APPDATA", BASE_DIR), "BSGForecastApp")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = BASE_DIR

os.makedirs(DATA_DIR, exist_ok=True)

# Make this DB path visible to settings.py - see note below on wiring it in.
os.environ.setdefault("APP_DATA_DIR", DATA_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ms.settings")  # adjust to your project

sys.path.insert(0, BASE_DIR)

import django  # noqa: E402
django.setup()

from django.core.management import call_command  # noqa: E402

PORT = 8000
HOST = "127.0.0.1"


def main():
    print(f"Starting Django backend on http://{HOST}:{PORT} ...")
    print(f"Data directory: {DATA_DIR}")

    # Apply any pending migrations automatically - no terminal access for the user.
    call_command("migrate", interactive=False, verbosity=1)

    from waitress import serve
    from ms.wsgi import application  # adjust to your project's wsgi module

    serve(application, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
