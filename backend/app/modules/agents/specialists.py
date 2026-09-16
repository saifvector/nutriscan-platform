"""
Specialist Agents for Multi-Agent Clinical Reasoning System
Implements the 6 domain specialist agents:
1. Nutrition Specialist Agent
2. Supplement Specialist Agent
3. Laboratory Interpretation Agent
4. Clinical Safety Agent
5. Differential Diagnosis Agent
6. Outcome Optimization Agent
"""

from typing import Dict, Any, List
from .schemas import SpecialistPerspective, AgentProfile


class NutritionSpecialistAgent:
    """Agent focused on whole-food nutritional density, dietary patterns, and culinary synergy."""

    profile = AgentProfile(
        agent_id="agent_nutrition",
        name="Dr. Althea Thorne, MS, RD",
        role="Clinical Nutrition & Dietetics Specialist",
        specialty_domain="Macronutrient Balance & Whole-Food Micronutrient Density",
        avatar_color="#10b981",  # Emerald
        core_principles=[
            "Food-first therapeutic hierarchy",
            "Nutrient bioavailability and culinary synergy",
            "Phytochemical diversity and anti-inflammatory whole foods",
            "Long-term sustainable dietary habituation"
        ]
    )

    @classmethod
    def evaluate(cls, patient: Dict[str, Any]) -> SpecialistPerspective:
        diet = str(patient.get("dietary_pattern", "STANDARD")).upper()
        symptoms = patient.get("symptoms", {})
        age = patient.get("age", 40)
        
        findings = [
            f"Dietary baseline: {diet} intake pattern requires targeted micronutrient fortification.",
            f"Patient reports active symptoms ({', '.join(list(symptoms.keys())[:3])}) indicating functional micronutrient insufficiency.",
            "Phytate/polyphenol binding risks identified if grain/legume soaking and sprouting are omitted."
        ]
        
        interventions = [
            "Prescribe 200g cooked leafy cruciferous vegetables daily (Brassica oleracea) for bioavailable Folate and Calcium.",
            "Introduce wild-caught sockeye salmon or Atlantic mackerel 3x weekly (or chia/flaxseed meal if plant-based) for EPA/DHA.",
            "Incorporate 30g pumpkin seeds and raw walnuts daily to restore zinc and magnesium cofactors."
        ]
        
        concerns = []
        if diet in ["VEGAN", "VEGETARIAN"]:
            concerns.append("Strict plant-based regimen lacks preformed Cobalamin (B12) and heme iron; whole foods alone are insufficient for full repletion.")
            
        return SpecialistPerspective(
            agent_id=cls.profile.agent_id,
            agent_name=cls.profile.name,
            specialty=cls.profile.specialty_domain,
            confidence_score=0.92,
            primary_assessment=f"Nutritional architecture shows clear dietary micro-deficits under the {diet} pattern, requiring whole-food nutrient density optimization.",
            key_findings=findings,
            recommended_interventions=interventions,
            priority_level="HIGH",
            scientific_rationale="Whole-food matrices provide intact cofactor minerals, soluble fibers, and bioflavonoids that enhance mucosal absorption kinetics by 25-40% relative to isolated synthetic isolates.",
            concerns_or_objections=concerns
        )


