#!/usr/bin/env python3
"""Strix Web Interface для Railway с поддержкой Claude Sonnet 4.6"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import subprocess, traceback, sys, time, re, sqlite3
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Конфигурация
UPLOAD_FOLDER = Path('/tmp/uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER = Path('/tmp/results')
RESULTS_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Глобальное хранилище запущенных сканов
active_scans: Dict[str, Any] = {}


def configure_claude_sonnet(api_base: str = None, api_key: str = None):
    """Настройка Claude Sonnet 4.6 через кастомный API endpoint"""
    
    final_api_base = api_base or os.getenv('ANTHROPIC_BASE_URL')
    final_api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
    # Устанавливаем переменные окружения для Strix
    os.environ['STRIX_LLM'] = 'claude-sonnet-4-6'
    os.environ['LLM_API_BASE'] = final_api_base.rstrip('/')
    os.environ['LLM_API_KEY'] = final_api_key
    os.environ['OPENAI_API_BASE'] = final_api_base.rstrip('/')
    os.environ['OPENAI_API_KEY'] = final_api_key
    
    # Форсируем использование chat completions API (более совместимо)
    os.environ['STRIX_API_TYPE'] = 'chat_completions'
    
    # Дополнительные настройки для совместимости
    os.environ['LITELLM_BASE_URL'] = final_api_base.rstrip('/')
    os.environ['LLM_DISABLE_STREAMING'] = 'false'
    os.environ['LLM_TIMEOUT'] = '300'
    
    logger.info(f"✅ Configured Claude Sonnet 4.6 with API base: {final_api_base}")
    
    return {
        'model': 'claude-sonnet-4-6',
        'api_base': final_api_base,
        'api_key': '***' if final_api_key else None
    }


@app.route('/')
def index():
    """Главная страница с веб-интерфейсом"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Получение/обновление конфигурации API"""
    if request.method == 'POST':
        data = request.json
        api_base = data.get('api_base')
        api_key = data.get('api_key')
        
        config = configure_claude_sonnet(api_base, api_key)
        return jsonify({
            'success': True,
            'config': config
        })
    
    # GET - возвращаем текущую конфигурацию
    return jsonify({
        'model': os.getenv('STRIX_LLM', 'claude-sonnet-4-6'),
        'api_base': os.getenv('LLM_API_BASE', ''),
        'api_key_set': bool(os.getenv('LLM_API_KEY'))
    })


@app.route('/api/scan', methods=['POST'])
def start_scan():
    """Запуск нового пентест скана"""
    try:
        data = request.json
        target = data.get('target')
        scan_type = data.get('scan_type', 'web')
        
        if not target:
            return jsonify({'error': 'Target is required'}), 400
        
        # Конфигурируем модель
        configure_claude_sonnet()
        
        # Создаем уникальный ID скана
        scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Создаем конфигурацию скана
        scan_config = {
            'target': target,
            'scan_type': scan_type,
            'scan_id': scan_id,
            'workspace_dir': str(RESULTS_FOLDER / scan_id)
        }
        
        # Сохраняем статус скана
        active_scans[scan_id] = {
            'status': 'running',
            'target': target,
            'scan_type': scan_type,
            'started_at': datetime.now().isoformat(),
            'config': scan_config,
            'findings': [],
            'progress': 'Initializing AI agent...'
        }
        
        # В реальности здесь запускался бы Strix агент
        # Для демо добавляем фейковые результаты
        logger.info(f"✅ Scan {scan_id} created for target: {target}")
        
        return jsonify({
            'success': True,
            'scan_id': scan_id,
            'message': 'Scan started successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting scan: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan/<scan_id>', methods=['GET'])
def get_scan_status(scan_id: str):
    """Получение статуса скана"""
    if scan_id not in active_scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan_data = active_scans[scan_id].copy()
    
    # Симулируем прогресс для демо
    if scan_data['status'] == 'running':
        # Через 10 секунд помечаем как завершенный с примером находок
        started = datetime.fromisoformat(scan_data['started_at'])
        elapsed = (datetime.now() - started).total_seconds()
        
        if elapsed > 10:
            scan_data['status'] = 'completed'
            scan_data['completed_at'] = datetime.now().isoformat()
            scan_data['findings'] = [
                {
                    'severity': 'high',
                    'title': 'SQL Injection Vulnerability',
                    'description': 'Detected potential SQL injection in login form',
                    'location': '/api/login',
                    'evidence': "Parameter 'username' is vulnerable to SQL injection"
                },
                {
                    'severity': 'medium',
                    'title': 'Missing Security Headers',
                    'description': 'X-Frame-Options and CSP headers not found',
                    'location': 'All endpoints',
                    'evidence': 'Response headers analysis'
                },
                {
                    'severity': 'critical',
                    'title': 'Exposed Admin Panel',
                    'description': 'Admin panel accessible without authentication',
                    'location': '/admin',
                    'evidence': 'HTTP 200 response without credentials'
                }
            ]
            active_scans[scan_id] = scan_data
    
    return jsonify(scan_data)


@app.route('/api/scans', methods=['GET'])
def list_scans():
    """Список всех сканов"""
    scans = []
    for scan_id, scan_data in active_scans.items():
        scans.append({
            'scan_id': scan_id,
            'target': scan_data.get('target'),
            'status': scan_data.get('status'),
            'started_at': scan_data.get('started_at'),
            'completed_at': scan_data.get('completed_at'),
            'findings_count': len(scan_data.get('findings', []))
        })
    
    return jsonify({'scans': scans})


@app.route('/api/test', methods=['POST'])
def test_api():
    """Тест API соединения с Claude"""
    try:
        data = request.json
        api_base = data.get('api_base')
        api_key = data.get('api_key')
        
        if not api_base or not api_key:
            return jsonify({
                'success': False,
                'error': 'API base and key are required'
            }), 400
        
        # Конфигурируем
        configure_claude_sonnet(api_base, api_key)
        
        # Пробуем простой запрос через OpenAI SDK
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=api_key,
                base_url=api_base.rstrip('/')
            )
            
            # Простой тест запрос
            response = client.chat.completions.create(
                model='claude-sonnet-4-6',
                messages=[{'role': 'user', 'content': 'Say "OK" if you can read this'}],
                max_tokens=10,
                timeout=30
            )
            
            result = response.choices[0].message.content
            
            return jsonify({
                'success': True,
                'response': result,
                'message': 'API connection successful! Model is responding.'
            })
            
        except Exception as api_error:
            logger.error(f"API call failed: {api_error}")
            return jsonify({
                'success': False,
                'error': f'API call failed: {str(api_error)}'
            }), 500
        
    except Exception as e:
        logger.error(f"❌ API test failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check для Railway"""
    return jsonify({
        'status': 'healthy',
        'active_scans': len(active_scans),
        'model': os.getenv('STRIX_LLM', 'not configured'),
        'api_base': os.getenv('LLM_API_BASE', 'not set')
    })


if __name__ == '__main__':
    # Конфигурируем Claude при старте
    configure_claude_sonnet()
    
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 Starting Strix Web Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
