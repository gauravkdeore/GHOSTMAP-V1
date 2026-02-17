"""
GHOSTMAP PDF Report Generator — Generate professional security reports.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger("ghostmap.reporter")


# Color palette
GHOST_DARK = colors.HexColor("#1a1a2e")
GHOST_BLUE = colors.HexColor("#0f3460")
GHOST_ACCENT = colors.HexColor("#e94560")
GHOST_GREEN = colors.HexColor("#a6e3a1")
GHOST_YELLOW = colors.HexColor("#fab387")
GHOST_RED = colors.HexColor("#f38ba8")
GHOST_GRAY = colors.HexColor("#6c7086")
WHITE = colors.white


class GhostMapReporter:
    """
    Generates professional PDF security reports from GHOSTMAP audit results.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Configure custom report styles."""
        self.styles.add(ParagraphStyle(
            name="GhostTitle",
            fontName="Helvetica-Bold",
            fontSize=28,
            textColor=GHOST_DARK,
            alignment=TA_CENTER,
            spaceAfter=12,
        ))
        self.styles.add(ParagraphStyle(
            name="GhostSubtitle",
            fontName="Helvetica",
            fontSize=14,
            textColor=GHOST_GRAY,
            alignment=TA_CENTER,
            spaceAfter=30,
        ))
        self.styles.add(ParagraphStyle(
            name="SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=GHOST_BLUE,
            spaceBefore=20,
            spaceAfter=10,
            borderWidth=2,
            borderColor=GHOST_BLUE,
            borderPadding=5,
        ))
        self.styles.add(ParagraphStyle(
            name="SubHeader",
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=GHOST_DARK,
            spaceBefore=12,
            spaceAfter=6,
        ))
        self.styles.add(ParagraphStyle(
            name="BodyText2",
            fontName="Helvetica",
            fontSize=10,
            textColor=GHOST_DARK,
            spaceAfter=6,
            leading=14,
        ))
        self.styles.add(ParagraphStyle(
            name="RiskHigh",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=GHOST_RED,
        ))
        self.styles.add(ParagraphStyle(
            name="RiskMedium",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=GHOST_YELLOW,
        ))
        self.styles.add(ParagraphStyle(
            name="RiskLow",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=GHOST_GREEN,
        ))

    def generate(
        self,
        data: Dict[str, Any],
        output_path: str,
        title: str = "GHOSTMAP Security Report",
    ):
        """
        Generate a PDF report from audit results.

        Args:
            data: Audit results dict (from audit_results.json)
            output_path: Output PDF file path
            title: Report title
        """
        # Ensure output directory
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=25 * mm,
            bottomMargin=25 * mm,
        )

        story = []
        meta = data.get("meta", {})
        summary = data.get("summary", {})
        endpoints = data.get("endpoints", [])

        # =====================================================================
        # COVER PAGE
        # =====================================================================
        story.append(Spacer(1, 80))
        story.append(Paragraph("👻", ParagraphStyle(
            "EmojiTitle", fontName="Helvetica",
            fontSize=60, alignment=TA_CENTER, spaceAfter=20,
        )))
        story.append(Paragraph(title, self.styles["GhostTitle"]))
        story.append(Paragraph(
            f"Generated: {meta.get('timestamp', datetime.now().isoformat())}",
            self.styles["GhostSubtitle"],
        ))
        story.append(Spacer(1, 40))

        # Summary box
        summary_data = [
            ["Total Endpoints", str(summary.get("total_endpoints", len(endpoints)))],
            ["High Risk", str(summary.get("high_risk", 0))],
            ["Medium Risk", str(summary.get("medium_risk", 0))],
            ["Low Risk", str(summary.get("low_risk", 0))],
            ["Documented", str(summary.get("documented", 0))],
        ]
        summary_table = Table(summary_data, colWidths=[200, 150])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), GHOST_BLUE),
            ("TEXTCOLOR", (0, 0), (0, -1), WHITE),
            ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#f0f0f5")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 1, GHOST_GRAY),
            ("ROWHEIGHT", (0, 0), (-1, -1), 30),
        ]))
        story.append(summary_table)
        story.append(PageBreak())

        # =====================================================================
        # EXECUTIVE SUMMARY
        # =====================================================================
        story.append(Paragraph("Executive Summary", self.styles["SectionHeader"]))

        high_count = summary.get("high_risk", 0)
        med_count = summary.get("medium_risk", 0)
        total = summary.get("total_endpoints", len(endpoints))

        story.append(Paragraph(
            f"This security assessment analyzed <b>{total}</b> API endpoints discovered "
            f"through public internet archive analysis. Of these, <b>{high_count}</b> "
            f"were classified as HIGH risk ghost endpoints — undocumented APIs that may "
            f"pose significant security threats.",
            self.styles["BodyText2"],
        ))

        if high_count > 0:
            story.append(Paragraph(
                f"<font color='#f38ba8'><b>⚠️ CRITICAL:</b></font> {high_count} high-risk "
                f"endpoint(s) require immediate attention. These endpoints are undocumented, "
                f"potentially active, and may expose sensitive functionality.",
                self.styles["BodyText2"],
            ))

        story.append(Spacer(1, 20))

        # =====================================================================
        # HIGH RISK ENDPOINTS
        # =====================================================================
        high_risk = [e for e in endpoints if e.get("risk_score", 0) >= 70]
        if high_risk:
            story.append(Paragraph(
                "🔴 High Risk Ghost Endpoints", self.styles["SectionHeader"]
            ))
            story.append(Paragraph(
                f"The following {len(high_risk)} endpoint(s) scored 70 or above "
                f"on the risk scale and require immediate review:",
                self.styles["BodyText2"],
            ))
            story.append(Spacer(1, 10))

            for ep in high_risk[:20]:  # Cap at 20 entries
                self._add_endpoint_block(story, ep, "HIGH")

            if len(high_risk) > 20:
                story.append(Paragraph(
                    f"... and {len(high_risk) - 20} more high-risk endpoints. "
                    f"See the full JSON report for details.",
                    self.styles["BodyText2"],
                ))

            story.append(PageBreak())

        # =====================================================================
        # MEDIUM RISK ENDPOINTS
        # =====================================================================
        med_risk = [e for e in endpoints if 40 <= e.get("risk_score", 0) < 70]
        if med_risk:
            story.append(Paragraph(
                "🟡 Medium Risk Endpoints", self.styles["SectionHeader"]
            ))
            story.append(Paragraph(
                f"{len(med_risk)} endpoint(s) scored between 40-69:",
                self.styles["BodyText2"],
            ))
            story.append(Spacer(1, 10))

            # Table format for medium risk
            table_data = [["Endpoint", "Score", "Factors"]]
            for ep in med_risk[:30]:
                url = ep.get("url", ep.get("normalized_url", ""))
                if len(url) > 60:
                    url = url[:57] + "..."
                score = str(ep.get("risk_score", 0))
                factors = ", ".join(
                    f.get("factor", "") for f in ep.get("risk_factors", [])
                    if isinstance(f, dict)
                )
                if len(factors) > 40:
                    factors = factors[:37] + "..."
                table_data.append([url, score, factors])

            if table_data and len(table_data) > 1:
                t = Table(table_data, colWidths=[250, 50, 170])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), GHOST_BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, GHOST_GRAY),
                    ("ROWHEIGHT", (0, 0), (-1, -1), 20),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#fafafa")]),
                ]))
                story.append(t)

            story.append(PageBreak())

        # =====================================================================
        # RECOMMENDATIONS
        # =====================================================================
        story.append(Paragraph("📋 Recommendations", self.styles["SectionHeader"]))

        recommendations = [
            ("Immediate Actions (High Risk)", [
                "Review and validate all HIGH risk ghost endpoints",
                "Disable or remove unused debug/admin endpoints",
                "Add authentication to any publicly accessible internal APIs",
                "Update API documentation to reflect actual state",
            ]),
            ("Short-term Actions (Medium Risk)", [
                "Audit MEDIUM risk endpoints for business necessity",
                "Implement proper access controls on suspicious endpoints",
                "Remove deprecated endpoints that are still responding",
                "Add rate limiting to undocumented but necessary endpoints",
            ]),
            ("Long-term Recommendations", [
                "Integrate GHOSTMAP into CI/CD pipeline for continuous monitoring",
                "Establish endpoint lifecycle management process",
                "Schedule monthly re-scans to detect regression",
                "Implement API gateway to centralize endpoint management",
            ]),
        ]

        for section_title, items in recommendations:
            story.append(Paragraph(section_title, self.styles["SubHeader"]))
            for item in items:
                story.append(Paragraph(f"• {item}", self.styles["BodyText2"]))
            story.append(Spacer(1, 10))

        # =====================================================================
        # FOOTER
        # =====================================================================
        story.append(Spacer(1, 40))
        story.append(HRFlowable(width="100%", color=GHOST_GRAY))
        story.append(Paragraph(
            f"Report generated by GHOSTMAP v{meta.get('version', '1.0.0')} | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ParagraphStyle("Footer", fontName="Helvetica", fontSize=8,
                           textColor=GHOST_GRAY, alignment=TA_CENTER),
        ))

        # Build PDF
        doc.build(story)
        logger.info(f"PDF report generated: {output_path}")

    def _add_endpoint_block(self, story: list, ep: Dict, risk_level: str):
        """Add a detailed endpoint block to the story."""
        url = ep.get("url", ep.get("normalized_url", "Unknown"))
        score = ep.get("risk_score", 0)
        factors = ep.get("risk_factors", [])

        style_map = {"HIGH": "RiskHigh", "MEDIUM": "RiskMedium", "LOW": "RiskLow"}
        risk_style = style_map.get(risk_level, "BodyText2")

        story.append(Paragraph(
            f"<b>{url}</b>", self.styles["SubHeader"]
        ))
        story.append(Paragraph(
            f"Risk Score: <b>{score}/100</b> | Level: ",
            self.styles["BodyText2"],
        ))

        # Risk factors
        if factors:
            for f in factors:
                if isinstance(f, dict):
                    story.append(Paragraph(
                        f"  → {f.get('factor', '')}: {f.get('detail', '')} (+{f.get('points', 0)} pts)",
                        self.styles["BodyText2"],
                    ))

        # Sources
        sources = ep.get("sources", [])
        if sources:
            story.append(Paragraph(
                f"Sources: {', '.join(sources)}",
                ParagraphStyle("SourceInfo", fontName="Helvetica", fontSize=8, textColor=GHOST_GRAY),
            ))

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", color=colors.HexColor("#e0e0e0")))
        story.append(Spacer(1, 5))