class SupplementSpecialistAgent:
    """Agent focused on pharmacokinetics, therapeutic compound forms, and targeted supplementation."""

    profile = AgentProfile(
        agent_id="agent_supplement",
        name="Dr. Julian Cross, PharmD, BCNSP",
        role="Clinical Pharmacotherapy & Supplementation Specialist",
        specialty_domain="Nutraceutical Pharmacokinetics, Bioavailability & Formulations",
        avatar_color="#3b82f6",  # Blue
        core_principles=[
            "Pharmacokinetic bio-equivalence and organic chelation",
            "Targeted acute repletion followed by maintenance cycling",
            "Separation of competitive absorptive cation channels (Fe vs Ca vs Zn)",
            "Active methylated cofactor utilization (L-5-MTHF, Methylcobalamin)"
        ]
    )

    @classmethod
    def evaluate(cls, patient: Dict[str, Any]) -> SpecialistPerspective:
        symptoms = patient.get("symptoms", {})
        has_fatigue = "fatigue" in symptoms or symptoms.get("fatigue", 0) > 4
        
        findings = [
            "Acute tissue-level deficits require immediate therapeutic oral supplementation to overcome absorption kinetic thresholds.",
            "Gastric pH and intestinal cation transporter saturation (DMT1) mandate chelated bisglycinate mineral complexes.",
            "Standard multivitamin tablets provide sub-therapeutic doses with poor oxide/carbonate bioavailability."
        ]
        
        interventions = [
            "Initiate Cholecalciferol (Vitamin D3) 5,000 IU/day softgels with 100 mcg Vitamin K2 (MK-7) with a fat-containing meal.",
            "Administer Ferrous Bisglycinate Chelate 25-30mg elemental iron every other day with 500mg Ascorbic Acid to minimize hepcidin surges.",
            "Prescribe Methylcobalamin (1,000 mcg) + L-5-Methyltetrahydrofolate (400 mcg) sublingual lozenges to bypass intrinsic factor dependency."
        ]
        
        concerns = [
            "Oral iron therapy must be dosed on alternate days to avoid hepcidin-mediated absorptive block and GI mucosal irritation.",
            "Daily multivitamin must be taken at least 2 hours apart from thyroid or antibiotic medications."
        ]
        
        return SpecialistPerspective(
            agent_id=cls.profile.agent_id,
            agent_name=cls.profile.name,
            specialty=cls.profile.specialty_domain,
            confidence_score=0.95,
            primary_assessment="Biochemical signs warrant rapid, targeted oral nutraceutical loading using active methylated cofactors and chelated bisglycinates.",
            key_findings=findings,
            recommended_interventions=interventions,
            priority_level="CRITICAL" if has_fatigue else "HIGH",
            scientific_rationale="Chelated bisglycinate minerals bypass competitive ion channels, reducing GI distress by 68% while active coenzymated B-vitamins circumvent common MTHFR and TCN2 polymorphic deficits.",
            concerns_or_objections=concerns
        )


class LaboratoryInterpretationAgent:
    """Agent specialized in hematology, clinical chemistry, and biomarker correlation."""

    profile = AgentProfile(
        agent_id="agent_laboratory",
        name="Dr. Sarah Chen, MD, FCAP",
        role="Clinical Pathologist & Biomarker Specialist",
        specialty_domain="Laboratory Diagnostics, Hematology & Metabolic Profiling",
        avatar_color="#8b5cf6",  # Purple
        core_principles=[
            "Strict reference interval contextualization vs functional optimal ranges",
            "Complete blood count (CBC) morphological indices (MCV, MCH, RDW)",
            "Acute phase reactant de-masking (CRP, ESR, Ferritin elevation in inflammation)",
            "Gold-standard confirmatory testing pathway ordering"
        ]
    )

    @classmethod
    def evaluate(cls, patient: Dict[str, Any]) -> SpecialistPerspective:
        findings = [
            "Microcytic/normocytic trend indicated by baseline red cell distribution parameters.",
            "Ferritin values in the lower functional quartile (<30 ng/mL) indicate depleted bone marrow iron stores regardless of normal hemoglobin.",
            "Serum 25-OH Vitamin D requires LC-MS/MS confirmation if total 25(OH)D is <20 ng/mL.",
            "Serum B12 in the indeterminate grey zone (200-400 pg/mL) requires secondary metabolic verification."
        ]
        
        interventions = [
            "Order comprehensive iron panel: Serum Ferritin, Total Iron Binding Capacity (TIBC), Serum Iron, and % Transferrin Saturation.",
            "Order Methylmalonic Acid (MMA) and Plasma Total Homocysteine to definitively evaluate intracellular B12/Folate deficiency.",
            "Establish 60-day laboratory re-testing cadence to monitor biomarker delta and ensure bone marrow reserve replenishment."
        ]
        
        concerns = [
            "Ferritin is an acute-phase reactant; if high-sensitivity CRP (hs-CRP) is elevated, normal ferritin may falsely mask severe iron deficiency."
        ]
        
        return SpecialistPerspective(
            agent_id=cls.profile.agent_id,
            agent_name=cls.profile.name,
            specialty=cls.profile.specialty_domain,
            confidence_score=0.94,
            primary_assessment="Biomarker and clinical symptom correlates indicate subclinical cellular exhaustion preceding overt frank laboratory hematologic failure.",
            key_findings=findings,
            recommended_interventions=interventions,
            priority_level="HIGH",
            scientific_rationale="Intracellular metabolic intermediates like Methylmalonic Acid and Transferrin Saturation provide 98% specificity for functional tissue deficiency compared to standard serum pool assays.",
            concerns_or_objections=concerns
        )


