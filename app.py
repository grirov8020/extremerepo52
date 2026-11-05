#!/usr/bin/env python3
"""
Strix Pentest Web Interface for Railway
AI-powered penetration testing with Claude Sonnet 4-6
"""

import os
import sys
import json
import asyncio
import logging
import secrets
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from threading import Thread, Lock

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
import anthropic

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['RESULTS_FOLDER'] = '/tmp/results'

# Create directories
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
Path(app.config['RESULTS_FOLDER']).mkdir(parents=True, exist_ok=True)

# Global state for scan management
scans_lock = Lock()
active_scans: Dict[str, Dict[str, Any]] = {}

# Claude API client
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
if not ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY not set - Claude features will be limited")

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


def get_claude_analysis(scan_results: str, target: str) -> str:
    """Get AI analysis from Claude Sonnet 4-6"""
    if not claude_client:
        return "⚠️ Claude API key not configured. Set ANTHROPIC_API_KEY environment variable."
    
    try:
        prompt = f"""You are an expert penetration tester analyzing security scan results.

Target: {target}

Scan Results:
{scan_results}

Provide a comprehensive security analysis including:
1. Executive Summary - high-level risk assessment
2. Critical Findings - vulnerabilities that need immediate attention
3. Detailed Analysis - technical breakdown of each finding
4. Exploitation Scenarios - how attackers could exploit these vulnerabilities
5. Remediation Recommendations - specific fixes with priority levels
6. Compliance Impact - OWASP Top 10, CVE references

Be specific, technical, and actionable. Format as markdown."""

        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text if response.content else "No analysis generated"
    
    except Exception as e:
        logger.error(f"Claude analysis failed: {e}")
        return f"⚠️ AI analysis error: {str(e)}"


def run_strix_scan(scan_id: str, target: str, scan_type: str, options: Dict[str, Any]) -> None:
    """Run Strix pentest in background thread"""
    try:
        with scans_lock:
            active_scans[scan_id]['status'] = 'running'
            active_scans[scan_id]['start_time'] = datetime.now().isoformat()
        
        # Prepare scan command
        cmd = ['strix', '--target', target]
        
        # Add scan type specific options
        if scan_type == 'web':
            cmd.extend(['--skills', 'web'])
        elif scan_type == 'api':
            cmd.extend(['--skills', 'api'])
        elif scan_type == 'full':
            cmd.extend(['--skills', 'all'])
        
        # Add custom options
        if options.get('aggressive'):
            cmd.append('--aggressive')
        if options.get('stealth'):
            cmd.append('--stealth')
        if options.get('depth'):
            cmd.extend(['--depth', str(options['depth'])])
        
        # Set environment variables
        env = os.environ.copy()
        if not env.get('STRIX_LLM'):
            env['STRIX_LLM'] = 'anthropic/claude-sonnet-4-20250514'
        if ANTHROPIC_API_KEY:
            env['LLM_API_KEY'] = ANTHROPIC_API_KEY
        
        result_dir = Path(app.config['RESULTS_FOLDER']) / scan_id
        result_dir.mkdir(parents=True, exist_ok=True)
        
        # Run scan
        logger.info(f"Starting scan {scan_id}: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=str(result_dir)
        )
        
        stdout, stderr = process.communicate(timeout=3600)  # 1 hour timeout
        
        # Save raw output
        output_file = result_dir / 'scan_output.txt'
        output_file.write_text(f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}")
        
        # Get Claude analysis
        logger.info(f"Getting Claude analysis for scan {scan_id}")
        analysis = get_claude_analysis(stdout, target)
        analysis_file = result_dir / 'claude_analysis.md'
        analysis_file.write_text(analysis)
        
        with scans_lock:
            active_scans[scan_id]['status'] = 'completed'
            active_scans[scan_id]['end_time'] = datetime.now().isoformat()
            active_scans[scan_id]['output'] = stdout
            active_scans[scan_id]['analysis'] = analysis
            active_scans[scan_id]['success'] = process.returncode == 0
        
        logger.info(f"Scan {scan_id} completed successfully")
    
    except subprocess.TimeoutExpired:
        logger.error(f"Scan {scan_id} timed out")
        with scans_lock:
            active_scans[scan_id]['status'] = 'failed'
            active_scans[scan_id]['error'] = 'Scan timed out (exceeded 1 hour)'
    
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {e}")
        with scans_lock:
            active_scans[scan_id]['status'] = 'failed'
            active_scans[scan_id]['error'] = str(e)


