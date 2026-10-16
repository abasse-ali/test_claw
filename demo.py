#!/usr/bin/env python3
"""Demo script: starts server, verifies it works, stops server."""
import subprocess
import time
import requests
import sys

# Start server in background
proc = subprocess.Popen([sys.executable, 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(2)
try:
    resp = requests.get('http://localhost:5000', timeout=5)
    assert resp.status_code == 200
    assert 'Gestionnaire de Budget' in resp.text
    assert 'Revenus' in resp.text
    assert 'Dépenses' in resp.text
    assert 'Épargne' in resp.text
    print('✓ App starts and serves main page correctly')
    sys.exit(0)
finally:
    proc.terminate()
    proc.wait(timeout=2)