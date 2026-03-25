import sys
import os

# Ensure the root directory is in the python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

try:
    from app import create_app
    app = create_app()
except Exception as e:
    import traceback
    from flask import Flask
    app = Flask(__name__)
    @app.route('/')
    @app.route('/<path:path>')
    def catch_all(path=''):
        return f"<h1>App Initialization Error</h1><pre>{str(e)}</pre><pre>{traceback.format_exc()}</pre>", 500

# This is the line Vercel actually needs
handler = app

if __name__ == "__main__":
    app.run()
