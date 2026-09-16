# Phase 5 Architecture Specification: Personalized Nutrition Recommendation Engine

## 1. Executive Summary

The **Personalized Nutrition Recommendation Engine** is the clinical intelligence layer of the *Integrated AI-Based Nutrient Deficiency Screening and Personalized Nutrition Platform*. It ingests multi-nutrient deficiency risk scores (from Phase 3) and SHAP feature attribution metrics (from Phase 4), contextualizes them against individual user phenotypes (dietary patterns, food allergies/intolerances, medical conditions, medication regimens, lifestyle factors), and generates:

1. **Filtered, High-Bioavailability Food Recommendations** categorized into Priority Tiers (Priority 1: High-Deficiency, Priority 2: Moderate-Deficiency, Priority 3: Foundational/Preventative).
2. **Biochemical Synergistic Food Pairings & Inhibitor Warnings** to maximize micronutrient uptake and avoid counter-regulatory nutrient competitions.
3. **Evidence-Based Lifestyle Interventions** addressing root behavioral causes identified by SHAP risk attribution (sunlight exposure, circadian alignment, hydration, stress management, exercise).
4. **Structured 7 / 14 / 30-Day Recovery Roadmap** progressing from acute deficiency stabilization to sustainable systemic maintenance.
5. **Multi-Dimensional Recommendation Scoring (0–100)** evaluating relevance, nutrient coverage, dietary compatibility, and overall plan quality.

---

## 2. End-to-End System Architecture

```
                    +------------------------------------+
                    |     User Health Assessment         |
                    |  (Demographics, Diet, Symptoms,    |
                    |   Lifestyle, Medications, Labs)    |
                    +-----------------+------------------+
                                      |
                                      v
                    +------------------------------------+
                    | Phase 3: Multi-Nutrient Inference  |
                    | 11 XGBoost Calibrated Classifiers  |
                    +-----------------+------------------+
                                      |
                                      v
                    +------------------------------------+
                    | Phase 4: SHAP Explainability Engine|
                    | Feature Contributions & Risk Drivers|
                    +-----------------+------------------+
                                      |
                                      v
+==================================================================================+
|                 PHASE 5: PERSONALIZED RECOMMENDATION ENGINE                      |
|                                                                                  |
|  1. DIETARY FILTERING PIPELINE                                                   |
|     [Exclusion Rules: Vegan, Vegetarian, Dairy-Free, Gluten-Free, Allergies]     |
|                                                                                  |
|  2. NUTRIENT DENSITY & BIOAVAILABILITY SCORER                                    |
|     [Score = Nutrient_Density * Bioavailability * SHAP_Weight * Risk_Score]      |
|                                                                                  |
|  3. PRIORITY TIER DISPATCHER                                                     |
|     • Tier 1: Risk Probability >= 0.65 OR High/Severe Category                   |
|     • Tier 2: Risk Probability >= 0.40 AND < 0.65                                |
|     • Tier 3: Risk Probability < 0.40 (Foundational Nutrients)                   |
|                                                                                  |
|  4. SYNERGY & INHIBITION MATRIX EVALUATOR                                        |
|     • Fe + Vit C (3-4x absorption)      • Vit D3 + Ca (Active transport)         |
|     • Mg + Vit D (Enzyme cofactor)      • Vit B12 + Folate (Methylation cycle)   |
|     • Zn vs Fe (Competitive binding)    • Phytates / Tannins (Chelation warning) |
|                                                                                  |
|  5. LIFESTYLE INTERVENTION ENGINE                                                |
|     [Sunlight, Sleep hygiene, Hydration, Cortisol control, Resistance training]  |
|                                                                                  |
|  6. 7 / 14 / 30-DAY RECOVERY ROADMAP COMPILER                                    |
|     • Days 1–7: Rapid Replenishment & Acute Symptom Relief                       |
|     • Days 8–14: Digestive & Absorption Optimization                             |
|     • Days 15–30: Cellular Restoration, Habit Consolidation & Maintenance        |
|                                                                                  |
|  7. RECOMMENDATION QUALITY SCORING (0-100)                                       |
|     • Relevance (35%) • Coverage (30%) • Compatibility (25%) • Diversity (10%)   |
+==================================================================================+
                                      |
                                      v
                    +------------------------------------+
                    | RESTful API Endpoints (/api/v1)    |
                    | Fast JSON Payloads (< 50 ms)       |
                    | Persistence: PostgreSQL 15+        |
                    +------------------------------------+
```

---

## 3. Nutrient-to-Food Knowledge Base

The food knowledge base comprises whole foods evaluated across all 11 core target nutrients. Each food entry is curated with biochemical parameters:

