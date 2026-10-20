"""报价单 PDF 生成（ReportLab）。"""

import os
import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP # 🌟 引入 Decimal
from typing import Optional, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import FONT_PATH

# ──────────────────── 中文字体注册 ────────────────────
_FONTS_READY = False


def register_fonts() -> bool:
    global _FONTS_READY
    if _FONTS_READY:
        return True
    try:
        if os.path.exists(FONT_PATH):
            for family in ("CustomChinese", "CustomChinese-Bold",
                           "CustomChinese-Italic", "CustomChinese-BoldItalic"):
                pdfmetrics.registerFont(TTFont(family, str(FONT_PATH), subfontIndex=0))
            print(f"✅ 成功完美注册华文细黑全家桶: {FONT_PATH}")
            _FONTS_READY = True
        else:
            print(f"⚠️ 未在项目根目录下找到字体文件: {FONT_PATH}")
    except Exception as e:
        print(f"⚠️ 字体注册异常: {e}")
    return _FONTS_READY


register_fonts()

# ──────────────────────────── 多语言文案 ────────────────────────────
TEXTS = {
    "es": {
        "comp_subtitle": "Valera, Trujillo - Venezuela",
        "invoice_no": "Comprobante Nro", "date": "Fecha", "company_info": "[ Información de la Empresa ]",
        "vendor": "Vendedor", "seller_phone": "Telf. Vendedor", "company_phone": "Telf. Empresa",
        "address": "Dirección", "client_info": "[ Datos del Cliente ]", "client": "Cliente",
        "phone": "Teléfono", "default_client": "Cliente General", "default_address": "Valera / Local",
        "sku": "SKU / OEM", "desc": "Descripción", "unit_price": "P. Unit", "qty": "Cant.",
        "subtotal": "Subtotal", "total_usd": "Total USD", "total_ves": "Total VES (BCV)",
        "thanks": "¡Gracias por su preferencia! - Tostiyk (TK) Repuestos para Vehículos Pesados y Livianos.",
    },
    "zh": {
        "comp_subtitle": "委内瑞拉 特鲁希略省 巴莱拉", "invoice_no": "单号", "date": "日期",
        "company_info": "[ 公司信息 ]", "vendor": "销售员", "seller_phone": "销售电话",
        "company_phone": "公司电话", "address": "地址", "client_info": "[ 客户档案 ]",
        "client": "客户名称", "phone": "联系电话", "default_client": "散客 / 默认客户",
        "default_address": "委内瑞拉本地", "sku": "SKU / OEM", "desc": "商品描述",
        "unit_price": "单价", "qty": "数量", "subtotal": "小计", "total_usd": "总计 USD",
        "total_ves": "总计 VES (BCV)", "thanks": "感谢惠顾！- Tostiyk (TK) 重型与轻型汽车配件专营。",
    },
    "en": {
        "comp_subtitle": "Valera, Trujillo - Venezuela", "invoice_no": "Invoice No", "date": "Date",
        "company_info": "[ Company Information ]", "vendor": "Salesperson", "seller_phone": "Sales Phone",
        "company_phone": "Company Phone", "address": "Address", "client_info": "[ Client Information ]",
        "client": "Client", "phone": "Phone", "default_client": "General Client",
        "default_address": "Valera / Local", "sku": "SKU / OEM", "desc": "Description",
        "unit_price": "Unit Price", "qty": "Qty", "subtotal": "Subtotal", "total_usd": "Total USD",
        "total_ves": "Total VES (BCV)", "thanks": "Thank you for your business! - Tostiyk (TK) Heavy & Light Duty Auto Parts.",
    },
}


def normalize_lang(raw_lang: Optional[str]) -> str:
    if isinstance(raw_lang, str) and ("zh" in raw_lang.lower() or "cn" in raw_lang.lower()):
        return "zh"
    if isinstance(raw_lang, str) and "en" in raw_lang.lower():
        return "en"
    return "es"


