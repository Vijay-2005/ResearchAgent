import os
import subprocess
import sys
import time

def main():
    """
    This script runs both the FastAPI server and Streamlit app
    in a way that's compatible with Render.
    """
    print("Starting Knowledge Navigator in Render-compatible mode...")
    
    # Print environment info for debugging
    render_port = os.environ.get("PORT")
    print(f"RENDER PORT: {render_port}")
    
    # Start FastAPI in the background
    print("Starting FastAPI server...")
    api_process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Give the API time to start
    time.sleep(5)
    
    # Start Streamlit on Render's expected port
    print("Starting Streamlit server...")
    streamlit_cmd = [
        "streamlit", "run", "streamlit_app.py",
        "--server.port", str(render_port or 10000),
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