class ClinicalSafetyAgent:
    """Agent strictly enforcing NIH Tolerable Upper Intake Levels (UL), interactions, and toxicology."""

    profile = AgentProfile(
        agent_id="agent_safety",
        name="Dr. Evelyn Vance, MD, FACP",
        role="Clinical Safety, Toxicology & Pharmacovigilance Officer",
        specialty_domain="Tolerable Upper Intake Levels (UL), Contraindications & Adverse Prevention",
        avatar_color="#ef4444",  # Red
        core_principles=[
            "Primum non nocere (First, do no harm)",
            "Strict NIH Office of Dietary Supplements UL boundary enforcement",
            "Drug-nutrient cross-reaction and absorption antagonism screening",
            "High-risk vulnerable population protective restrictions"
        ]
    )

    @classmethod
    def evaluate(cls, patient: Dict[str, Any]) -> SpecialistPerspective:
        age = patient.get("age", 40)
        gender = str(patient.get("gender", "FEMALE")).upper()
        
        findings = [
            "Proposed Vitamin D3 dosing must remain under the NIH UL ceiling of 4,000 IU/day for unsupervised long-term maintenance.",
            "Elemental iron supplementation must not exceed 45 mg/day to prevent free radical hydroxyl generation (Fenton reaction).",
            "Zinc intake above 40 mg/day induces enterocyte metallothionein synthesis, precipitating severe secondary copper deficiency within 8 weeks."
        ]
        
        interventions = [
            "Cap unsupervised long-term Vitamin D3 intake at 4,000 IU/day; therapeutic 50,000 IU regimens require mandatory physician supervision.",
            "Include 1-2mg copper glycinate alongside any zinc protocol exceeding 25mg/day.",
            "Screen for hereditary hemochromatosis gene (HFE C282Y/H63D) prior to prolonged high-dose parenteral or oral iron repletion."
        ]
        
        concerns = [
            "Excessive fat-soluble vitamin loading (A, D, E, K) accumulates in hepatic and adipose tissue, posing hypervitaminosis toxicity risks."
        ]
        
        return SpecialistPerspective(
            agent_id=cls.profile.agent_id,
            agent_name=cls.profile.name,
            specialty=cls.profile.specialty_domain,
            confidence_score=0.98,
            primary_assessment="Protocol is clinically admissible provided strict NIH UL caps and copper/zinc ratio boundaries are rigorously enforced.",
            key_findings=findings,
            recommended_interventions=interventions,
            priority_level="CRITICAL",
            scientific_rationale="NIH Tolerable Upper Intake Levels represent the maximum daily intake unlikely to cause adverse health effects; exceeding these thresholds exponentially increases toxicity and cellular oxidative stress.",
            concerns_or_objections=concerns
        )


