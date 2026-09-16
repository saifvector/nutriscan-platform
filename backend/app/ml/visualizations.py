"""
Dashboard Visualization & SVG Chart Engine
Phase 4: Explainable AI and Risk Factor Analysis System

Provides:
1. Server-side standalone SVG waterfall chart rendering (zero external JS dependencies)
2. Horizontal feature importance bar chart SVG rendering
3. JSON coordinate contracts for frontend charting libraries (Chart.js / Recharts)
"""

from typing import List, Dict, Any, Optional
import html


class DashboardVisualizer:
    """
    Renders standalone responsive SVG diagrams and formats JSON visualization contracts.
    """

    @staticmethod
    def generate_waterfall_svg(
        nutrient_name: str,
        base_value: float,
        final_value: float,
        steps: List[Dict[str, Any]],
        width: int = 700,
        height: int = 380
    ) -> str:
        """
        Renders a self-contained, responsive SVG waterfall plot showing how each feature
        shifts the probability from baseline E[f(x)] to final f(x).
        """
        margin_left = 180
        margin_right = 40
        margin_top = 60
        margin_bottom = 50
        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom

        # Determine value range
        all_vals = [base_value, final_value]
        running = base_value
        for s in steps:
            running += s.get("delta", 0.0)
            all_vals.append(running)
            all_vals.append(running - s.get("delta", 0.0))

        min_val = min(0.0, min(all_vals) - 0.05)
        max_val = max(1.0, max(all_vals) + 0.05)
        val_range = max_val - min_val if max_val > min_val else 1.0

        def val_to_x(v: float) -> float:
            return margin_left + ((v - min_val) / val_range) * plot_width

        n_items = len(steps) + 2  # Baseline + steps + Final
        row_height = plot_height / max(1, n_items)
        bar_thickness = min(22.0, row_height * 0.7)

        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#0f172a; border-radius:12px; font-family:Inter,system-ui,sans-serif;">',
            f'<defs>',
            f'  <linearGradient id="riskGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#ef4444"/><stop offset="100%" stop-color="#dc2626"/></linearGradient>',
            f'  <linearGradient id="protGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#10b981"/><stop offset="100%" stop-color="#059669"/></linearGradient>',
            f'  <linearGradient id="baseGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#64748b"/><stop offset="100%" stop-color="#475569"/></linearGradient>',
            f'</defs>',
            f'<!-- Title -->',
            f'<text x="{margin_left}" y="32" fill="#f8fafc" font-size="16" font-weight="700">{html.escape(nutrient_name)}: SHAP Attribution Waterfall</text>',
            f'<text x="{margin_left}" y="48" fill="#94a3b8" font-size="11">Baseline E[f(x)] = {base_value:.2f} &#8594; Final Probability = {final_value:.2f}</text>',
            f'<!-- Grid line for baseline -->',
            f'<line x1="{val_to_x(base_value)}" y1="{margin_top}" x2="{val_to_x(base_value)}" y2="{height - margin_bottom}" stroke="#334155" stroke-dasharray="4" stroke-width="1.5"/>',
        ]

        # 1. Base Value Bar
        curr_y = margin_top + 10
        base_x = val_to_x(0.0)
        base_w = abs(val_to_x(base_value) - base_x)
        svg_lines.extend([
            f'<text x="{margin_left - 12}" y="{curr_y + bar_thickness*0.75}" fill="#cbd5e1" font-size="11" text-anchor="end" font-weight="600">Population Baseline</text>',
            f'<rect x="{min(base_x, val_to_x(base_value))}" y="{curr_y}" width="{max(2.0, base_w)}" height="{bar_thickness}" rx="3" fill="url(#baseGrad)"/>',
            f'<text x="{val_to_x(base_value) + 6}" y="{curr_y + bar_thickness*0.75}" fill="#94a3b8" font-size="10">{base_value:.2f}</text>'
        ])

        # 2. Step Bars
        curr_accum = base_value
        for idx, step in enumerate(steps):
            curr_y += row_height
            delta = step.get("delta", 0.0)
            next_accum = curr_accum + delta
            label = step.get("factor_name", step.get("feature_name", f"Feature {idx+1}"))
            truncated_label = label[:24] + "..." if len(label) > 24 else label

            x_start = val_to_x(curr_accum)
            x_end = val_to_x(next_accum)
            bar_x = min(x_start, x_end)
            bar_w = max(2.0, abs(x_end - x_start))

            color = "url(#riskGrad)" if delta > 0 else "url(#protGrad)"
            sign = "+" if delta > 0 else ""

            svg_lines.extend([
                f'<text x="{margin_left - 12}" y="{curr_y + bar_thickness*0.75}" fill="#94a3b8" font-size="11" text-anchor="end">{html.escape(truncated_label)}</text>',
                f'<rect x="{bar_x}" y="{curr_y}" width="{bar_w}" height="{bar_thickness}" rx="3" fill="{color}"/>',
                f'<text x="{max(bar_x + bar_w + 5, x_end + 5)}" y="{curr_y + bar_thickness*0.75}" fill="{"#f87171" if delta > 0 else "#34d399"}" font-size="10" font-weight="600">{sign}{delta:.3f}</text>'
            ])
            curr_accum = next_accum

        # 3. Final Prediction Bar
        curr_y += row_height
        final_x = val_to_x(0.0)
        final_w = abs(val_to_x(final_value) - final_x)
        final_color = "#ef4444" if final_value >= 0.70 else ("#f59e0b" if final_value >= 0.35 else "#10b981")

        svg_lines.extend([
            f'<line x1="{margin_left}" y1="{curr_y - 4}" x2="{width - margin_right}" y2="{curr_y - 4}" stroke="#334155" stroke-width="1"/>',
            f'<text x="{margin_left - 12}" y="{curr_y + bar_thickness*0.75}" fill="#f8fafc" font-size="11" text-anchor="end" font-weight="700">Final Risk Score</text>',
            f'<rect x="{min(final_x, val_to_x(final_value))}" y="{curr_y}" width="{max(2.0, final_w)}" height="{bar_thickness}" rx="3" fill="{final_color}"/>',
            f'<text x="{val_to_x(final_value) + 6}" y="{curr_y + bar_thickness*0.75}" fill="#f8fafc" font-size="11" font-weight="700">{final_value:.2f} ({int(final_value*100)}%)</text>'
        ])

        # Bottom Axis
        axis_y = height - 20
        ticks = [min_val, (min_val+max_val)/2.0, max_val]
        for t in ticks:
            tx = val_to_x(t)
            svg_lines.append(f'<text x="{tx}" y="{axis_y}" fill="#64748b" font-size="10" text-anchor="middle">{t:.2f}</text>')

        svg_lines.append('</svg>')
        return "\n".join(svg_lines)

    @staticmethod
    def generate_feature_importance_svg(
        factors: List[Dict[str, Any]],
        title: str = "Top Risk Drivers & Protective Factors",
        width: int = 650,
        height: int = 340
    ) -> str:
        """
        Renders horizontal bidirectional bar chart (red for risk, green for protective).
        """
        margin_left = 180
        margin_right = 60
        margin_top = 50
        margin_bottom = 30
        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom

        if not factors:
            return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><text x="20" y="30" fill="#fff">No factors</text></svg>'

        max_imp = max(0.01, max(abs(f.get("impact_score", 0.0)) for f in factors))
        row_h = plot_height / max(1, len(factors))
        bar_h = min(18.0, row_h * 0.7)
        mid_x = margin_left + (plot_width / 2.0)

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#0b1329; border-radius:12px; font-family:Inter,system-ui,sans-serif;">',
            f'<text x="{margin_left}" y="30" fill="#f8fafc" font-size="15" font-weight="700">{html.escape(title)}</text>',
            f'<line x1="{mid_x}" y1="{margin_top}" x2="{mid_x}" y2="{height - margin_bottom}" stroke="#334155" stroke-width="1.5"/>',
            f'<text x="{mid_x - 10}" y="{margin_top - 10}" fill="#10b981" font-size="10" text-anchor="end">&#8592; Protective</text>',
            f'<text x="{mid_x + 10}" y="{margin_top - 10}" fill="#ef4444" font-size="10" text-anchor="start">Risk Driver &#8594;</text>'
        ]

        for i, f in enumerate(factors):
            y = margin_top + (i * row_h)
            imp = f.get("impact_score", 0.0)
            pct = f.get("contribution_percentage", 0.0)
            name = f.get("factor_name", f.get("feature_name", ""))
            trunc_name = name[:24] + ".." if len(name) > 24 else name

            bar_len = (abs(imp) / max_imp) * (plot_width / 2.0)
            if imp >= 0:
                bar_x = mid_x
                color = "#ef4444"
                text_x = mid_x + bar_len + 6
                text_anchor = "start"
            else:
                bar_x = mid_x - bar_len
                color = "#10b981"
                text_x = mid_x - bar_len - 6
                text_anchor = "end"

            svg.extend([
                f'<text x="{margin_left - 10}" y="{y + bar_h*0.8}" fill="#94a3b8" font-size="11" text-anchor="end">{html.escape(trunc_name)}</text>',
                f'<rect x="{bar_x}" y="{y}" width="{max(2.0, bar_len)}" height="{bar_h}" rx="3" fill="{color}"/>',
                f'<text x="{text_x}" y="{y + bar_h*0.8}" fill="#cbd5e1" font-size="10" text-anchor="{text_anchor}">{pct:.1f}%</text>'
            ])

        svg.append('</svg>')
        return "\n".join(svg)

    @staticmethod
    def format_recharts_contract(
        base_value: float,
        final_value: float,
        steps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Formats waterfall coordinates specifically for React Recharts / Chart.js stacked bar charts.
        """
        recharts_data = []
        running = 0.0

        # Baseline item
        recharts_data.append({
            "name": "Population Baseline",
            "bottom": 0.0,
            "value": round(base_value, 4),
            "delta": round(base_value, 4),
            "direction": "BASELINE",
            "color": "#64748b"
        })
        running = base_value

        for s in steps:
            delta = s.get("delta", 0.0)
            if delta >= 0:
                bottom = running
                val = delta
                color = "#ef4444"
            else:
                bottom = running + delta
                val = abs(delta)
                color = "#10b981"

            recharts_data.append({
                "name": s.get("factor_name", s.get("feature_name")),
                "bottom": round(bottom, 4),
                "value": round(val, 4),
                "delta": round(delta, 4),
                "direction": "RISK_INCREASING" if delta >= 0 else "PROTECTIVE",
                "color": color
            })
            running += delta

        # Final score item
        recharts_data.append({
            "name": "Final Risk Score",
            "bottom": 0.0,
            "value": round(final_value, 4),
            "delta": round(final_value, 4),
            "direction": "FINAL",
            "color": "#f59e0b" if final_value >= 0.35 else "#10b981"
        })

        return recharts_data
