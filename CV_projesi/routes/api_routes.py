from flask import request, jsonify, session
from models import User
from middleware import api_subscription_required
from services import AIService
from .blueprints import api_bp


@api_bp.route('/optimize', methods=['POST'])
@api_subscription_required
def optimize_summary():
    """AI-powered text optimization endpoint"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'success': False, 'error': 'Text gerekli.'}), 400
    
    text = data.get('text', '').strip()
    tone = data.get('tone', 'professional')
    
    if not text:
        return jsonify({'success': False, 'error': 'Text boş olamaz.'}), 400
    
    if tone not in ['professional', 'technical', 'short', 'modern']:
        return jsonify({'success': False, 'error': 'Geçersiz tone.'}), 400
    
    try:
        optimized = AIService.optimize_summary(text, tone)
        
        return jsonify({
            'success': True,
            'original': text,
            'optimized': optimized,
            'tone': tone
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'AI hata: {str(e)}'
        }), 500


@api_bp.route('/optimize-all', methods=['POST'])
@api_subscription_required
def optimize_all_tones():
    """Generate optimized versions for all tones"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'success': False, 'error': 'Text gerekli.'}), 400
    
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'success': False, 'error': 'Text boş olamaz.'}), 400
    
    try:
        results = AIService.optimize_all_tones(text)
        
        return jsonify({
            'success': True,
            'original': text,
            'versions': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'AI hata: {str(e)}'
        }), 500


@api_bp.route('/tones', methods=['GET'])
def get_tones():
    """Get available AI tones"""
    tones = AIService.get_available_tones()
    return jsonify({
        'success': True,
        'tones': tones
    })
