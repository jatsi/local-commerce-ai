from __future__ import annotations

from collections import Counter
from statistics import mean


class CompetitorAnalyzer:
    """Analiza snapshots de competencia y propone mejoras de contenido.

    Las reglas son heurísticas sencillas para que el agente funcione en local
    sin depender de modelos remotos.
    """

    STOPWORDS = {
        "the",
        "and",
        "for",
        "with",
        "your",
        "from",
        "this",
        "that",
        "tracker",
        "trackers",
        "para",
        "con",
        "por",
        "de",
        "el",
        "la",
        "los",
        "las",
        "un",
        "una",
        "y",
    }

    def analyze(self, snapshots: list[dict], own_product: dict | None = None) -> dict:
        clean_snapshots = [s for s in snapshots if s.get("status") == "scraped" and s.get("title")]
        prices = [float(s["price"]) for s in clean_snapshots if self._is_number(s.get("price"))]
        all_keywords = self._extract_keywords([s.get("title", "") for s in clean_snapshots])

        most_common_keywords = [k for k, _ in Counter(all_keywords).most_common(8)]
        avg_price = round(mean(prices), 2) if prices else None

        recommendations = self._build_recommendations(
            own_title=(own_product or {}).get("title", ""),
            avg_competitor_price=avg_price,
            top_keywords=most_common_keywords,
            own_price=(own_product or {}).get("price"),
        )

        return {
            "competitors_count": len(clean_snapshots),
            "average_price": avg_price,
            "top_keywords": most_common_keywords,
            "recommendations": recommendations,
        }

    def _extract_keywords(self, titles: list[str]) -> list[str]:
        tokens: list[str] = []
        for title in titles:
            for raw in title.lower().replace("-", " ").split():
                token = "".join(ch for ch in raw if ch.isalnum())
                if len(token) >= 4 and token not in self.STOPWORDS:
                    tokens.append(token)
        return tokens

    def _build_recommendations(
        self,
        own_title: str,
        avg_competitor_price: float | None,
        top_keywords: list[str],
        own_price: float | None,
    ) -> list[str]:
        recs: list[str] = []
        own_title_lower = own_title.lower()

        missing_keywords = [kw for kw in top_keywords[:5] if kw not in own_title_lower]
        if missing_keywords:
            recs.append(
                f"Añadir keywords competitivas al título/descripción: {', '.join(missing_keywords[:3])}."
            )

        if self._is_number(own_price) and avg_competitor_price is not None:
            own_price_float = float(own_price)
            if own_price_float > avg_competitor_price * 1.1:
                recs.append(
                    "Precio por encima del mercado (>10%). Considerar reforzar propuesta de valor o ajustar precio."
                )
            elif own_price_float < avg_competitor_price * 0.9:
                recs.append(
                    "Precio por debajo del mercado (<10%). Evaluar subida controlada para capturar margen."
                )

        if not recs:
            recs.append("Mantener estructura actual y ejecutar test A/B con bullets y primer párrafo.")

        return recs

    @staticmethod
    def _is_number(value: object) -> bool:
        try:
            float(value)
        except (TypeError, ValueError):
            return False
        return True
