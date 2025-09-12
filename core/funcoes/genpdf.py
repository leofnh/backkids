from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
import io
from ..models import ProdutoVendido

def generate_receipt_pdf(sale):
    buffer = io.BytesIO()
    venda = ProdutoVendido.objects.filter(id=sale)
    dados_venda = ProdutoVendido.objects.get(id=sale)

    # Definir a largura da página como 80mm (largura comum para impressoras térmicas)
    doc = SimpleDocTemplate(buffer, pagesize=(80 * mm, 200 * mm))
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles['BodyText']
    normal_style.alignment = 0
    
    # Adicionar o cabeçalho da empresa
    elements.append(Paragraph("<b>Paula Kids</b>", normal_style))
    elements.append(Paragraph("Rua Getulio Vargas, 48 - Centro", normal_style))
    elements.append(Paragraph("São Domingos do Prata - MG", normal_style))
    elements.append(Paragraph("CNPJ: 30.393.196/0001-81", normal_style))
    elements.append(Spacer(1, 12))

    # Informações da venda
    elements.append(Paragraph(f"<b>Cliente:</b> Teste", normal_style))
    elements.append(Paragraph(f"<b>Data:</b> {dados_venda.cadastro}", normal_style))
    elements.append(Paragraph(f"<b>Vendedor:</b> Teste", normal_style))
    elements.append(Spacer(1, 12))

    # Tabela dos itens vendidos
    data = [["Código", "Produto", "Qtd", "V. Unit", "V. Total"]]
    for item in venda:
        data.append([
            item.codigo, 
            item.marca, 
            item.unidades, 
            f"R$ {item.preco:.2f}", 
            f"R$ {item.preco:.2f}"
        ])

    # Ajustar a largura das colunas
    col_widths = [1.5 * cm]

    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 6),  # Ajustar tamanho da fonte
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),        
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),      
        
    ]))
    elements.append(table)

    # Total
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Total:</b> R$ {dados_venda.preco:.2f}", normal_style))

    # Finalizar o documento
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_receipt_pdf2(sale):
    buffer = io.BytesIO()

    venda = ProdutoVendido.objects.filter(id=sale)
    dados_venda = ProdutoVendido.objects.get(id=sale)

    # Define line breaks and centering commands for ESC/POS
    line_break = b"\n"
    center = b"\x1b@a"  # ESC @ a - center alignment

    # Header
    buffer.write(center + b"Paula Kids\n")
    buffer.write(center + b"Rua Getulio Vargas, 48 - Centro\n")
    buffer.write(center + b"Sao Domingos do Prata - MG\n")
    buffer.write(center + b"CNPJ: 30.393.196/0001-81\n\n")

    # Customer Information
    buffer.write(b"Cliente: Teste\n")
    buffer.write(f"Data: {dados_venda.cadastro}\n".encode())
    buffer.write(b"Vendedor: Teste\n\n")

    # Item table header
    buffer.write(b"Codigo  Produto     Qtd  V. Unit  V. Total\n")
    buffer.write(b"------- ---------- ---- -------- --------\n")

    # Items
    for item in venda:
        codigo = f"{item.codigo:<5}"  # Pad left with spaces to fit 5 characters
        produto = f"{item.marca[:15]:<15}"  # Truncate product name to 15 characters
        qtd = f"{item.unidades:<4}"
        preco_unitario = f"R$ {item.preco:.2f}"
        preco_total = f"R$ {item.preco:.2f}"
        buffer.write(
            f"{codigo} {produto} {qtd} {preco_unitario} {preco_total}\n".encode()
        )

    buffer.write(line_break)

    # Total
    #buffer.write(b"Total: R$ {:.2f}\n\n".format(dados_venda.preco))

    receipt_text = buffer.getvalue()    
    buffer.close()
    print(f"OXI:")
    print(receipt_text)
    return receipt_text