| Nutrient | Representative Food Items | Bioavailability Index | Standard Serving | Clinical Absorption Co-Factors |
| :--- | :--- | :---: | :---: | :--- |
| **Protein** | Wild Salmon, Chicken Breast, Eggs, Tempeh, Lentils, Hemp Seeds, Greek Yogurt | 0.70 – 0.95 | 85g – 200g | Gastric acid, protease activity, pyridoxine (B6) |
| **Vitamin A** | Sweet Potato, Carrots, Spinach, Beef Liver, Pumpkin | 0.65 – 0.90 | 100g – 150g | Dietary lipids (fat-soluble carotenoid emulsification) |
| **Vitamin B12** | Sardines, Nutritional Yeast (fortified), Salmon, Beef Tenderloin, Eggs | 0.50 – 0.85 | 10g – 100g | Gastric Intrinsic Factor (IF), stomach acid (HCl) |
| **Folate (B9)** | Chickpeas, Edamame, Asparagus, Spinach, Avocado | 0.70 – 0.85 | 100g – 180g | Minimal cooking heat, Vitamin C stability preservation |
| **Vitamin C** | Guava, Red Bell Pepper, Kiwi, Broccoli, Strawberries, Oranges | 0.80 – 0.90 | 80g – 150g | Fresh/raw consumption to prevent thermal degradation |
| **Vitamin D** | Wild Salmon, Fortified Almond Milk, Egg Yolks, Maitake Mushrooms, Sardines | 0.70 – 0.85 | 100g – 240ml | Dietary fats, Magnesium (cofactor for 25-hydroxylase) |
| **Vitamin E** | Sunflower Seeds, Almonds, Wheat Germ Oil, Avocado, Spinach | 0.75 – 0.85 | 15ml – 30g | Healthy fats; fat malabsorption inhibits uptake |
| **Iron** | Grass-fed Beef, Lentils, Pumpkin Seeds, Spinach, Black Beans | 0.15 (Non-heme) - 0.35 (Heme) | 85g – 200g | Ascorbic acid enhances; tannins, phytates, dairy inhibit |
| **Calcium** | Sardines with bones, Collard Greens, Chia Seeds, Tofu, Greek Yogurt | 0.30 – 0.35 | 100g – 200g | Vitamin D3, gastric acid; excess sodium increases urinary excretion |
| **Zinc** | Oysters, Pumpkin Seeds, Grass-fed Beef, Hemp Hearts, Chickpeas | 0.25 – 0.40 | 30g – 150g | Protein-bound carriers; phytates/high-dose iron inhibit |
| **Magnesium** | Pumpkin Seeds, Dark Chocolate (85%), Black Beans, Almonds, Swiss Chard | 0.35 – 0.45 | 30g – 180g | Vitamin B6 enhances uptake; phytic acid inhibits |

---

## 4. Dietary Restriction & Safety Rules

Strict boolean and string containment checks prevent cross-contamination:

1. **Vegan Filtering:**
   - Excludes all animal flesh, poultry, seafood, dairy products, eggs, honey, and gelatin.
   - Fortified plant sources (e.g., Nutritional Yeast, Fortified Plant Milk) prioritized for B12 and Vitamin D.
2. **Vegetarian Filtering:**
   - Excludes poultry, red meat, and seafood. Permits dairy and eggs.
3. **Dairy-Free Filtering:**
   - Excludes cows' milk, yogurt, cheeses, whey, casein, and butter. Prioritizes dark leafy greens, sesame seeds, and fortified alternatives for Calcium.
4. **Gluten-Free Filtering:**
   - Excludes wheat, barley, rye, spelt, and conventional oats. Permits quinoa, rice, buckwheat, and gluten-free legumes.
5. **Medical Contraindications:**
   - *Chronic Kidney Disease (CKD):* Suppresses high-potassium/phosphorus foods (spinach, pumpkin seeds, high protein loads).
   - *Warfarin/Anticoagulants:* Flags Vitamin K-rich leafy greens (spinach, collard greens) for INR consistency.
   - *Hemochromatosis:* Suppresses supplemental heme iron and ascorbic acid mega-dosing.

---

## 5. Synergistic Food Pairings & Absorption Inhibitors

The engine contains an explicit clinical synergy matrix:

- **Iron + Vitamin C:** Non-heme iron reduction from $Fe^{3+}$ to soluble $Fe^{2+}$ by ascorbic acid; boosts bioavailability by 300–400%.
  *Pairing:* Lentils or spinach drizzled with fresh lemon juice or paired with sliced bell peppers.
- **Vitamin D3 + Calcium:** Calcitriol activates intestinal epithelial calcium channels (TRPV6) and calbindin synthesis.
  *Pairing:* Steamed collard greens or tofu sautéed with wild salmon or maitake mushrooms.
