import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

from nlp_layer import GeminiInferenceServer

class SourceIntelligenceTracker:
    """Manages tracking, caching, and scraping domain reputation data."""
    
    def __init__(self):
        # In-Memory Cache maps domain (str) -> dict of intel
        self._cache = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.llm_fallback = GeminiInferenceServer()

    def _extract_domain(self, url: str) -> str:
        """Parses URL down to the core domain (e.g. edition.cnn.com -> cnn.com)."""
        if not url or url.lower() == "raw_text":
            return "unknown"
            
        try:
            domain = urllib.parse.urlparse(url).netloc
            domain = domain.lower().replace("www.", "")
            # Basic reduction to second-level domain
            parts = domain.split(".")
            if len(parts) > 2:
                # E.g. news.yahoo.com -> yahoo.com
                domain = f"{parts[-2]}.{parts[-1]}"
            return domain
        except Exception:
            return "unknown"

    def _scrape_mbfc(self, domain: str) -> Dict[str, str]:
        """Attempt to grab MediaBiasFactCheck ratings via generic search."""
        search_url = f"https://mediabiasfactcheck.com/?s={domain}"
        
        try:
            resp = requests.get(search_url, headers=self.headers, timeout=5)
            if resp.status_code != 200:
                return {}
                
            soup = BeautifulSoup(resp.text, "html.parser")
            # MBFC places search results in <article> tags, usually.
            # We're making a "best-effort" lightweight search here.
            articles = soup.find_all("article")
            if not articles:
                return {}
                
            first_result_url = articles[0].find("a")["href"]
            
            # Fetch the actual profile page
            profile_resp = requests.get(first_result_url, headers=self.headers, timeout=5)
            if profile_resp.status_code != 200:
                return {}
                
            prof_soup = BeautifulSoup(profile_resp.text, "html.parser")
            
            # MBFC usually puts "Bias Rating: LEFT" or "Factual Reporting: HIGH" in bold <p> or <span>
            text_content = prof_soup.get_text()
            
            # Extract via simple string search
            bias = "Unknown"
            reliability = "Unknown"
            
            if "Bias Rating:" in text_content:
                idx = text_content.find("Bias Rating:")
                end_idx = text_content.find("\n", idx)
                bias = text_content[idx:end_idx].replace("Bias Rating:", "").strip()
                
            if "Factual Reporting:" in text_content:
                idx = text_content.find("Factual Reporting:")
                end_idx = text_content.find("\n", idx)
                reliability = text_content[idx:end_idx].replace("Factual Reporting:", "").strip()
                
            if bias != "Unknown" or reliability != "Unknown":
                return {
                    "source": "MediaBiasFactCheck",
                    "bias": bias,
                    "reliability": reliability
                }
                
            return {}
        except Exception:
            return {}

    def _scrape_allsides(self, domain: str) -> Dict[str, str]:
        """Attempt to use AllSides generic text search."""
        search_url = f"https://www.allsides.com/media-bias/ratings?search={domain}"
        try:
            resp = requests.get(search_url, headers=self.headers, timeout=5)
            if resp.status_code != 200:
                return {}
                
            soup = BeautifulSoup(resp.text, "html.parser")
            # Usually rows in the table denote results
            table = soup.find("table")
            if not table:
                return {}
                
            rows = table.find_all("tr")
            if len(rows) < 2:
                return {} # only header
                
            # First real row
            cols = rows[1].find_all("td")
            if len(cols) >= 3:
                bias_img = cols[2].find("img")
                if bias_img and "alt" in bias_img.attrs:
                    return {
                        "source": "AllSides",
                        "bias": bias_img["alt"]
                    }
                    
            return {}
        except Exception:
            return {}

    def _get_gemini_fallback(self, domain: str) -> Dict[str, Any]:
        """Uses LLM to summarize obscure domains when scraping fails."""
        if not self.llm_fallback.client:
            return {"error": "LLM client unavailable for fallback"}
            
        prompt = f"""
        Provide a very brief (2-sentence) summary of the journalistic reputation, known political bias,
        and factual credibility of the news domain: "{domain}". 
        If you have absolutely no data, just say "No established data available."
        """
        
        try:
            from google.genai import types
            response = self.llm_fallback.client.models.generate_content(
                model=self.llm_fallback.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            return {
                "source": "Gemini Fallback (Inferred)",
                "confidence": "Low",
                "summary": response.text.strip()
            }
        except Exception as e:
            return {"error": str(e)}

    def get_domain_info(self, url: str) -> Dict[str, Any]:
        """Main routing method. Checks cache, triggers scrapers, handles fallbacks."""
        domain = self._extract_domain(url)
        
        if domain == "unknown":
            return {"domain": "unknown", "status": "no_url_provided"}
            
        # 1. In-Memory Cache Check
        if domain in self._cache:
            cache_result = self._cache[domain].copy()
            cache_result["_cache_hit"] = True 
            return cache_result
            
        print(f"[SourceIntelligenceTracker] Cache miss for '{domain}'. Evaluating...")
        
        # 2. Live Scrape
        result = {}
        mbfc_data = self._scrape_mbfc(domain)
        allsides_data = self._scrape_allsides(domain)
        
        if mbfc_data:
            result["mbfc_rating"] = mbfc_data
        if allsides_data:
            result["allsides_rating"] = allsides_data
            
        # 3. LLM Fallback (if both scrapers failed / returned empty)
        if not mbfc_data and not allsides_data:
            print(f"[SourceIntelligenceTracker] Live Scrapers returned NO DATA for '{domain}'. Using Gemini Fallback...")
            fallback_data = self._get_gemini_fallback(domain)
            result["llm_fallback_assessment"] = fallback_data
            
        result["domain_evaluated"] = domain
        
        # Update Cache
        self._cache[domain] = result
        
        # Return a copy to avoid external mutation
        ret = result.copy()
        ret["_cache_hit"] = False
        return ret