@app.route('/')
def index():
    """Main page with scan form"""
    return render_template('index.html')


@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    """Start a new pentest scan"""
    try:
        data = request.get_json()
        target = data.get('target', '').strip()
        scan_type = data.get('scan_type', 'web')
        
        if not target:
            return jsonify({'error': 'Target is required'}), 400
        
        # Validate target format
        if not (target.startswith('http://') or target.startswith('https://') or 
                target.startswith('/') or Path(target).exists()):
            return jsonify({'error': 'Invalid target format'}), 400
        
        # Generate scan ID
        scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}"
        
        # Parse options
        options = {
            'aggressive': data.get('aggressive', False),
            'stealth': data.get('stealth', False),
            'depth': int(data.get('depth', 3))
        }
        
        # Initialize scan record
        with scans_lock:
            active_scans[scan_id] = {
                'id': scan_id,
                'target': target,
                'scan_type': scan_type,
                'options': options,
                'status': 'queued',
                'created_at': datetime.now().isoformat()
            }
        
        # Start scan in background
        thread = Thread(
            target=run_strix_scan,
            args=(scan_id, target, scan_type, options),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'scan_id': scan_id,
            'message': 'Scan started successfully'
        }), 202
    
    except Exception as e:
        logger.error(f"Failed to start scan: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan/<scan_id>/status')
def scan_status(scan_id: str):
    """Get scan status and results"""
    with scans_lock:
        scan = active_scans.get(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        # Return safe copy without sensitive data
        return jsonify({
            'id': scan['id'],
            'target': scan['target'],
            'scan_type': scan['scan_type'],
            'status': scan['status'],
            'created_at': scan.get('created_at'),
            'start_time': scan.get('start_time'),
            'end_time': scan.get('end_time'),
            'success': scan.get('success'),
            'error': scan.get('error')
        })


@app.route('/api/scan/<scan_id>/results')
def scan_results(scan_id: str):
    """Get detailed scan results and AI analysis"""
    with scans_lock:
        scan = active_scans.get(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        if scan['status'] != 'completed':
            return jsonify({'error': 'Scan not completed yet'}), 400
        
        return jsonify({
            'id': scan['id'],
            'target': scan['target'],
            'output': scan.get('output', ''),
            'analysis': scan.get('analysis', ''),
            'success': scan.get('success', False)
        })


@app.route('/api/scan/<scan_id>/download')
def download_results(scan_id: str):
    """Download scan results as file"""
    result_dir = Path(app.config['RESULTS_FOLDER']) / scan_id
    analysis_file = result_dir / 'claude_analysis.md'
    
    if not analysis_file.exists():
        return jsonify({'error': 'Results not found'}), 404
    
    return send_file(
        analysis_file,
        as_attachment=True,
        download_name=f'strix_pentest_{scan_id}.md'
    )


@app.route('/api/scans')
def list_scans():
    """List all scans"""
    with scans_lock:
        scans_list = [
            {
                'id': s['id'],
                'target': s['target'],
                'scan_type': s['scan_type'],
                'status': s['status'],
                'created_at': s.get('created_at')
            }
            for s in active_scans.values()
        ]
        return jsonify({'scans': scans_list})


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'strix_installed': True,
        'claude_available': bool(claude_client),
        'active_scans': len(active_scans)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Strix Pentest Web Interface on port {port}")
    logger.info(f"Claude API: {'Configured' if claude_client else 'Not configured'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
