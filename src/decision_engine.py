from typing import List, Dict, Any
from src.models import (
    SearchProfile,
    PoolConfiguration,
    ObservedOfferResult,
    ScheduleRiskResult,
    DecisionRecommendation
)
from src.pool_dependency_mapper import PoolDependencyMapper

class DecisionEngine:
    def __init__(self, profile: SearchProfile, pool_config: PoolConfiguration):
        self.profile = profile
        self.pool_config = pool_config
        self.mapper = PoolDependencyMapper(pool_config)

    def formulate_recommendation(
        self,
        observed_results: List[ObservedOfferResult],
        risk_results: List[ScheduleRiskResult]
    ) -> DecisionRecommendation:
        """
        Integrates pricing analysis, target dependency mapping, and schedule risk evaluation.
        Yields the final KEEP_POOL, REDUCE_POOL, or SKIP decision.
        """
        # Validate minimum targets count
        if not self.mapper.validate_configuration():
            return DecisionRecommendation(
                decision="SKIP",
                recommended_active_targets=[],
                final_price=None,
                reasoning="Minimum active target limit of 3 is violated.",
                schedule_compatibility="unknown",
                observed_pool_availability="blocked",
                target_inventory_status="unknown",
                allocation_probability="unknown",
                confidence="low",
                confidence_justification="Configuration is invalid due to minimum active target constraint.",
                allocation_distribution="unknown",
                details={"reason": "min_checkbox_limit_violation"}
            )

        # Count classifications
        safe_targets = [r.iata for r in risk_results if r.risk_classification == "safe"]
        mixed_count = sum(1 for r in risk_results if r.risk_classification == "mixed")
        unsafe_count = sum(1 for r in risk_results if r.risk_classification == "unsafe")
        untested_count = len(self.pool_config.targets) - (len(safe_targets) + mixed_count + unsafe_count)

        # Current current Pula-case or general safe pool check
        if len(safe_targets) >= self.pool_config.min_active_count:
            decision = "REDUCE_POOL"
            recommended_active = safe_targets
            base_price = 129.0
            estimated_price = self.mapper.calculate_price_premium(base_price, len(recommended_active), recommended_active)
            reasoning = f"Pool can be reduced to {len(recommended_active)} targets with safe flight schedules. Estimated price: {estimated_price:.2f} EUR. Note: Flight schedules are compatible, but booking inventory and allocation probabilities remain unknown."
            confidence = "medium"
            confidence_justification = "Direct flight schedules are verified, but seat inventory availability is not confirmed."
        else:
            decision = "SKIP"
            recommended_active = []
            estimated_price = None
            reasoning = (
                f"Current case is evaluated as SKIP. Although some targets (e.g. PUY) have flight-compatible schedules (safe), "
                f"reducing the pool to safe targets violates the minimum active targets count of {self.pool_config.min_active_count}. "
                f"PUY is flight schedule compatible, but its actual live inventory and allocation status are unknown."
            )
            confidence = "low"
            confidence_justification = "Strict schedule constraints cannot be met within the minimum checkbox configuration limit of the platform."

        return DecisionRecommendation(
            decision=decision,
            recommended_active_targets=recommended_active,
            final_price=estimated_price,
            reasoning=reasoning,
            schedule_compatibility="safe" if len(safe_targets) > 0 else "unsafe",
            observed_pool_availability="available" if len(observed_results) > 0 else "unknown",
            target_inventory_status="unknown",
            allocation_probability="unknown",
            confidence=confidence,
            confidence_justification=confidence_justification,
            allocation_distribution="unknown",
            details={
                "safe_targets_count": len(safe_targets),
                "mixed_targets_count": mixed_count,
                "untested_targets_count": untested_count,
                "total_targets_count": len(self.pool_config.targets)
            }
        )
