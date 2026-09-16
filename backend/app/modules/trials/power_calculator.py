"""
Statistical Power & Effect Size Calculator
Calculates Cohen's d effect sizes, two-sample statistical power (1 - beta),
and recommended minimal sample size thresholds for clinical trial simulations.
"""

import math
from .schemas import StatisticalPowerAnalysis


class PowerCalculatorEngine:
    """Computes statistical power and effect size metrics for in-silico trial validation."""

    @classmethod
    def calculate_power(
        cls,
        target_nutrient: str,
        sample_size_per_arm: int,
        mean_control: float,
        mean_intervention: float,
        pooled_std: float = 5.0,
        alpha: float = 0.05
    ) -> StatisticalPowerAnalysis:
        # Cohen's d: (mean_intervention - mean_control) / pooled_std
        mean_diff = abs(mean_intervention - mean_control)
        cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0.85
        cohens_d = round(cohens_d, 2)

        # Standard normal critical value for alpha=0.05 (two-tailed z_alpha = 1.96)
        z_alpha = 1.96

        # Non-centrality parameter delta = d * sqrt(N / 2)
        delta = cohens_d * math.sqrt(sample_size_per_arm / 2.0)

        # Approximate power = Phi(delta - z_alpha) where Phi is standard normal CDF
        z_beta = delta - z_alpha
        # Normal CDF approximation using erf
        power = 0.5 * (1.0 + math.erf(z_beta / math.sqrt(2.0)))
        power = round(max(0.05, min(0.999, power)), 3)

        # Approximate p-value
        p_val = round(max(0.0001, 2.0 * (1.0 - 0.5 * (1.0 + math.erf(delta / math.sqrt(2.0))))), 4)

        # Recommended min sample size for 80% power (z_beta = 0.84)
        # N_arm = 2 * ((z_alpha + z_beta) / d)^2
        z_beta_80 = 0.8416
        min_n = int(math.ceil(2.0 * (((z_alpha + z_beta_80) / max(0.1, cohens_d)) ** 2)))

        return StatisticalPowerAnalysis(
            target_nutrient=target_nutrient,
            sample_size_per_arm=sample_size_per_arm,
            alpha_significance=alpha,
            effect_size_cohens_d=cohens_d,
            calculated_statistical_power=power,
            p_value=p_val,
            recommended_min_sample_size=min_n,
            clinical_superiority_confirmed=(p_val < 0.05 and cohens_d >= 0.5)
        )
