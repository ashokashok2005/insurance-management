from app import create_app

app = create_app()
app.testing = True # Propagate exceptions
client = app.test_client()

# Simulating Login
print("Attempting Login...")
try:
    response = client.post('/api/auth/login', json={
        'email': 'ashokarun301105@gmail.com', # From screenshot
        'password': 'password123' # Assuming standard test password or arbitrary, aiming to trigger the log logic
    })
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.data.decode('utf-8')}")
except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
