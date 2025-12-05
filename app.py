#!/usr/bin/env python3
"""
AO76 Weekly Briefing Webhook - Manus AI Integration
Triggers Manus AI to perform complete dashboard analysis and post to Notion
"""

from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
MANUS_API_KEY = os.environ.get('MANUS_API_KEY', 'sk-Apa5NF86lrjqXkf7puttAZ4796euwmzv2XtS17b0oNiPieNzluZ6dlyhexdzjog0esk7U6OKV9sXYPjuM9zoRtyFz0a_')
MANUS_API_URL = 'https://api.manus.ai/v1/tasks'

# The complete prompt for Manus
ANALYSIS_PROMPT = """Analyseer het AO76 dashboard op https://app.databox.com/datawall/f6cacd629eb4539a638d4480099e8f2c390c3f8692ef623 volgens de werkwijze in https://docs.google.com/document/d/1scmaUysEz8RCG_aBL17vEWGsEA42ovcoYbhuyXid1DM/edit?usp=sharing

Volg deze stappen:
1. Open het dashboard en verzamel alle relevante data (scroll door alle pagina's indien nodig)
2. Analyseer de data volgens de werkwijze in het Google Docs document
3. Genereer een Weekly Performance Briefing volgens de mandatory output structure

4. Vervang de BRIEFING_PLACEHOLDER in de Notion pagina https://www.notion.so/landingpartners/AO76-Weekly-performance-meetings-be479359449646ea8e4d44527d5e5159 met de nieuwe briefing.

Gebruik de notion-update-page tool via MCP met deze parameters:
- command: replace_content_range
- selection_with_ellipsis: "<!-- BRIEFING_PLACEHOLDER_START -->...<!-- BRIEFING_PLACEHOLDER_END -->"
- page_id: be479359449646ea8e4d44527d5e5159

BELANGRIJK: De nieuwe content moet beginnen met <!-- BRIEFING_PLACEHOLDER_START --> en eindigen met <!-- BRIEFING_PLACEHOLDER_END --> zodat de placeholder behouden blijft voor toekomstige updates.

Format de briefing als een toggle block met deze structuur:
▶ 📊 Week [datum] - Performance Briefing
	<callout icon="⏱️" color="gray_bg">
	**EXECUTIVE SUMMARY**
	[summary]
	</callout>
	
	[rest van de briefing met alle secties]

Belangrijke aandachtspunten:
- Gebruik de specifieke tone of voice en afkortingen (MTD, L14D, TOFU/MOFU, PC, A+camp)
- Zorg voor context bij alle cijfers (efficiency vs. volume)
- Frame aanbevelingen als suggesties, niet als orders
- Gebruik de Landing Partners communicatiestijl (direct, zelfverzekerd, strategisch)
- Gebruik callout blocks voor key insights
- Gebruik emojis en bold formatting zoals in de voorbeelden

De Notion MCP connectie is al geconfigureerd."""

def trigger_manus_task():
    """Trigger Manus AI to perform the analysis"""
    
    headers = {
        'API_KEY': MANUS_API_KEY,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'prompt': ANALYSIS_PROMPT,
        'agentProfile': 'manus-1.5',
        'hideInTaskList': False,
        'createShareableLink': False
    }
    
    try:
        print(f"🚀 Triggering Manus AI task...")
        response = requests.post(MANUS_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Manus task created: {result.get('task_id')}")
        print(f"📊 Task URL: {result.get('task_url')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error triggering Manus: {e}")
        raise

@app.route('/')
def home():
    """Home page"""
    return jsonify({
        "service": "AO76 Weekly Briefing Webhook (Manus Integration)",
        "version": "2.1",
        "status": "running",
        "description": "Triggers Manus AI to analyze AO76 dashboard and post briefing to Notion using placeholder replacement",
        "endpoints": {
            "/generate-briefing": "POST/GET - Trigger Manus AI analysis",
            "/health": "GET - Health check"
        }
    })

@app.route('/generate-briefing', methods=['GET', 'POST', 'PUT'])
def generate_briefing():
    """Trigger Manus AI to generate briefing"""
    try:
        today = datetime.now().strftime("%B %d, %Y")
        
        print(f"📝 Triggering briefing generation for {today}...")
        
        # Trigger Manus AI
        manus_result = trigger_manus_task()
        
        return jsonify({
            "success": True,
            "message": f"Manus AI task triggered for {today}",
            "manus_task_id": manus_result.get('task_id'),
            "manus_task_url": manus_result.get('task_url'),
            "timestamp": datetime.now().isoformat(),
            "note": "Manus AI is now analyzing the dashboard and will replace the BRIEFING_PLACEHOLDER in Notion. Check the task URL for progress."
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error: {e}")
        print(error_trace)
        return jsonify({
            "error": str(e),
            "trace": error_trace
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.1",
        "manus_api_configured": bool(MANUS_API_KEY),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting AO76 Briefing Webhook on port {port}")
    print(f"🤖 Manus API configured: {bool(MANUS_API_KEY)}")
    app.run(host='0.0.0.0', port=port, debug=False)

