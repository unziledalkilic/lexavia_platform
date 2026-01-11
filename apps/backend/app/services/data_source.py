"""
Dil veri setlerinden içerik çekme servisi.
Tatoeba, OpenSubtitles, vb. kaynaklardan veri alır.
"""
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class TatoebaDataSource:
    """Tatoeba API'den çeviri cümleler çeker."""
    
    BASE_URL = "https://tatoeba.org/api/v0"
    
    async def get_sentences(
        self,
        word: str,
        from_lang: str = "eng",
        to_lang: str = "tur",
        limit: int = 5
    ) -> list[dict]:
        """
        Bir kelime için örnek cümleler getirir.
        
        Args:
            word: Aranacak kelime
            from_lang: Kaynak dil kodu (eng, tur, vb.)
            to_lang: Hedef dil kodu
            limit: Maksimum cümle sayısı
            
        Returns:
            [{"original": "...", "translation": "...", "audio_url": "..."}]
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Tatoeba API'den cümle ara
                response = await client.get(
                    f"{self.BASE_URL}/sentences/search",
                    params={
                        "query": word,
                        "from": from_lang,
                        "to": to_lang,
                        "limit": limit,
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Tatoeba API error: {response.status_code}")
                    return []
                
                data = response.json()
                sentences = []
                
                # Tatoeba response formatını parse et
                for item in data.get("results", [])[:limit]:
                    sentences.append({
                        "original": item.get("text", ""),
                        "translation": item.get("translations", [{}])[0].get("text", ""),
                        "audio_url": item.get("audio", {}).get("url") if item.get("audio") else None,
                    })
                
                return sentences
        except Exception as e:
            logger.error(f"Error fetching from Tatoeba: {e}", exc_info=True)
            return []


class OpenSubtitlesDataSource:
    """OpenSubtitles API'den gerçek kullanım örnekleri çeker."""
    
    BASE_URL = "https://api.opensubtitles.com/api/v1"
    
    async def get_examples(
        self,
        word: str,
        language: str = "en",
        limit: int = 5
    ) -> list[dict]:
        """
        Bir kelime için film/dizi altyazılarından örnekler getirir.
        
        Args:
            word: Aranacak kelime
            language: Dil kodu
            limit: Maksimum örnek sayısı
            
        Returns:
            [{"sentence": "...", "context": "...", "source": "..."}]
        """
        # OpenSubtitles API için authentication gerekli
        # Şimdilik placeholder - gerçek implementasyon için API key gerekli
        logger.info(f"OpenSubtitles search for: {word} (not implemented yet)")
        return []


class DataSourceService:
    """Tüm veri kaynaklarını yöneten ana servis."""
    
    def __init__(self):
        self.tatoeba = TatoebaDataSource()
        self.opensubtitles = OpenSubtitlesDataSource()
    
    async def get_word_examples(
        self,
        word: str,
        from_lang: str = "eng",
        to_lang: str = "tur",
        limit: int = 5
    ) -> list[dict]:
        """
        Bir kelime için tüm kaynaklardan örnekler getirir.
        
        Returns:
            [{"source": "tatoeba", "original": "...", "translation": "...", ...}]
        """
        examples = []
        
        # Tatoeba'dan çek
        tatoeba_results = await self.tatoeba.get_sentences(word, from_lang, to_lang, limit)
        for result in tatoeba_results:
            examples.append({
                "source": "tatoeba",
                **result
            })
        
        # OpenSubtitles'tan çek (gelecekte)
        # opensubtitles_results = await self.opensubtitles.get_examples(word, from_lang, limit)
        
        return examples[:limit]

