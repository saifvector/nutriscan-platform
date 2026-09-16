"""
Dashboard Visualization Engine
Phase 6: Comprehensive Nutritional Report Generation and Health Dashboard

Builds structured JSON charting contracts (for React Recharts / Chart.js) and
standalone responsive server-side SVGs for 6 dashboard visualization widgets:
1. Nutrient Risk Radar Chart (11 polar radial axes)
2. Nutrient Risk Bar Chart (sorted severity-coded bars)
3. Deficiency Priority Ranking Chart (Priority 1, 2, 3 tiering)
4. SHAP Feature Importance Chart (bidirectional risk vs protective drivers)
5. Nutrient Interaction Graph (network topology nodes & biochemical edges)
6. Recovery Progress Timeline (7, 14, 30-day milestone progress)
"""

import math
import html
from typing import Dict, Any, List, Optional
from ...schemas.report import DashboardVisualizationsBundle


class DashboardBuilder:
    """
    Renders visualization contracts and standalone SVGs for nutritional dashboards.
    """

    @classmethod
    def build_all_visualizations(
        cls,
        nutrient_predictions: List[Dict[str, Any]],
        interaction_analysis: Optional[Dict[str, Any]] = None,
        explainability_data: Optional[Dict[str, Any]] = None,
        recovery_plan: Optional[Dict[str, Any]] = None,
        priority_foods: Optional[Dict[str, List[Any]]] = None
    ) -> DashboardVisualizationsBundle:
        """
        Compiles all 6 dashboard visualization contracts and SVG assets.
        """
        interaction_analysis = interaction_analysis or {}
        explainability_data = explainability_data or {}
        recovery_plan = recovery_plan or {}

        radar = cls.build_radar_chart(nutrient_predictions)
        bar = cls.build_bar_chart(nutrient_predictions)
        priority = cls.build_priority_ranking_chart(nutrient_predictions)
        shap = cls.build_shap_importance_chart(explainability_data)
        graph = cls.build_interaction_graph(nutrient_predictions, interaction_analysis)
        timeline = cls.build_recovery_timeline(recovery_plan)

        return DashboardVisualizationsBundle(
            radar_chart=radar,
            bar_chart=bar,
            priority_ranking_chart=priority,
            shap_importance_chart=shap,
            interaction_graph=graph,
            recovery_timeline=timeline
        )

    # -------------------------------------------------------------------------
    # 1. Nutrient Risk Radar Chart
    # -------------------------------------------------------------------------
    @classmethod
    def build_radar_chart(cls, nutrient_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates polar radar chart for all 11 target nutrients.
        """
        data = []
        for p in nutrient_predictions:
            prob = float(p.get("probability", 0.0))
            data.append({
                "nutrient": p.get("nutrient", ""),
                "probability": round(prob, 3),
                "risk_score": int(round(prob * 100)),
                "risk_level": p.get("risk_level", "LOW")
            })

        # SVG Dimensions
        width, height = 520, 440
        cx, cy = width / 2.0, height / 2.0 + 10
        radius = 150.0
        n_axes = max(1, len(data))

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#0f172a; border-radius:12px; font-family:Inter,system-ui,sans-serif;">',
            f'<text x="{width/2}" y="28" fill="#f8fafc" font-size="15" font-weight="700" text-anchor="middle">Nutrient Deficiency Risk Radar</text>',
            f'<text x="{width/2}" y="44" fill="#94a3b8" font-size="11" text-anchor="middle">11-Target Polar Risk Profile (0% Center &#8594; 100% Perimeter)</text>'
        ]

        # Draw concentric rings
        for level, pct in [(0.25, "25%"), (0.50, "50%"), (0.75, "75%"), (1.00, "100%")]:
            r = radius * level
            svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" stroke="#334155" stroke-dasharray="3" stroke-width="1"/>')
            svg.append(f'<text x="{cx + 4}" y="{cy - r + 10}" fill="#64748b" font-size="9">{pct}</text>')

        # Calculate polygon points
        poly_points = []
        for i, item in enumerate(data):
            angle = (2 * math.pi * i / n_axes) - (math.pi / 2.0)
            score_frac = min(1.0, max(0.05, item["probability"]))
            pt_r = radius * score_frac
            px = cx + pt_r * math.cos(angle)
            py = cy + pt_r * math.sin(angle)
            poly_points.append((px, py))

            # Axis line
            ax_x = cx + radius * math.cos(angle)
            ax_y = cy + radius * math.sin(angle)
            svg.append(f'<line x1="{cx}" y1="{cy}" x2="{ax_x:.1f}" y2="{ax_y:.1f}" stroke="#1e293b" stroke-width="1.5"/>')

            # Label position
            lbl_r = radius + 22.0
            lx = cx + lbl_r * math.cos(angle)
            ly = cy + lbl_r * math.sin(angle) + 4
            anchor = "middle"
            if math.cos(angle) > 0.3:
                anchor = "start"
            elif math.cos(angle) < -0.3:
                anchor = "end"

            nut_short = item["nutrient"].replace("Vitamin ", "Vit ")
            svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#cbd5e1" font-size="10" text-anchor="{anchor}" font-weight="600">{html.escape(nut_short)}</text>')

        # Draw polygon
        if poly_points:
            pts_str = " ".join([f"{p[0]:.1f},{p[1]:.1f}" for p in poly_points])
            svg.append(f'<polygon points="{pts_str}" fill="rgba(239, 68, 68, 0.25)" stroke="#ef4444" stroke-width="2.5"/>')

            # Draw data nodes
            for p in poly_points:
                svg.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.5" fill="#f87171" stroke="#ffffff" stroke-width="1.5"/>')

        svg.append('</svg>')

        return {
            "chart_type": "RADAR",
            "data": data,
            "svg": "\n".join(svg)
        }

    # -------------------------------------------------------------------------
    # 2. Nutrient Risk Bar Chart
    # -------------------------------------------------------------------------
    @classmethod
    def build_bar_chart(cls, nutrient_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates horizontal bar chart sorted by risk probability.
        """
        sorted_items = sorted(nutrient_predictions, key=lambda x: float(x.get("probability", 0.0)), reverse=True)
        data = []
        for p in sorted_items:
            prob = float(p.get("probability", 0.0))
            lvl = p.get("risk_level", "LOW")
            color = "#ef4444" if "HIGH" in lvl or "SEVERE" in lvl else ("#f59e0b" if "MODERATE" in lvl else "#10b981")
            data.append({
                "nutrient": p.get("nutrient", ""),
                "probability": round(prob, 3),
                "percentage": int(round(prob * 100)),
                "risk_level": lvl,
                "color": color
            })

        width, height = 560, 400
        margin_left, margin_right = 130, 70
        margin_top, margin_bottom = 50, 30
        plot_w = width - margin_left - margin_right
        plot_h = height - margin_top - margin_bottom

        n = len(data)
        row_h = plot_h / max(1, n)
        bar_h = min(18.0, row_h * 0.72)

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#0b1329; border-radius:12px; font-family:Inter,system-ui,sans-serif;">',
            f'<text x="{margin_left}" y="28" fill="#f8fafc" font-size="15" font-weight="700">Nutrient Risk Probability Rankings</text>',
            f'<text x="{margin_left}" y="42" fill="#94a3b8" font-size="11">Predicted deficiency probability across 11 target nutrients</text>',
            f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#334155" stroke-width="1.5"/>',
            # 50% Threshold marker line
            f'<line x1="{margin_left + plot_w*0.5}" y1="{margin_top}" x2="{margin_left + plot_w*0.5}" y2="{height - margin_bottom}" stroke="#475569" stroke-dasharray="3" stroke-width="1"/>',
            f'<text x="{margin_left + plot_w*0.5}" y="{height - 12}" fill="#64748b" font-size="9" text-anchor="middle">50% Risk Threshold</text>'
        ]

        for i, item in enumerate(data):
            y = margin_top + (i * row_h)
            w = max(2.0, (item["probability"]) * plot_w)
            svg.extend([
                f'<text x="{margin_left - 10}" y="{y + bar_h*0.8}" fill="#cbd5e1" font-size="11" text-anchor="end">{html.escape(item["nutrient"])}</text>',
                f'<rect x="{margin_left}" y="{y}" width="{w:.1f}" height="{bar_h:.1f}" rx="3" fill="{item["color"]}"/>',
                f'<text x="{margin_left + w + 8}" y="{y + bar_h*0.8}" fill="#f8fafc" font-size="10" font-weight="600">{item["percentage"]}%</text>'
            ])

        svg.append('</svg>')

        return {
            "chart_type": "BAR_CHART",
            "data": data,
            "svg": "\n".join(svg)
        }

    # -------------------------------------------------------------------------
    # 3. Deficiency Priority Ranking Chart
    # -------------------------------------------------------------------------
    @classmethod
    def build_priority_ranking_chart(cls, nutrient_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates Priority Tier classification widget (Priority 1, 2, 3).
        """
        sorted_items = sorted(nutrient_predictions, key=lambda x: float(x.get("probability", 0.0)), reverse=True)
        data = []
        for idx, p in enumerate(sorted_items):
            prob = float(p.get("probability", 0.0))
            lvl = p.get("risk_level", "LOW")
            if prob >= 0.65 or "HIGH" in lvl or "SEVERE" in lvl:
                tier = "Priority 1 (Urgent)"
                tier_badge = "P1"
                color = "#ef4444"
            elif prob >= 0.40 or "MODERATE" in lvl:
                tier = "Priority 2 (Targeted)"
                tier_badge = "P2"
                color = "#f59e0b"
            else:
                tier = "Priority 3 (Maintenance)"
                tier_badge = "P3"
                color = "#10b981"

            data.append({
                "rank": idx + 1,
                "nutrient": p.get("nutrient", ""),
                "probability": round(prob, 3),
                "tier": tier,
                "tier_badge": tier_badge,
                "color": color
            })

        width, height = 520, 360
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#0f172a; border-radius:12px; font-family:Inter,system-ui,sans-serif;">',
            f'<text x="24" y="28" fill="#f8fafc" font-size="15" font-weight="700">Deficiency Priority Tier Classification</text>',
            f'<text x="24" y="44" fill="#94a3b8" font-size="11">Clinical prioritization matrix for dietary & supplement sequencing</text>'
        ]

        # Draw top 6 priority items in a responsive grid
        card_w = (width - 60) / 2.0
        card_h = 44.0
        start_y = 65

        for i, item in enumerate(data[:8]):
            col = i % 2
            row = i // 2
            cx = 20 + col * (card_w + 20)
            cy = start_y + row * (card_h + 10)

            svg.extend([
                f'<rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>',
                f'<rect x="{cx + 8}" y="{cy + 10}" width="26" height="24" rx="4" fill="{item["color"]}"/>',
                f'<text x="{cx + 21}" y="{cy + 26}" fill="#ffffff" font-size="11" font-weight="800" text-anchor="middle">{item["tier_badge"]}</text>',
                f'<text x="{cx + 42}" y="{cy + 22}" fill="#f8fafc" font-size="11" font-weight="700">{html.escape(item["nutrient"])}</text>',
                f'<text x="{cx + 42}" y="{cy + 34}" fill="#94a3b8" font-size="10">{item["tier"]}</text>',
                f'<text x="{cx + card_w - 12}" y="{cy + 26}" fill="#cbd5e1" font-size="11" font-weight="700" text-anchor="end">#{item["rank"]}</text>'
            ])

        svg.append('</svg>')

        return {
            "chart_type": "PRIORITY_RANKING",
            "data": data,
            "svg": "\n".join(svg)
        }

    # -------------------------------------------------------------------------
    # 4. SHAP Feature Importance Chart
    # -------------------------------------------------------------------------
    @classmethod
    def build_shap_importance_chart(cls, explainability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates bidirectional SHAP feature attribution bar chart.
        """
        drivers = explainability_data.get("top_risk_drivers", [])
        protective = explainability_data.get("top_protective_factors", [])

        data = []
        for d in drivers[:4]:
            data.append({
                "factor_name": d.get("factor_name", d.get("feature_name", "Risk Driver")),
                "impact_score": round(float(d.get("impact_score", 0.05)), 4),
                "contribution_percentage": round(float(d.get("contribution_percentage", 15.0)), 1),
                "type": "RISK_INCREASING"
            })
        for p in protective[:4]:
            data.append({
                "factor_name": p.get("factor_name", p.get("feature_name", "Protective Factor")),
                "impact_score": round(-abs(float(p.get("impact_score", 0.05))), 4),
                "contribution_percentage": round(float(p.get("contribution_percentage", 12.0)), 1),
                "type": "PROTECTIVE"
            })

        from ..explainability.service import ExplainabilityService
        from ...ml.visualizations import DashboardVisualizer

        svg_str = DashboardVisualizer.generate_feature_importance_svg(
            factors=data,
            title="SHAP Risk Factor Attribution Balance",
            width=580,
            height=340
        )

        return {
            "chart_type": "SHAP_IMPORTANCE",
            "data": data,
            "svg": svg_str
        }

    # -------------------------------------------------------------------------
    # 5. Nutrient Interaction Graph
    # -------------------------------------------------------------------------
    @classmethod
    def build_interaction_graph(
        cls,
        nutrient_predictions: List[Dict[str, Any]],
        interaction_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Builds network graph of nutrient nodes and biochemical interaction edges.
        """
        nodes = []
        pred_map = {p.get("nutrient"): p for p in nutrient_predictions}

        # Select core 8 nutrients for clean network topology
        core_nutrients = ["Vitamin D", "Calcium", "Iron", "Vitamin C", "Magnesium", "Zinc", "Vitamin B12", "Folate"]
        for idx, nut in enumerate(core_nutrients):
            p = pred_map.get(nut, {})
            prob = float(p.get("probability", 0.25))
            lvl = p.get("risk_level", "LOW")
            color = "#ef4444" if "HIGH" in lvl else ("#f59e0b" if "MODERATE" in lvl else "#10b981")
            nodes.append({
                "id": nut,
                "label": nut.replace("Vitamin ", "Vit "),
                "risk_level": lvl,
                "probability": prob,
                "color": color
            })

        edges = [
            {"source": "Vitamin D", "target": "Calcium", "type": "SYNERGY", "label": "Active Transport"},
            {"source": "Iron", "target": "Vitamin C", "type": "SYNERGY", "label": "Bioavailability +300%"},
            {"source": "Magnesium", "target": "Vitamin D", "type": "CO-FACTOR", "label": "Enzymatic Cofactor"},
            {"source": "Vitamin B12", "target": "Folate", "type": "SYNERGY", "label": "Methylation Cycle"},
            {"source": "Iron", "target": "Zinc", "type": "COMPETITIVE", "label": "DMT1 Competition"},
            {"source": "Calcium", "target": "Iron", "type": "INHIBITORY", "label": "Absorption Blocker"}
        ]

        # Generate Network SVG
        width, height = 540, 360
        cx, cy = width / 2.0, height / 2.0 + 15
        radius = 120.0
        n_nodes = len(nodes)

        node_positions = {}
        for i, node in enumerate(nodes):
            angle = (2 * math.pi * i / n_nodes) - (math.pi / 2.0)
            nx = cx + radius * math.cos(angle)
            ny = cy + radius * math.sin(angle)
            node_positions[node["id"]] = (nx, ny)

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#090d16; border-radius:12px; font-family:Inter,system-ui,sans-serif;">',
            f'<text x="{width/2}" y="28" fill="#f8fafc" font-size="15" font-weight="700" text-anchor="middle">Biochemical Nutrient Interaction Network</text>',
            f'<text x="{width/2}" y="44" fill="#94a3b8" font-size="11" text-anchor="middle">Green = Synergy, Blue = Co-factor, Red = Competitive Inhibition</text>'
        ]

        # Draw Edges
        for edge in edges:
            p1 = node_positions.get(edge["source"])
            p2 = node_positions.get(edge["target"])
            if p1 and p2:
                edge_col = "#10b981" if edge["type"] == "SYNERGY" else ("#38bdf8" if edge["type"] == "CO-FACTOR" else "#f43f5e")
                stroke_dash = "4" if edge["type"] in ["COMPETITIVE", "INHIBITORY"] else "none"
                svg.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{edge_col}" stroke-width="2" stroke-dasharray="{stroke_dash}" opacity="0.8"/>')

        # Draw Nodes
        for node in nodes:
            pos = node_positions.get(node["id"])
            if pos:
                svg.extend([
                    f'<circle cx="{pos[0]:.1f}" cy="{pos[1]:.1f}" r="18" fill="#1e293b" stroke="{node["color"]}" stroke-width="2.5"/>',
                    f'<text x="{pos[0]:.1f}" y="{pos[1] + 4:.1f}" fill="#ffffff" font-size="9" font-weight="700" text-anchor="middle">{html.escape(node["label"])}</text>'
                ])

        svg.append('</svg>')

        return {
            "chart_type": "INTERACTION_GRAPH",
            "nodes": nodes,
            "edges": edges,
            "svg": "\n".join(svg)
        }

    # -------------------------------------------------------------------------
    # 6. Recovery Progress Timeline
    # -------------------------------------------------------------------------
    @classmethod
    def build_recovery_timeline(cls, recovery_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates 7, 14, 30-day milestone progress timeline.
        """
        p7 = recovery_plan.get("phase_7_day", {})
        p14 = recovery_plan.get("phase_14_day", {})
        p30 = recovery_plan.get("phase_30_day", {})

        milestones = [
            {
                "day": 7,
                "title": p7.get("phase_title", "Acute Replenishment"),
                "goal": p7.get("primary_objective", "Target acute deficiency symptoms and stabilize energy."),
                "badge": "Days 1–7",
                "color": "#38bdf8"
            },
            {
                "day": 14,
                "title": p14.get("phase_title", "Absorption Optimization"),
                "goal": p14.get("primary_objective", "Incorporate synergistic food pairings and eliminate inhibitors."),
                "badge": "Days 8–14",
                "color": "#818cf8"
            },
            {
                "day": 30,
                "title": p30.get("phase_title", "Maintenance & Consolidation"),
                "goal": p30.get("primary_objective", "Consolidate long-term dietary diversity and metabolic vitality."),
                "badge": "Days 15–30",
                "color": "#34d399"
            }
        ]

        width, height = 580, 260
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#0f172a; border-radius:12px; font-family:Inter,system-ui,sans-serif;">',
            f'<text x="24" y="28" fill="#f8fafc" font-size="15" font-weight="700">Nutritional Recovery Progression Timeline</text>',
            f'<text x="24" y="44" fill="#94a3b8" font-size="11">Progressive clinical milestones from acute replenishment to systemic resilience</text>',
            # Horizontal connector bar
            f'<line x1="60" y1="100" x2="{width - 60}" y2="100" stroke="#334155" stroke-width="4" stroke-linecap="round"/>',
            f'<line x1="60" y1="100" x2="{width/2}" y2="100" stroke="#38bdf8" stroke-width="4" stroke-linecap="round"/>'
        ]

        step_w = (width - 120) / 2.0
        for i, ms in enumerate(milestones):
            x = 60 + (i * step_w)
            y = 100
            svg.extend([
                f'<circle cx="{x}" cy="{y}" r="14" fill="#0f172a" stroke="{ms["color"]}" stroke-width="3"/>',
                f'<text x="{x}" y="{y + 4}" fill="{ms["color"]}" font-size="10" font-weight="800" text-anchor="middle">{i+1}</text>',
                f'<rect x="{x - 45}" y="{y + 24}" width="90" height="20" rx="4" fill="{ms["color"]}" opacity="0.2"/>',
                f'<text x="{x}" y="{y + 38}" fill="{ms["color"]}" font-size="10" font-weight="700" text-anchor="middle">{ms["badge"]}</text>',
                f'<text x="{x}" y="{y + 60}" fill="#f8fafc" font-size="12" font-weight="700" text-anchor="middle">{html.escape(ms["title"])}</text>',
                f'<foreignObject x="{x - 85}" y="{y + 68}" width="170" height="60">',
                f'  <div xmlns="http://www.w3.org/1999/xhtml" style="font-size:10px; color:#94a3b8; text-align:center; line-height:1.3;">{html.escape(ms["goal"][:65])}...</div>',
                f'</foreignObject>'
            ])

        svg.append('</svg>')

        return {
            "chart_type": "RECOVERY_TIMELINE",
            "milestones": milestones,
            "svg": "\n".join(svg)
        }