def build_quotation_pdf(
    *,
    pdf_path: str,
    quotation_no: str,
    client_name: str,
    client_obj,
    items: Sequence,
    total_usd: float,
    total_bs: float,
    lang: str,
) -> None:
    
    t = TEXTS.get(lang, TEXTS["es"])
    active_font = "CustomChinese" if lang == "zh" else "Helvetica"
    active_bold_font = "CustomChinese" if lang == "zh" else "Helvetica-Bold"

    try:
        doc = SimpleDocTemplate(
            pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=100,
        )
        styles = getSampleStyleSheet()
        story = []

        comp_title = "TOSTIYK (TK) - AUTOPARTES VENEZUELA"
        title_style = ParagraphStyle(
            "TopTitle", parent=styles["Heading1"], fontSize=14, leading=18,
            textColor=colors.HexColor("#0f172a"), fontName=active_bold_font,
        )
        right_meta_style = ParagraphStyle(
            "TopRight", parent=styles["Normal"], fontSize=9.5, leading=13,
            alignment=2, textColor=colors.HexColor("#1e293b"), fontName=active_font,
        )

        top_table_data = [
            [
                Paragraph(
                    f"<b>{comp_title}</b><br/><font size=8.5 color='#64748b'>{t['comp_subtitle']}</font>", title_style,
                ),
                Paragraph(
                    f"<b>{t['invoice_no']}:</b> {quotation_no}<br/>"
                    f"<b>{t['date']}:</b> {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}", right_meta_style,
                ),
            ]
        ]
        t_top = Table(top_table_data, colWidths=[310, 230])
        t_top.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_top)
        story.append(Spacer(1, 10))

        box_style = ParagraphStyle(
            "BoxStyle", parent=styles["Normal"], fontSize=9.5, leading=14,
            textColor=colors.HexColor("#1e293b"), fontName=active_font,
        )

        company_info_html = (
            f"<b>{t['company_info']}</b><br/>"
            f"• {t['vendor']}: Elias<br/>"
            f"• {t['seller_phone']}: +58 412-0000000<br/>"
            f"• {t['company_phone']}: +58 271-0000000<br/>"
            f"• {t['address']}: Valera, Estado Trujillo, Venezuela"
        )

        actual_client_name = client_name if client_name != "Cliente General" else t["default_client"]
        actual_client_addr = client_obj.address if client_obj and client_obj.address else t["default_address"]

        client_info_html = (
            f"<b>{t['client_info']}</b><br/>"
            f"• {t['client']}: {actual_client_name}<br/>"
            f"• {t['phone']}: {client_obj.phone if client_obj and client_obj.phone else 'N/A'}<br/>"
            f"• {t['address']}: {actual_client_addr}"
        )

        t_info = Table([[Paragraph(company_info_html, box_style), Paragraph(client_info_html, box_style)]],
                       colWidths=[270, 270])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 14))

        th_style = ParagraphStyle(
            "THStyle", parent=styles["Normal"], fontSize=9.5, leading=12,
            textColor=colors.HexColor("#0f172a"), fontName=active_bold_font,
        )
        th_right_style = ParagraphStyle(
            "THRightStyle", parent=styles["Normal"], fontSize=9.5, leading=12,
            alignment=2, textColor=colors.HexColor("#0f172a"), fontName=active_bold_font,
        )

        table_data = [[
            Paragraph(t["sku"], th_style),
            Paragraph(t["desc"], th_style),
            Paragraph(t["unit_price"], th_right_style),
            Paragraph(t["qty"], th_right_style),
            Paragraph(t["subtotal"], th_right_style),
            Paragraph(t["total_usd"], th_right_style),
        ]]

        td_style = ParagraphStyle(
            "TDStyle", parent=styles["Normal"], fontSize=9.5, leading=13,
            textColor=colors.HexColor("#1e293b"), fontName=active_font,
        )
        td_right_style = ParagraphStyle(
            "TDRightStyle", parent=styles["Normal"], fontSize=9.5, leading=13,
            alignment=2, textColor=colors.HexColor("#1e293b"), fontName=active_font,
        )

        for item in items:
            # 🌟 核心修复：在生成 PDF 内容时，也必须使用 Decimal 做计算，防止打印出 19.9999
            d_price = Decimal(str(item.price))
            d_qty = Decimal(str(item.quantity))
            subtotal = (d_price * d_qty).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if lang == "zh":
                clean_name = item.name
            else:
                clean_name = re.sub(r"[\u4e00-\u9fa5]", "", item.name).strip()
                if not clean_name:
                    clean_name = f"Repuesto OEM {item.oem}"

            table_data.append([
                Paragraph(str(item.oem), td_style),
                Paragraph(clean_name, td_style),
                Paragraph(f"${d_price:.2f}", td_right_style),
                Paragraph(str(d_qty), td_right_style),
                Paragraph(f"${subtotal:.2f}", td_right_style),
                Paragraph(f"${subtotal:.2f}", td_right_style),
            ])

        t_items = Table(table_data, colWidths=[100, 170, 65, 45, 80, 80])
        t_items.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_items)

        def draw_fixed_footer(canvas, document):
            canvas.saveState()
            total_left_style = ParagraphStyle(
                "TotalLeft", parent=styles["Normal"], fontSize=11, leading=15,
                textColor=colors.HexColor("#0f172a"), fontName=active_bold_font,
            )
            total_right_style = ParagraphStyle(
                "TotalRight", parent=styles["Normal"], fontSize=11, leading=15,
                alignment=2, textColor=colors.HexColor("#059669"), fontName=active_bold_font,
            )

            # 🌟 格式化展示，同样避免浮点误差
            d_total_usd = Decimal(str(total_usd)).quantize(Decimal("0.01"))
            d_total_bs = Decimal(str(total_bs)).quantize(Decimal("0.01"))

            t_total = Table(
                [[
                    Paragraph(f"<b>{t['total_usd']}:</b> ${d_total_usd:.2f}", total_left_style),
                    Paragraph(f"<b>{t['total_ves']}:</b> Bs. {d_total_bs:,.2f}", total_right_style),
                ]],
                colWidths=[270, 270],
            )
            t_total.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LINEABOVE", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
            ]))

            t_total.wrap(540, 100)
            t_total.drawOn(canvas, 36, 75)

            canvas.setFont(active_font, 8.5)
            canvas.setFillColor(colors.HexColor("#64748b"))
            canvas.drawCentredString(612 / 2.0, 50, t["thanks"])
            canvas.restoreState()

        doc.build(story, onFirstPage=draw_fixed_footer, onLaterPages=draw_fixed_footer)
    except Exception as e:
        print(f"PDF 生成异常: {e}")