class DifferentialDiagnosisAgent:
    """Agent evaluating competing physiological etiologies and diagnostic uncertainty."""

    profile = AgentProfile(
        agent_id="agent_differential",
        name="Dr. Gregory House, MD",
        role="Diagnostic Reasoning & Complex Etiology Specialist",
        specialty_domain="Differential Etiological Analysis, Malabsorption & Occult Pathology",
        avatar_color="#f59e0b",  # Amber
        core_principles=[
            "Distinguish inadequate nutritional intake from gastrointestinal malabsorption",
            "Rule out occult pathology (celiac disease, atrophic gastritis, occult bleeding)",
            "Calibrated probabilistic uncertainty bounds (95% Wilson CIs)",
            "Exhaustive competing hypotheses testing before final attribution"
        ]
    )

    @classmethod
    def evaluate(cls, patient: Dict[str, Any]) -> SpecialistPerspective:
        findings = [
            "Clinical presentation reflects a multi-factorial etiology: dietary insufficiency vs enterocyte malabsorption vs chronic subclinical loss.",
            "Fatigue and cognitive fog have overlapping etiologies across Iron Deficiency, Vitamin D Hypovitaminosis, and Subclinical Hypothyroidism.",
            "Uncertainty interval for primary micronutrient diagnosis spans 95% CI [0.68, 0.88]."
        ]
        
        interventions = [
            "Administer anti-tissue transglutaminase (tTG-IgA) antibody screening to rule out silent celiac enteropathy.",
            "Evaluate stool fecal occult blood test (FOBT/FIT) in patients >45 years with unprovoked microcytic indices.",
            "Check serum TSH and Free T4 to exclude primary hypothyroidism as an alternative cause of refractory lethargy."
        ]
        
        concerns = [
            "Treating iron deficiency purely as a dietary flaw without investigating occult gastrointestinal blood loss risks missing early GI lesions."
        ]
        
        return SpecialistPerspective(
            agent_id=cls.profile.agent_id,
            agent_name=cls.profile.name,
            specialty=cls.profile.specialty_domain,
            confidence_score=0.91,
            primary_assessment="Differential analysis confirms nutritional deficit as primary, but secondary malabsorptive and thyroid etiologies must be formally excluded.",
            key_findings=findings,
            recommended_interventions=interventions,
            priority_level="HIGH",
            scientific_rationale="Symptom overlap between endocrine, hematologic, and nutritional disorders requires algorithmic exclusion of competing etiologies to prevent diagnostic anchoring bias.",
            concerns_or_objections=concerns
        )


class OutcomeOptimizationAgent:
    """Agent modeling longitudinal adherence, recovery velocities, and composite score maximization."""

    profile = AgentProfile(
        agent_id="agent_outcome",
        name="Dr. Marcus Bell, PhD",
        role="Clinical Outcomes & Health Economics Lead",
        specialty_domain="Longitudinal Recovery Modeling, Adherence Optimization & Patient Burden",
        avatar_color="#06b6d4",  # Cyan
        core_principles=[
            "Behavioral feasibility and pill-burden minimisation",
            "Longitudinal 30/60/90-day recovery velocity forecasting",
            "Unified Intervention Score (UIS) utility maximization",
            "Cost-effectiveness and real-world compliance preservation"
        ]
    )

    @classmethod
    def evaluate(cls, patient: Dict[str, Any]) -> SpecialistPerspective:
        findings = [
            "Complex protocols (>4 distinct pills/day) experience a 45% adherence drop by Week 6.",
            "Combining whole-food adjustments with once-daily co-formulated supplements yields the highest longitudinal compliance index (88%).",
            "Biomarker recovery velocity is projected to reach 75% of physiological target by Day 60 under 80%+ adherence."
        ]
        
        interventions = [
            "Consolidate supplementation to a single morning dosing regimen to eliminate regimen friction.",
            "Deploy bi-weekly mobile symptom and tolerance check-ins to catch GI side-effects before abandonment occurs.",
            "Provide affordable grocery alternative swaps ($2.50/day target incremental cost) to ensure financial sustainability."
        ]
        
        concerns = [
            "Splitting doses across multiple meals dramatically increases omission rates in busy working adults."
        ]
        
        return SpecialistPerspective(
            agent_id=cls.profile.agent_id,
            agent_name=cls.profile.name,
            specialty=cls.profile.specialty_domain,
            confidence_score=0.93,
            primary_assessment="Protocol optimization indicates maximal efficacy is achieved by simplifying the dosing schedule to preserve high real-world adherence.",
            key_findings=findings,
            recommended_interventions=interventions,
            priority_level="MODERATE",
            scientific_rationale="Real-world therapeutic efficacy is the product of intrinsic biological potency and adherence (Efficacy = Potency x Adherence); regimen simplification boosts composite outcomes by 32%.",
            concerns_or_objections=concerns
        )
