import os
import json
from typing import List, Dict, Any
from src.models import PoolConfiguration, ObservedOfferResult

class PoolDependencyMapper:
    def __init__(self, config: PoolConfiguration, research_data_dir: str = "research_data/lufthansa_surprise"):
        self.config = config
        self.research_data_dir = research_data_dir
        self.pricing_data = self._load_research_pricing_data()

    def _load_research_pricing_data(self) -> List[Dict[str, Any]]:
        data = []
        if os.path.exists(self.research_data_dir):
            try:
                for file in os.listdir(self.research_data_dir):
                    if file.endswith(".json"):
                        filepath = os.path.join(self.research_data_dir, file)
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = json.load(f)
                            if isinstance(content, list):
                                data.extend(content)
            except Exception:
                pass
        return data

    def validate_configuration(self) -> bool:
        """Verifies if the active target count matches the minimum requirements."""
        return len(self.config.active_targets) >= self.config.min_active_count

    def calculate_price_premium(self, base_price: float, active_count: int, active_targets: List[str] = None) -> float:
        """
        Calculates the expected premium based on the number of active checkboxes and pool composition.
        Tries to match configured active targets against recorded research fixtures.
        """
        if active_targets is None:
            active_targets = self.config.active_targets

        targets_set = set(active_targets)
        
        # Try to find an exact match in the research pricing data
        for entry in self.pricing_data:
            entry_active = set(entry.get("active_destinations", []))
            if targets_set == entry_active:
                return entry.get("price_eur", base_price)
                
        # Fallback approximation:
        difference = len(self.config.targets) - len(targets_set)
        # Note: The pricing model is NOT linear. This is a rough estimation for fallback purposes.
        return base_price + (difference * 9.58)

    def analyze_dependency(self, results: List[ObservedOfferResult]) -> Dict[str, Any]:
        """Maps target dependency based on observed differential tests."""
        # Find necessary triggers
        # An inactive target is a trigger if its absence changes the status to unavailable
        triggers = []
        for res in results:
            if res.status == "unavailable" and len(res.active_targets) < len(self.config.targets):
                # The target that was deactivated is a trigger
                deactivated = set(self.config.targets) - set(res.active_targets)
                triggers.extend(list(deactivated))
        return {
            "necessary_observed_triggers": list(set(triggers)),
            "min_checkbox_rule_valid": self.validate_configuration()
        }
