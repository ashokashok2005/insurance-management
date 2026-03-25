print("Start import...", flush=True)
try:
    from app import create_app
    print("Imported create_app", flush=True)
    app = create_app()
    print("Created app", flush=True)
except Exception as e:
    print(f"FAILED: {e}", flush=True)
    import traceback
    traceback.print_exc()
