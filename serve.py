import os
import subprocess
import sys
import time
import signal

def main():
    """
    This script runs both the FastAPI server and Streamlit app
    in a way that's compatible with Render.
    """
    print("Starting Knowledge Navigator in Render-compatible mode...")
    
    # Print environment info for debugging
    render_port = os.environ.get("PORT")
    print(f"RENDER PORT: {render_port}")
    
    # Set API port to 8000
    api_port = 8000
    os.environ["API_PORT"] = str(api_port)
    
    # Start FastAPI in the background with explicit port
    print(f"Starting FastAPI server on port {api_port}...")
    api_cmd = [sys.executable, "app.py", "--port", str(api_port)]
    api_process = subprocess.Popen(
        api_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Give the API time to start
    print("Waiting for API to start...")
    time.sleep(10)  # Increased wait time
    
    # Start Streamlit on Render's expected port
    streamlit_port = render_port or 10000
    print(f"Starting Streamlit server on port {streamlit_port}...")
    streamlit_cmd = [
        "streamlit", "run", "streamlit_app.py",
        "--server.port", str(streamlit_port),
        "--server.address", "0.0.0.0"
    ]
    streamlit_process = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Monitor both processes
    try:
        while True:
            api_output = api_process.stdout.readline()
            if api_output:
                print(f"[API] {api_output.strip()}")
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("WARNING: API process has terminated!")
                break
                
            if streamlit_process.poll() is not None:
                print("WARNING: Streamlit process has terminated!")
                break
                
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping servers...")
    finally:
        # Clean up processes
        if api_process.poll() is None:
            api_process.terminate()
        if streamlit_process.poll() is None:
            streamlit_process.terminate()
    
if __name__ == "__main__":
    main()
