import requests
import socketio
import time

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('connection_status')
def on_connection_status(data):
    print(f'Connection status: {data}')

@sio.on('message')
def on_message(data):
    print(f'Received message: {data}')

def test_http():
    # Test HTTP endpoints
    print("\nTesting HTTP endpoints...")
    
    # Test home endpoint
    response = requests.get('http://localhost:8080/')
    print(f"Home endpoint: {response.text}")
    
    # Test status endpoint
    response = requests.get('http://localhost:8080/api/status')
    print(f"Status endpoint: {response.json()}")

def test_websocket():
    print("\nTesting WebSocket connection...")
    
    try:
        # Connect to the server
        sio.connect('http://localhost:8080')
        
        # Send a test message
        sio.emit('message', {'text': 'Hello from test client!'})
        
        # Wait for a moment to receive responses
        time.sleep(2)
        
        # Disconnect
        sio.disconnect()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_http()
    test_websocket() 