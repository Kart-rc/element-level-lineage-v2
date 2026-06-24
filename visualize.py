#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
import sys
import threading
import time

PORT = 8000
# Target directory containing the html files
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deliverables", "latest_source", "Data Lineage Impact Platform-5")

if not os.path.exists(DIRECTORY):
    # Fallback to root directory if the folder structure changes
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server(port):
    # Allow address reuse to avoid port locking
    socketserver.TCPServer.allow_reuse_address = True
    while port < 9000:
        try:
            with socketserver.TCPServer(("", port), Handler) as httpd:
                url = f"http://localhost:{port}/Index%20-%20Throughline%20PRDs.dc.html"
                print(f"\n==================================================")
                print(f"  Throughline Prototype & PRD Server Started")
                print(f"==================================================")
                print(f"  Serving files from: {DIRECTORY}")
                print(f"  URL:                {url}")
                print(f"==================================================")
                print(f"  Opening browser...")
                
                # Open browser in a separate thread after server starts
                def open_browser():
                    time.sleep(0.5)
                    webbrowser.open(url)
                
                threading.Thread(target=open_browser, daemon=True).start()
                
                print(f"  Press Ctrl+C to stop the server.\n")
                httpd.serve_forever()
        except OSError:
            print(f"  Port {port} is in use, trying {port + 1}...")
            port += 1
    print("Error: Could not find an open port to run the server.")
    sys.exit(1)

if __name__ == "__main__":
    start_server(PORT)
