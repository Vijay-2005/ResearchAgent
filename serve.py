import os
import subprocess
import sys
import time

def main():
    """
    This script runs both the FastAPI server and Streamlit app
    for Render.com deployment.
    """
    print("Starting Knowledge Navigator in Render-compatible mode...")
    
    # Get render port
    render_port = os.environ.get("PORT", "10000")
    print(f"RENDER PORT: {render_port}")
    
    # Set environment variables
    env_vars = os.environ.copy()
    
    # Set API port to 8000
    api_port = 8000
    
    # Start FastAPI in the background
    print(f"Starting FastAPI server on port {api_port}...")
    api_cmd = [sys.executable, "app.py"]
    api_process = subprocess.Popen(
        api_cmd,
        env=env_vars,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Give the API time to start
    print("Waiting for API to start...")
    time.sleep(5)
    
    # Start Streamlit
    print(f"Starting Streamlit server on port {render_port}...")
    streamlit_cmd = [
        "streamlit", "run", "streamlit_app.py",
        "--server.port", render_port,
        "--server.address", "0.0.0.0",
        "--browser.serverAddress", "0.0.0.0",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    streamlit_process = subprocess.Popen(
        streamlit_cmd,
        env=env_vars,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Monitor both processes
    while True:
        # Print API output
        api_line = api_process.stdout.readline()
        if api_line:
            print(f"[API] {api_line.strip()}")
        
        # Print Streamlit output
        streamlit_line = streamlit_process.stdout.readline()
        if streamlit_line:
            print(f"[STREAMLIT] {streamlit_line.strip()}")
        
        # Check if processes are still running
        api_status = api_process.poll()
        streamlit_status = streamlit_process.poll()
        
        if api_status is not None:
            print(f"API process exited with code {api_status}")
            break
            
        if streamlit_status is not None:
            print(f"Streamlit process exited with code {streamlit_status}")
            break
            
        # Short sleep to prevent CPU hogging
        time.sleep(0.1)

if __name__ == "__main__":
    main()
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
