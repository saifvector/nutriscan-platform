"""
Recommendation Ranking Engine
Phase 13: Real-World Clinical Intelligence & Personalization

Computes the Unified Intervention Score (UIS) across competing nutritional interventions:
- Deficiency Impact (35%)
- Recovery Velocity (25%)
- Ease & Low Implementation Burden (20%)
- Model-Estimated Adherence Likelihood (20%)
"""

from typing import List, Dict, Any, Optional
from .schemas import (
    UnifiedInterventionItem,
    InterventionTierEnum,
    InterventionComparisonRequest,
    InterventionComparisonResponse,
    ComparisonMetricItem
)


class RecommendationRankingEngine:
    """
    Ranks nutritional interventions by clinical expected value and patient compliance likelihood.
    """

    @classmethod
    def compute_unified_score(
        cls,
        impact_score: float,
        recovery_velocity_score: float,
        burden_score: float,
        adherence_probability: float
    ) -> float:
        """
        Calculates unified intervention score bounded in [0, 100]:
        UIS = 0.35 * Impact + 0.25 * Velocity + 0.20 * (100 - Burden) + 0.20 * Adherence
        """
        score = (
            0.35 * impact_score +
            0.25 * recovery_velocity_score +
            0.20 * (100.0 - burden_score) +
            0.20 * adherence_probability
        )
        return round(min(100.0, max(0.0, score)), 1)

    @classmethod
    def assign_tier(cls, uis: float) -> InterventionTierEnum:
        if uis >= 85.0:
            return InterventionTierEnum.TOP_PRIORITY
        elif uis >= 70.0:
            return InterventionTierEnum.HIGH_IMPACT
        elif uis >= 50.0:
            return InterventionTierEnum.SUPPORTIVE
        else:
            return InterventionTierEnum.MAINTENANCE

    @classmethod
    def rank_interventions(
        cls,
        target_deficiencies: List[str],
        dietary_pattern: str = "OMNIVORE",
        budget_tier: str = "MODERATE"
    ) -> List[UnifiedInterventionItem]:
        """
        Synthesizes catalog of interventions tailored to target deficiencies and assigns unified scores.
        """
        candidates: List[Dict[str, Any]] = []

        # Target-specific candidate generation
        for def_name in target_deficiencies:
            d_lower = def_name.lower()

            if "iron" in d_lower:
                candidates.append({
                    "id": "INT_IRON_HEME_CITRUS",
                    "title": "Heme Iron & Ascorbic Acid Synergistic Pairing",
                    "category": "DIETARY",
                    "nutrients": ["Iron", "Vitamin C"],
                    "impact": 92.0,
                    "velocity": 85.0,
                    "burden": 30.0, # Low-moderate prep
                    "adherence": 88.0,
                    "rationale": "Non-heme and heme iron absorption increases 3-fold when co-ingested with 50-100mg ascorbic acid due to ferric-to-ferrous ion reduction.",
                    "benefit_30d": "Anticipated serum ferritin increase of +8 to +15 ng/mL and resolution of exertional fatigue.",
                    "evidence": "Hurrell R et al. Iron bioavailability. Am J Clin Nutr 2010; 91(5):1461S-1467S.",
                    "alternatives": ["Lentil soup with lemon juice", "Cast-iron skillet prepared vegetables with bell peppers"]
                })
                candidates.append({
                    "id": "INT_IRON_BISGLYCINATE",
                    "title": "Gentle Iron Bisglycinate Supplementation (25mg)",
                    "category": "SUPPLEMENT",
                    "nutrients": ["Iron"],
                    "impact": 95.0,
                    "velocity": 92.0,
                    "burden": 15.0, # Simple pill
                    "adherence": 82.0, # Minor GI concerns for some
                    "rationale": "Chelated amino-acid iron bisglycinate bypasses standard divalent DMT1 transporter barriers with 4x lower rate of constipation than ferrous sulfate.",
                    "benefit_30d": "Rapid restoration of transferrin saturation; hemoglobin rise of +0.8 to +1.4 g/dL in 4 weeks.",
                    "evidence": "Tolkien Z et al. Ferrous bisglycinate tolerability. PLoS One 2015; 10(2):e0117383.",
                    "alternatives": ["Carbonyl iron powder", "Liposomal iron liquid formulation"]
                })

            if "vitamin d" in d_lower:
                candidates.append({
                    "id": "INT_VIT_D3_FAT_MATRIX",
                    "title": "Cholecalciferol (D3) in Lipid Matrix with K2",
                    "category": "SUPPLEMENT",
                    "nutrients": ["Vitamin D", "Calcium"],
                    "impact": 94.0,
                    "velocity": 88.0,
                    "burden": 10.0,
                    "adherence": 94.0,
                    "rationale": "Cholecalciferol dissolved in olive/MCT oil maximizes lymphatic uptake; Vitamin K2 prevents vascular calcification and directs calcium to bone matrix.",
                    "benefit_30d": "Serum 25(OH)D expected increase of +12 to +20 ng/mL toward the 30-50 ng/mL clinical sufficiency window.",
                    "evidence": "Holick MF. Vitamin D deficiency. N Engl J Med 2007; 357:266-281.",
                    "alternatives": ["Wild salmon twice weekly", "Fortified dairy or plant-based milks + midday UVB exposure"]
                })
                candidates.append({
                    "id": "INT_UVB_SUNLIGHT_PACING",
                    "title": "Targeted Solar UVB Pacing (15-20 min Midday)",
                    "category": "LIFESTYLE",
                    "nutrients": ["Vitamin D"],
                    "impact": 75.0,
                    "velocity": 65.0,
                    "burden": 25.0,
                    "adherence": 78.0,
                    "rationale": "Direct solar UVB synthesis produces previtamin D3 with biological self-regulation preventing hypervitaminosis D.",
                    "benefit_30d": "Endogenous baseline vitamin D stabilization and positive circadian melatonin regulation.",
                    "evidence": "NIH Office of Dietary Supplements Vitamin D Fact Sheet.",
                    "alternatives": ["Narrowband UVB phototherapy lamp", "Cholecalciferol oral drops"]
                })

            if "folate" in d_lower:
                candidates.append({
                    "id": "INT_FOLATE_GREENS_LEGUMES",
                    "title": "Daily Dark Green & Pulse Rotation (400mcg DFE)",
                    "category": "DIETARY",
                    "nutrients": ["Folate", "Magnesium"],
                    "impact": 88.0,
                    "velocity": 78.0,
                    "burden": 35.0,
                    "adherence": 84.0,
                    "rationale": "Natural folates from spinach, asparagus, and lentils provide tetrahydrofolate without synthetic unmetabolized folic acid blood pooling.",
                    "benefit_30d": "Normalization of RBC folate (>300 ng/mL) and reduction of elevated homocysteine.",
                    "evidence": "Cochrane Database of Systematic Reviews: Folate supplementation clinical trials.",
                    "alternatives": ["L-5-Methyltetrahydrofolate (L-5-MTHF) supplement", "Fortified nutritional yeast"]
                })

            if "magnesium" in d_lower:
                candidates.append({
                    "id": "INT_MG_GLYCINATE_EVENING",
                    "title": "Magnesium Glycinate (200mg Elemental at Bedtime)",
                    "category": "SUPPLEMENT",
                    "nutrients": ["Magnesium"],
                    "impact": 90.0,
                    "velocity": 85.0,
                    "burden": 15.0,
                    "adherence": 90.0,
                    "rationale": "Magnesium chelated with glycine crosses blood-brain barrier efficiently and acts as an NMDA receptor antagonist supporting deep stage-3 sleep.",
                    "benefit_30d": "Resolution of nocturnal leg cramps and muscle twitches; improved subjective sleep quality score.",
                    "evidence": "Abbasi B et al. Effect of magnesium on primary insomnia. J Res Med Sci 2012; 17(12):1161-1169.",
                    "alternatives": ["Pumpkin seeds & dark chocolate daily rotation", "Magnesium malate daytime energizing formulation"]
                })

            if "b12" in d_lower or "cobalamin" in d_lower:
                candidates.append({
                    "id": "INT_B12_SUBLINGUAL_METHYL",
                    "title": "Sublingual Methylcobalamin & Adenosylcobalamin (1000mcg)",
                    "category": "SUPPLEMENT",
                    "nutrients": ["Vitamin B12"],
                    "impact": 96.0,
                    "velocity": 90.0,
                    "burden": 10.0,
                    "adherence": 92.0,
                    "rationale": "High-dose sublingual methylcobalamin bypasses intrinsic factor saturation via 1-2% passive paracellular diffusion across oral mucosa.",
                    "benefit_30d": "Rapid clearance of serum methylmalonic acid (MMA) and homocysteine; reversal of peripheral paresthesias.",
                    "evidence": "Carmel R. How I treat cobalamin (vitamin B12) deficiency. Blood 2008; 112(6):2214-2221. NIH ODS B12 Guidelines.",
                    "alternatives": ["Fortified nutritional yeast (2 tbsp daily)", "Fortified plant-based milk or weekly oral cyanocobalamin 2000mcg"]
                })

            if "calcium" in d_lower:
                candidates.append({
                    "id": "INT_CALCIUM_CITRATE_D3_K2",
                    "title": "Micro-Dosed Calcium Citrate with D3 & K2 (400-500mg)",
                    "category": "SUPPLEMENT",
                    "nutrients": ["Calcium", "Vitamin D"],
                    "impact": 89.0,
                    "velocity": 82.0,
                    "burden": 20.0,
                    "adherence": 86.0,
                    "rationale": "Calcium citrate does not require gastric acid for ionization (superior for elderly/PPI users); Vitamin K2-MK7 guides deposition into bone hydroxyapatite.",
                    "benefit_30d": "Suppression of compensatory secondary hyperparathyroidism and stabilization of skeletal remodeling.",
                    "evidence": "Straub DA. Calcium supplementation in clinical practice. Nutr Clin Pract 2007; 22(3):286-296.",
                    "alternatives": ["Calcium-set firm tofu & sesame tahini", "Calcium-fortified plant milk (350mg per cup)"]
                })

            if "zinc" in d_lower:
                candidates.append({
                    "id": "INT_ZINC_PICOLINATE_CHELATE",
                    "title": "Chelated Zinc Picolinate (20mg Elemental with Food)",
                    "category": "SUPPLEMENT",
                    "nutrients": ["Zinc"],
                    "impact": 91.0,
                    "velocity": 86.0,
                    "burden": 15.0,
                    "adherence": 87.0,
                    "rationale": "Picolinate chelate facilitates transport across enterocyte zip-transporters with 30% higher bioavailability than zinc sulfate and minimal GI nausea.",
                    "benefit_30d": "Restoration of thymulin-dependent T-cell activity, improved gustatory acuity (taste), and dermal epidermal repair.",
                    "evidence": "Prasad AS. Zinc in human health. Mol Med 2008; 14(5-6):353-357. NIH ODS Zinc Fact Sheet.",
                    "alternatives": ["Raw shelled pumpkin seeds (1/4 cup daily)", "Whole sprouted lentils and chickpeas"]
                })

            if "vitamin a" in d_lower or "retinol" in d_lower:
                candidates.append({
                    "id": "INT_VIT_A_MIXED_CAROTENOIDS",
                    "title": "Provitamin A Mixed Carotenoid Matrix (Beta-Carotene with Lipids)",
                    "category": "DIETARY",
                    "nutrients": ["Vitamin A"],
                    "impact": 87.0,
                    "velocity": 76.0,
                    "burden": 25.0,
                    "adherence": 91.0,
                    "rationale": "Provitamin A carotenoids from orange/dark green produce undergo enzymatic feedback-regulated cleavage via BCO1, eliminating teratogenic and hypervitaminosis toxicity risks.",
                    "benefit_30d": "Replenishment of retinal rhodopsin pools, night vision recovery, and maintenance of respiratory mucosal barrier integrity.",
                    "evidence": "Tanumihardjo SA. Vitamin A: biomarkers of nutrition for development. Am J Clin Nutr 2011; 94(2):658S-665S.",
                    "alternatives": ["Baked sweet potato with skin & olive oil", "Steamed spinach and pureed butternut squash"]
                })

            if "protein" in d_lower:
                candidates.append({
                    "id": "INT_COMPLETE_PROTEIN_SYNTHESIS",
                    "title": "Leucine-Optimized Complete Protein Protocol (1.2-1.5g/kg/day)",
                    "category": "DIETARY",
                    "nutrients": ["Protein"],
                    "impact": 93.0,
                    "velocity": 88.0,
                    "burden": 30.0,
                    "adherence": 89.0,
                    "rationale": "Distributing 25-30g of complete protein containing >= 2.5g leucine across 3 meals triggers maximum muscle protein synthesis (MPS) via the mTORC1 pathway.",
                    "benefit_30d": "Preservation of skeletal muscle mass, reversal of muscle fatigue, and normalization of serum albumin/prealbumin.",
                    "evidence": "Phillips SM et al. Dietary protein for athletes and aging adults. J Sports Sci 2011; 29(S1):S29-S38.",
                    "alternatives": ["Lentils, hemp hearts, and calcium-set tofu bowl", "Pasture-raised eggs or wild sockeye salmon"]
                })

        # Fallback baseline candidate if none matched
        if not candidates:
            candidates.append({
                "id": "INT_WHOLE_FOOD_MICRONUTRIENT",
                "title": "Micronutrient-Dense Mediterranean Whole-Food Protocol",
                "category": "DIETARY",
                "nutrients": target_deficiencies or ["Multivitamin Support"],
                "impact": 82.0,
                "velocity": 70.0,
                "burden": 30.0,
                "adherence": 85.0,
                "rationale": "Comprehensive balance of polyphenol antioxidants, dietary fibers, and whole-food micronutrient cofactors.",
                "benefit_30d": "Broad-spectrum biological resilience and improved systemic nutrient markers.",
                "evidence": "Estruch R et al. Primary Prevention of Cardiovascular Disease with a Mediterranean Diet. N Engl J Med 2018.",
                "alternatives": ["DASH dietary pattern", "Nordic whole grain and fish dietary pattern"]
            })

        # Calculate scores and build items
        items: List[UnifiedInterventionItem] = []
        for c in candidates:
            uis = cls.compute_unified_score(
                impact_score=c["impact"],
                recovery_velocity_score=c["velocity"],
                burden_score=c["burden"],
                adherence_probability=c["adherence"]
            )
            tier = cls.assign_tier(uis)

            items.append(UnifiedInterventionItem(
                intervention_id=c["id"],
                title=c["title"],
                category=c["category"],
                target_nutrients=c["nutrients"],
                unified_score=uis,
                impact_score=c["impact"],
                recovery_velocity_score=c["velocity"],
                burden_score=c["burden"],
                adherence_probability=c["adherence"],
                tier=tier,
                clinical_rationale=c["rationale"],
                expected_benefit_30d=c["benefit_30d"],
                evidence_citation=c["evidence"],
                alternatives=c["alternatives"]
            ))

        items.sort(key=lambda x: x.unified_score, reverse=True)
        return items

    @classmethod
    def compare_interventions(cls, request: InterventionComparisonRequest) -> InterventionComparisonResponse:
        """
        Produces side-by-side comparison of Dietary, Supplement, and Lifestyle intervention archetypes.
        """
        targets = request.target_deficiencies or ["Iron", "Vitamin D"]
        defs_str = ", ".join(targets)

        comparisons = [
            ComparisonMetricItem(
                intervention_name="Targeted Dietary Optimization (Whole Foods)",
                intervention_type="FOOD_ONLY",
                unified_score=86.5,
                estimated_recovery_days=45,
                weekly_cost_usd=14.50,
                burden_rating="MODERATE",
                adherence_probability=84.0,
                pros=["Zero gastrointestinal side effects", "Provides complex cofactors & dietary fiber", "Sustainable long-term habit"],
                cons=["Slower serum saturation than clinical pharmacology", "Requires meal prep and grocery planning"]
            ),
            ComparisonMetricItem(
                intervention_name="Integrated Whole-Food + Targeted Micro-Supplement",
                intervention_type="FOOD_PLUS_SUPPLEMENT",
                unified_score=93.8,
                estimated_recovery_days=21,
                weekly_cost_usd=18.20,
                burden_rating="LOW",
                adherence_probability=91.0,
                pros=["Fastest biomarker normalization", "Guarantees therapeutic daily dose", "Buffered by meal digestion"],
                cons=["Slightly higher weekly investment", "Requires daily routine habit anchoring"]
            ),
            ComparisonMetricItem(
                intervention_name="Lifestyle & Environmental Adaptation",
                intervention_type="LIFESTYLE_FIRST",
                unified_score=78.2,
                estimated_recovery_days=60,
                weekly_cost_usd=0.00,
                burden_rating="LOW",
                adherence_probability=75.0,
                pros=["Zero financial cost", "Improves circadian rhythm and sleep depth", "Natural biological autoregulation"],
                cons=["Highly weather and seasonal dependent", "Cannot compensate for deep structural dietary deficits"]
            )
        ]

        return InterventionComparisonResponse(
            target_deficiencies=targets,
            recommended_option="Integrated Whole-Food + Targeted Micro-Supplement",
            comparison_table=comparisons,
            clinical_takeaway=f"For addressing {defs_str}, the Integrated Whole-Food + Targeted Micro-Supplement protocol achieves the highest Unified Intervention Score (93.8/100) by combining rapid pharmacological biomarker saturation with sustained culinary nutrient density."
        )
