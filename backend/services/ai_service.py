"""
AI/LLM service for parlay generation and analysis
"""
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from openai import OpenAI
from config.settings import EMERGENT_LLM_KEY

logger = logging.getLogger(__name__)


def get_openai_client() -> Optional[OpenAI]:
    """Get OpenAI client with Emergent LLM key"""
    if not EMERGENT_LLM_KEY:
        return None
    return OpenAI(
        api_key=EMERGENT_LLM_KEY,
        base_url="https://api.emergentmethods.ai/v1"
    )


async def generate_parlay_with_ai(
    matches: List[Dict],
    num_selections: int = 3,
    risk_level: str = "medium",
    sports_filter: Optional[List[str]] = None
) -> Optional[Dict]:
    """Generate a parlay using AI analysis"""
    client = get_openai_client()
    if not client:
        logger.warning("OpenAI client not available")
        return None
    
    # Filter matches if needed
    if sports_filter:
        matches = [m for m in matches if m.get("sport") in sports_filter]
    
    if len(matches) < num_selections:
        return None
    
    # Prepare match data for AI
    matches_info = []
    for m in matches[:30]:  # Limit for token optimization
        odds_summary = {}
        if m.get("odds"):
            for bookie, odds in list(m["odds"].items())[:3]:
                odds_summary[bookie] = odds
        
        matches_info.append({
            "id": m["id"],
            "match": f"{m['home_team']} vs {m['away_team']}",
            "league": m["league"],
            "sport": m.get("sport", "football"),
            "start_time": m["start_time"],
            "odds": odds_summary
        })
    
    risk_descriptions = {
        "low": "favoritos claros con alta probabilidad de ganar, cuotas bajas",
        "medium": "balance entre valor y seguridad, cuotas moderadas",
        "high": "apuestas de mayor riesgo con cuotas altas y gran potencial"
    }
    
    prompt = f"""Eres un experto analista de apuestas deportivas. Analiza los siguientes partidos y selecciona {num_selections} apuestas para una combinada con nivel de riesgo "{risk_level}" ({risk_descriptions.get(risk_level, 'moderado')}).

PARTIDOS DISPONIBLES:
{json.dumps(matches_info, indent=2, ensure_ascii=False)}

Responde SOLO con un JSON válido con esta estructura:
{{
    "selections": [
        {{
            "match_id": "id_del_partido",
            "match": "Equipo1 vs Equipo2",
            "league": "Liga",
            "selection": "Equipo ganador o resultado",
            "market": "home/away/draw",
            "odds": 1.85,
            "confidence": 75,
            "reasoning": "Breve análisis de por qué esta selección"
        }}
    ],
    "total_odds": 5.67,
    "win_probability": 45,
    "risk_assessment": "Análisis breve del riesgo de la combinada",
    "recommendation": "Recomendación final"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un analista experto en apuestas deportivas. Responde solo con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        
        # Clean JSON response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        result = json.loads(content.strip())
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing AI response: {e}")
        return None
    except Exception as e:
        logger.error(f"Error generating parlay with AI: {e}")
        return None


async def analyze_match_with_ai(match: Dict) -> Optional[str]:
    """Get AI analysis for a specific match"""
    client = get_openai_client()
    if not client:
        return None
    
    prompt = f"""Analiza este partido de apuestas:

{match['home_team']} vs {match['away_team']}
Liga: {match['league']}
Cuotas disponibles: {json.dumps(match.get('odds', {}), indent=2)}

Proporciona un análisis breve (2-3 párrafos) sobre:
1. Probabilidades implícitas
2. Posible valor en las cuotas
3. Factores a considerar"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un analista experto en apuestas deportivas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error analyzing match with AI: {e}")
        return None
