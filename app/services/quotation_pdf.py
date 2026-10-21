"""报价单 PDF 生成（ReportLab）。"""

import os
import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import FONT_PATH

# 🌟 1. 先注册 ReportLab 自带的中文字体作为绝对安全的兜底
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

_FONTS_READY = False

def register_fonts() -> bool:
    global _FONTS_READY
    if _FONTS_READY:
        return True
    try:
        if os.path.exists(FONT_PATH):
            # 🌟 2. 绝不使用 customchinese 这个名字，换成不可能冲突的 TK_CN_Font
            font_name = "TK_CN_Font"
            pdfmetrics.registerFont(TTFont(font_name, str(FONT_PATH), subfontIndex=0))
            
            # 🌟 3. 强制把所有的变体绑定给自己，彻底杀掉映射报错
            pdfmetrics.registerFontFamily(
                font_name,
                normal=font_name,
                bold=font_name,
                italic=font_name,
                boldItalic=font_name
            )
            print(f"✅ 成功完美注册自定义中文字体: {FONT_PATH}")
            _FONTS_READY = True
        else:
            print(f"⚠️ 未在项目根目录下找到字体文件: {FONT_PATH}，将使用 STSong-Light 兜底。")
    except Exception as e:
        print(f"⚠️ 字体注册异常，将使用 STSong-Light 兜底: {e}")
    return _FONTS_READY

register_fonts()

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
    
    # 🌟 4. 根据注册状态智能选择字体，若有自定义用自定义，否则用自带的 STSong-Light
    if lang == "zh":
        active_font = "TK_CN_Font" if _FONTS_READY else "STSong-Light"
    else:
        active_font = "Helvetica"
    
    try:
        doc = SimpleDocTemplate(
            pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=100,
        )
        story = []

        comp_title = "TOSTIYK (TK) - AUTOPARTES VENEZUELA"
        
        # ─────────── 样式定义 ───────────
        title_style = ParagraphStyle(
            "TopTitle", fontSize=14, leading=18,
            textColor=colors.HexColor("#0f172a"), fontName="Helvetica-Bold",
        )
        right_meta_style = ParagraphStyle(
            "TopRight", fontSize=9.5, leading=13,
            alignment=2, textColor=colors.HexColor("#1e293b"), fontName=active_font,
        )
        box_style = ParagraphStyle(
            "BoxStyle", fontSize=9.5, leading=15,
            textColor=colors.HexColor("#1e293b"), fontName=active_font,
        )
        
        # 🌟 5. 关键修复：顶部副标题不再使用 Paragraph，彻底避免解析报错
        subtitle_table_data = [
            [Paragraph(comp_title, title_style), Paragraph(f"{t['invoice_no']}: {quotation_no}", right_meta_style)],
            [t['comp_subtitle'], f"{t['date']}: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"]
        ]
        t_top = Table(subtitle_table_data, colWidths=[310, 230])
        t_top.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("FONTNAME", (0, 1), (0, 1), active_font), # 副标题直接使用表格原生渲染
            ("FONTNAME", (1, 0), (1, 1), active_font),
            ("FONTSIZE", (0, 1), (0, 1), 8.5),
            ("TEXTCOLOR", (0, 1), (0, 1), colors.HexColor("#64748b")),
            ("ALIGN", (1, 0), (1, 1), "RIGHT"),
        ]))
        story.append(t_top)
        story.append(Spacer(1, 12))

        # ─────────── 客户与公司信息 ───────────
        company_info_content = [
            Paragraph(t['company_info'], box_style),
            Paragraph(f"• {t['vendor']}: Elias", box_style),
            Paragraph(f"• {t['seller_phone']}: +58 412-0000000", box_style),
            Paragraph(f"• {t['company_phone']}: +58 271-0000000", box_style),
            Paragraph(f"• {t['address']}: Valera, Estado Trujillo, Venezuela", box_style),
        ]

        actual_client_name = client_name if client_name != "Cliente General" else t["default_client"]
        actual_client_addr = client_obj.address if client_obj and client_obj.address else t["default_address"]
        
        client_info_content = [
            Paragraph(t['client_info'], box_style),
            Paragraph(f"• {t['client']}: {actual_client_name}", box_style),
            Paragraph(f"• {t['phone']}: {client_obj.phone if client_obj and client_obj.phone else 'N/A'}", box_style),
            Paragraph(f"• {t['address']}: {actual_client_addr}", box_style),
        ]

        t_info = Table([[company_info_content, client_info_content]], colWidths=[270, 270])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 16))

        # ─────────── 商品明细表 ───────────
        th_style = ParagraphStyle(
            "THStyle", fontSize=9.5, leading=12,
            textColor=colors.HexColor("#0f172a"), fontName=active_font,
        )
        th_right_style = ParagraphStyle(
            "THRightStyle", fontSize=9.5, leading=12,
            alignment=2, textColor=colors.HexColor("#0f172a"), fontName=active_font,
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
            "TDStyle", fontSize=9.5, leading=13,
            textColor=colors.HexColor("#1e293b"), fontName=active_font,
        )
        td_right_style = ParagraphStyle(
            "TDRightStyle", fontSize=9.5, leading=13,
            alignment=2, textColor=colors.HexColor("#1e293b"), fontName=active_font,
        )

        for item in items:
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
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        story.append(t_items)

        # ─────────── 底部合计 ───────────
        def draw_fixed_footer(canvas, document):
            canvas.saveState()
            total_left_style = ParagraphStyle(
                "TotalLeft", fontSize=11, leading=15,
                textColor=colors.HexColor("#0f172a"), fontName=active_font,
            )
            total_right_style = ParagraphStyle(
                "TotalRight", fontSize=11, leading=15,
                alignment=2, textColor=colors.HexColor("#059669"), fontName=active_font,
            )

            d_total_usd = Decimal(str(total_usd)).quantize(Decimal("0.01"))
            d_total_bs = Decimal(str(total_bs)).quantize(Decimal("0.01"))

            t_total = Table(
                [[
                    Paragraph(f"{t['total_usd']}: ${d_total_usd:.2f}", total_left_style),
                    Paragraph(f"{t['total_ves']}: Bs. {d_total_bs:,.2f}", total_right_style),
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