- **Magnesium + Vitamin D:** All enzymes metabolizing Vitamin D require hepatic and renal magnesium as an enzymatic cofactor.
  *Pairing:* Pumpkin seeds and almonds paired with sun-exposed maitake or fortified plant milk.
- **Vitamin B12 + Folate:** Interdependent one-carbon transfer and homocysteine-to-methionine conversion cycle.
  *Pairing:* Nutritional yeast sprinkled over steamed asparagus or chickpea bowls.
- **Inhibition Alerts:**
  - *Calcium vs. Iron:* Ingestion of >300mg calcium inhibits both heme and non-heme iron uptake; separate meals by 2 hours.
  - *Zinc vs. Iron:* High-dose inorganic iron competes with zinc for divalent metal transporter 1 (DMT1).
  - *Tannins/Polyphenols (Tea/Coffee):* Inhibit non-heme iron absorption up to 60–90% if consumed during or within 1 hour of meals.

---

## 6. 7 / 14 / 30-Day Recovery Roadmap Protocol

The recovery plan generates progressive, measurable milestone targets:

### Phase 1: Days 1–7 (Acute Replenishment & Symptom Relief)
- **Goal:** Rapidly arrest micronutrient depletion and relieve acute symptoms (fatigue, brain fog, muscular cramps).
- **Nutritional Focus:** Incorporate at least 2 Priority-1 bioavailable nutrient-dense food servings daily.
- **Lifestyle Action:** Optimize hydration baseline (35ml/kg body weight) and establish consistent sleep rhythms.
- **Clinical Milestone:** Reduction in reported morning fatigue and neuromuscular irritability.

### Phase 2: Days 8–14 (Digestive & Bioavailability Optimization)
- **Goal:** Enhance intestinal mucosal absorption and eliminate concurrent absorption inhibitors.
- **Nutritional Focus:** Apply synergistic food pairings (e.g., Vitamin C + Iron) at all major meals; separate tea/coffee by 90 minutes.
- **Lifestyle Action:** Introduce 15–20 minutes of midday sunlight or circadian light exposure; reduce gut barrier stress.
- **Clinical Milestone:** Enhanced digestive comfort, stabilized energy throughout the afternoon.

### Phase 3: Days 15–30 (Cellular Restoration & Habit Consolidation)
- **Goal:** Restore intracellular and tissue nutrient reserves, transitioning to sustainable long-term dietary routines.
- **Nutritional Focus:** Expand dietary diversity across 20+ distinct whole foods weekly, alternating plant and protein sources.
- **Lifestyle Action:** Integrate moderate resistance and aerobic physical exercise (3–4x weekly) to stimulate nutrient turnover.
- **Clinical Milestone:** Normalization of subjective clinical symptoms; readiness for repeat screening assessment.

---

## 7. Recommendation Scoring Methodology

Every recommendation payload is evaluated across four distinct mathematical dimensions:

1. **Relevance Score ($S_{rel}$):**
   $$\text{Coverage of Flagged High-Risk Deficiencies} \times 100$$
   Reflects how precisely the generated food recommendations target the user's elevated risk profile.
2. **Coverage Score ($S_{cov}$):**
   $$\frac{\text{Unique Targeted Nutrients}}{\text{Total Flagged Nutrients}} \times 100$$
   Guarantees that no flagged nutrient deficiency is left unaddressed.
3. **Compatibility Score ($S_{comp}$):**
   $$\left(1.0 - \frac{\text{Restricted Food Violations}}{\text{Total Candidate Foods}}\right) \times 100$$
   Strictly penalized (drops to 0% if any diet or allergy breach is detected).
4. **Overall Recommendation Score ($S_{overall}$):**
   $$S_{overall} = 0.35 \cdot S_{rel} + 0.30 \cdot S_{cov} + 0.25 \cdot S_{comp} + 0.10 \cdot S_{diversity}$$

---

## 8. API Specifications & Performance

Mounted under `/api/v1/recommendations`:
- `GET /api/v1/recommendations/{assessment_id}`: Comprehensive full recommendation dossier (foods, pairings, lifestyle, recovery roadmap, scores).
- `GET /api/v1/recommendations/{assessment_id}/foods`: Filtered food recommendations grouped by Priority Tier and target nutrient.
- `GET /api/v1/recommendations/{assessment_id}/lifestyle`: Behavior-driven lifestyle interventions mapped to SHAP root causes.
- `GET /api/v1/recommendations/{assessment_id}/recovery-plan`: Progressive 7/14/30-day clinical recovery roadmap.

### SLA Compliance
- **Target Response Time:** $< 500\text{ ms}$
- **Observed Benchmarked Latency:** $< 35\text{ ms}$
- **Database Transactions:** Asynchronous background relational persistence to `food_recommendations` table without blocking client response.
