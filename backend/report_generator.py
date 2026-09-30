import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_pdf_report(username: str, influencer: dict, analysis: dict) -> bytes:
    """
    Generates a professional Brand Trust Scorecard PDF using ReportLab.
    Adheres strictly to product principles:
    - Never declares an influencer 'fake'.
    - Communicates explainable detection signals, anomaly metrics, and disclaimers.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Define custom color palette
    c_primary = colors.HexColor("#0f172a")      # Slate 900
    c_accent = colors.HexColor("#3b82f6")       # Blue 500
    c_secondary = colors.HexColor("#1e293b")    # Slate 800
    c_text_dark = colors.HexColor("#0f172a")
    c_text_muted = colors.HexColor("#64748b")   # Slate 500
    c_border = colors.HexColor("#e2e8f0")       # Slate 200
    c_card_bg = colors.HexColor("#f8fafc")      # Slate 50
    c_risk_elevated = colors.HexColor("#dc2626")# Red 600
    c_risk_moderate = colors.HexColor("#d97706")# Amber 600
    c_risk_low = colors.HexColor("#16a34a")     # Green 600

    # Custom typography styles
    header_title_style = ParagraphStyle(
        "HeaderTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.white
    )
    header_sub_style = ParagraphStyle(
        "HeaderSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#94a3b8")
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=c_secondary,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_text_dark
    )
    body_muted = ParagraphStyle(
        "ReportBodyMuted",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_text_muted
    )
    bold_label = ParagraphStyle(
        "ReportBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=c_text_dark
    )
    score_big = ParagraphStyle(
        "ScoreBig",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=32,
        textColor=c_accent,
        alignment=1
    )
    score_sub = ParagraphStyle(
        "ScoreSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=c_text_muted,
        alignment=1
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=11,
        textColor=c_text_muted
    )

    story = []

    # ==========================================
    # 1. HEADER BANNER
    # ==========================================
    header_data = [
        [
            Paragraph("EngagementPodGuard", header_title_style),
            Paragraph("AUDIENCE AUTHENTICITY INTELLIGENCE<br/>BRAND TRUST SCORECARD", header_sub_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[320, 220])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_primary),
        ("ALIGN", (0, 0), (0, 0), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    # ==========================================
    # 2. PROFILE & METRICS SUMMARY
    # ==========================================
    followers = influencer.get("followers", 100000)
    following = influencer.get("following", 850)
    posts_count = influencer.get("posts_count", 20)
    auth_score = analysis.get("authenticity_score", 68.5)
    overall_risk = analysis.get("overall_risk", 31.5)
    auth_label = analysis.get("authenticity_label", "MODERATE RISK")
    confidence_text = analysis.get("confidence", "High (1,000 comments / 20 posts)")

    risk_color = c_risk_elevated if overall_risk > 65 else (c_risk_moderate if overall_risk > 30 else c_risk_low)

    auth_pill_style = ParagraphStyle(
        "AuthPill",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=risk_color,
        alignment=1
    )

    profile_card_data = [
        [
            Paragraph(f"<b>Creator:</b> @{username}", bold_label),
            Paragraph(f"<b>Followers:</b> {followers:,}", body_style),
            Paragraph(f"<b>Following:</b> {following:,}", body_style),
            Paragraph(f"<b>Analyzed Posts:</b> {posts_count}", body_style),
        ],
        [
            Paragraph(f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body_muted),
            Paragraph(f"<b>Comments Analyzed:</b> {analysis.get('total_comments', 1000):,}", body_muted),
            Paragraph(f"<b>Confidence:</b> {analysis.get('confidence_score', 92)}%", body_muted),
            Paragraph("<b>Data Origin:</b> Synthetic Demo", body_muted),
        ]
    ]
    profile_table = Table(profile_card_data, colWidths=[140, 130, 130, 140])
    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_card_bg),
        ("BOX", (0, 0), (-1, -1), 1, c_border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 14))

    # ==========================================
    # 3. SCORE OVERVIEW TABLE
    # ==========================================
    score_overview_data = [
        [
            Paragraph(f"<b>{auth_score}</b>", score_big),
            Paragraph(f"<b>{overall_risk}%</b>", score_big),
            Paragraph(f"<b>{auth_label}</b>", auth_pill_style),
        ],
        [
            Paragraph("AUDIENCE AUTHENTICITY SCORE (/100)", score_sub),
            Paragraph("AGGREGATE RISK INDEX", score_sub),
            Paragraph("ENGAGEMENT RISK STATUS", score_sub),
        ]
    ]
    score_table = Table(score_overview_data, colWidths=[180, 180, 180])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_card_bg),
        ("BOX", (0, 0), (-1, -1), 1, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # ==========================================
    # 4. DETECTION SIGNALS BREAKDOWN
    # ==========================================
    story.append(Paragraph("Detection Signals Breakdown", section_heading))

    sig_data = [
        [
            Paragraph("<b>Signal Category</b>", bold_label),
            Paragraph("<b>Calculated Score</b>", bold_label),
            Paragraph("<b>Prototype Weight</b>", bold_label),
            Paragraph("<b>Observed Pattern & Assessment</b>", bold_label)
        ],
        [
            Paragraph("Engagement Anomaly", bold_label),
            Paragraph(f"{analysis.get('engagement_risk', 42.0)}%", body_style),
            Paragraph("25%", body_muted),
            Paragraph(f"Avg likes: {analysis.get('avg_likes', 0):,} | Avg comments: {analysis.get('avg_comments', 0):,} | Comment/like ratio: {analysis.get('comment_to_like_ratio', 0)}%", body_style)
        ],
        [
            Paragraph("Comment Semantic Similarity", bold_label),
            Paragraph(f"{analysis.get('semantic_risk', 78.0)}%", body_style),
            Paragraph("25%", body_muted),
            Paragraph(f"{analysis.get('suspicious_comments', 500)} comments share matching phrasing and recurring templates across media posts.", body_style)
        ],
        [
            Paragraph("Timestamp Coordination", bold_label),
            Paragraph(f"{analysis.get('timing_risk', 81.0)}%", body_style),
            Paragraph("25%", body_muted),
            Paragraph("Synchronized comment submissions concentrated within rapid ≤45 second arrival intervals.", body_style)
        ],
        [
            Paragraph("Account Coordination", bold_label),
            Paragraph(f"{analysis.get('coordination_risk', 75.0)}%", body_style),
            Paragraph("25%", body_muted),
            Paragraph(f"{analysis.get('suspicious_accounts', 100)} accounts identified operating in coordinated pods across multiple posts.", body_style)
        ]
    ]

    sig_table = Table(sig_data, colWidths=[140, 80, 70, 250])
    sig_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_card_bg),
        ("BOX", (0, 0), (-1, -1), 1, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 14))

    # ==========================================
    # 5. SUSPICIOUS POD CLUSTERS SECTION
    # ==========================================
    clusters = analysis.get("clusters", [])
    if clusters:
        story.append(Paragraph(f"Coordinated Engagement Clusters ({len(clusters)} Detected)", section_heading))
        cluster_rows = [
            [
                Paragraph("<b>Cluster Name</b>", bold_label),
                Paragraph("<b>Accounts</b>", bold_label),
                Paragraph("<b>Comments</b>", bold_label),
                Paragraph("<b>Similarity</b>", bold_label),
                Paragraph("<b>Timing</b>", bold_label),
                Paragraph("<b>Risk Score</b>", bold_label),
            ]
        ]
        for c in clusters[:5]:
            cluster_rows.append([
                Paragraph(c.get("cluster_name", "Pod Cluster"), bold_label),
                Paragraph(str(c.get("account_count", 20)), body_style),
                Paragraph(str(c.get("comment_count", 100)), body_style),
                Paragraph(f"{c.get('semantic_similarity', 91.5)}%", body_style),
                Paragraph(f"{c.get('timing_score', 86.0)}%", body_style),
                Paragraph(f"{c.get('risk_score', 90.5)}%", bold_label),
            ])

        cluster_table = Table(cluster_rows, colWidths=[140, 80, 80, 80, 80, 80])
        cluster_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), c_card_bg),
            ("BOX", (0, 0), (-1, -1), 1, c_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(cluster_table)
        story.append(Spacer(1, 14))

    # ==========================================
    # 6. EXPLAINABILITY EVIDENCE
    # ==========================================
    evidence_items = analysis.get("evidence", [])
    if evidence_items:
        story.append(Paragraph("Explainable Findings & Evidence", section_heading))
        evidence_rows = []
        for ev in evidence_items[:4]:
            sev_badge = ev.get("severity", "medium").upper()
            title = ev.get("title", "Signal")
            msg = ev.get("message", "")
            evidence_rows.append([
                Paragraph(f"<b>[{sev_badge}] {title}</b><br/>{msg}", body_style)
            ])
        ev_table = Table(evidence_rows, colWidths=[540])
        ev_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), c_card_bg),
            ("BOX", (0, 0), (-1, -1), 1, c_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_border),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(ev_table)
        story.append(Spacer(1, 14))

    # ==========================================
    # 7. METHODOLOGY & DISCLAIMER
    # ==========================================
    story.append(Paragraph("Methodology & Scoring Philosophy", section_heading))
    methodology_text = (
        "EngagementPodGuard evaluates four orthogonal intelligence dimensions: engagement variance, "
        "semantic comment redundancy (TF-IDF and sentence embeddings), temporal arrival burst clustering, "
        "and account co-occurrence graph topology using NetworkX. Transparent weights (25% each) compute the composite risk index."
    )
    story.append(Paragraph(methodology_text, body_muted))
    story.append(Spacer(1, 8))

    disclaimer_text = (
        "<b>Important Disclaimer:</b> This report identifies statistical and behavioral patterns associated with "
        "potentially coordinated engagement. It does not independently establish that an account, influencer, or comment "
        "is fraudulent or violating platform terms of service. Results are provided for preliminary brand safety and audience due diligence."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    # Build document
    doc.build(story)
    return buffer.getvalue()
