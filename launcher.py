"""
PyInstaller entry point for the Django backend.

Responsibilities:
- Determine whether the app is running frozen by PyInstaller.
- Create a persistent AppData directory for the SQLite database.
- Configure Django environment variables.
- Run database migrations.
- Collect static files.
- Start Django using Waitress.

The first admin user is NOT created here.
The /login/setup/ page handles first-time administrator creation.
"""

import os
import sys


# ============================================================================
# PATH CONFIGURATION
# ============================================================================

if getattr(sys, "frozen", False):
    # Directory containing the packaged EXE.
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))

    # PyInstaller's temporary extraction directory.
    BUNDLE_DIR = getattr(sys, "_MEIPASS", EXE_DIR)

    # Persistent writable application directory.
    #
    # This survives application updates/reinstallations as long as
    # the user's AppData folder is preserved.
    DATA_DIR = os.path.join(
        os.environ.get("APPDATA", EXE_DIR),
        "BSGForecastApp",
    )

    # Tell Django that this is the packaged application.
    os.environ["APP_FROZEN"] = "1"

else:
    # Normal development environment.
    EXE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    BUNDLE_DIR = EXE_DIR
    DATA_DIR = EXE_DIR

    os.environ.setdefault("APP_FROZEN", "0")


# ============================================================================
# CREATE APPLICATION DATA DIRECTORY
# ============================================================================

os.makedirs(DATA_DIR, exist_ok=True)


# ============================================================================
# DJANGO ENVIRONMENT
# ============================================================================

os.environ.setdefault(
    "APP_DATA_DIR",
    DATA_DIR,
)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ms.settings",
)


# ============================================================================
# PYTHON PATH
# ============================================================================

# Make the bundled Django project available to Python.
if EXE_DIR not in sys.path:
    sys.path.insert(0, EXE_DIR)

if BUNDLE_DIR not in sys.path:
    sys.path.insert(0, BUNDLE_DIR)


# ============================================================================
# DJANGO INITIALIZATION
# ============================================================================

import django  # noqa: E402

django.setup()


# Import call_command only, NOT the wsgi application yet.
#
# WhiteNoise's middleware snapshots STATIC_ROOT's contents the moment
# the WSGI application (and therefore the middleware stack) is
# constructed. If that import happens before collectstatic has run,
# WhiteNoise permanently believes STATIC_ROOT is empty/missing for the
# lifetime of the process -- collectstatic running later does nothing
# to fix an already-initialized middleware instance. So we deliberately
# delay `from ms.wsgi import application` until after collectstatic
# finishes inside main().
from django.core.management import call_command  # noqa: E402
from waitress import serve  # noqa: E402


# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

HOST = "127.0.0.1"
PORT = 8000


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 60)
    print("KFC Marketing & Sales - Django Backend")
    print("=" * 60)

    print(f"Frozen application : {getattr(sys, 'frozen', False)}")
    print(f"Bundle directory   : {BUNDLE_DIR}")
    print(f"Data directory     : {DATA_DIR}")
    print(f"Database           : {os.path.join(DATA_DIR, 'db.sqlite3')}")
    print(f"Server             : http://{HOST}:{PORT}/")
    print("=" * 60)


    # ------------------------------------------------------------------------
    # DATABASE MIGRATIONS
    # ------------------------------------------------------------------------

    print()
    print("Running database migrations...")

    try:
        call_command(
            "migrate",
            interactive=False,
            verbosity=1,
        )

    except Exception as exc:
        print()
        print("ERROR: Database migration failed.")
        print(str(exc))
        raise


    # ------------------------------------------------------------------------
    # STATIC FILES
    # ------------------------------------------------------------------------

    print()
    print("Collecting static files...")

    try:
        call_command(
            "collectstatic",
            interactive=False,
            verbosity=0,
            clear=True,
        )

    except Exception as exc:
        print()
        print("ERROR: Static file collection failed.")
        print(str(exc))
        raise


    # ------------------------------------------------------------------------
    # START SERVER
    # ------------------------------------------------------------------------
    #
    # The wsgi application (and its middleware stack, including
    # WhiteNoise) is imported here -- deliberately after collectstatic
    # has already populated STATIC_ROOT -- so WhiteNoise's static file
    # snapshot reflects what's actually on disk.

    from ms.wsgi import application  # noqa: E402

    print()
    print("=" * 60)
    print("Django backend is ready.")
    print(f"Open: http://{HOST}:{PORT}/")
    print("=" * 60)
    print()


    serve(
        application,
        host=HOST,
        port=PORT,
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()