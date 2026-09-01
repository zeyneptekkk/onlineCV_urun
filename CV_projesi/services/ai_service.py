import os
import openai
from flask import current_app


class AIService:
    """OpenAI integration for CV optimization"""
    
    @staticmethod
    def initialize():
        """Initialize OpenAI client"""
        api_key = current_app.config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            return True
        return False
    
    @staticmethod
    def optimize_summary(text, tone='professional'):
        """Optimize CV summary with different tones"""
        if not text:
            return text
        
        if not AIService.initialize():
            # Fallback: return original text if API key not set
            return f"[AI unavailable] {text}"
        
        tones = {
            'professional': 'Bunu profesyonel bir CV özeti olarak yeniden yaz. Formal, akılcı ve işletme odaklı tut.',
            'technical': 'Bunu teknik ve uzman profili vurgulayan şekilde yeniden yaz. Teknik beceriler ve derinliği göster.',
            'short': 'Bunu 50-80 kelime arasında, etkileyici ve özet şekilde yeniden yaz. Hiçbir kelimeyi boşa harcama.',
            'modern': 'Bunu modern, dinamik ve girişimci tonu ile yeniden yaz. Yenilikçi ve hızlı öğrenen bir profil göster.',
        }
        
        prompt = tones.get(tone, tones['professional'])
        
        try:
            response = openai.ChatCompletion.create(
                model=current_app.config.get('OPENAI_MODEL', 'gpt-4'),
                messages=[
                    {
                        "role": "system",
                        "content": "Sen profesyonel bir CV yazarısın. Kullanıcının metinlerini geliştir, ancak orijinal anlamını koru."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nOrijinal metin:\n{text}"
                    }
                ],
                temperature=0.7,
                max_tokens=300,
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"AI Service Error: {e}")
            return f"[Hata: AI çalışmıyor] {text}"
    
    @staticmethod
    def get_available_tones():
        """Get available tone options"""
        return list(current_app.config.get('AI_TONES', {}).keys())
    
    @staticmethod
    def optimize_all_tones(text):
        """Generate optimized versions for all tones"""
        if not text:
            return {}
        
        results = {}
        for tone in AIService.get_available_tones():
            results[tone] = AIService.optimize_summary(text, tone)
        
        return results
