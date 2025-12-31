"""Quick test to verify Flask server can start"""
from app import app
import sys

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Server will be available at: http://127.0.0.1:5000")
    print("Press CTRL+C to stop")
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

