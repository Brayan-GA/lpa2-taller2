from flask import Flask, render_template, request, send_file, abort
from werkzeug.exceptions import HTTPException
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from io import BytesIO
import os
from xml.sax.saxutils import escape

def texto(valor):
    """Escapa caracteres especiales y convierte saltos de línea para Paragraph."""
    return escape(str(valor)).replace('\n', '<br/>')

app = Flask(__name__)
# Configuración desde variables de entorno (definidas en docker-compose.yml)
BACKEND_URL = os.getenv('API_URL', 'http://backend:8000')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    try:
        id_factura = request.form['id_factura']
        response = requests.get(f'{BACKEND_URL}/facturas/v1/{id_factura}')
        
        if response.status_code != 200:
            abort(404, description="Factura no encontrada")
            
        factura = response.json()
        
        # TODO: Crear buffer y doc para la creación del PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=20*mm, rightMargin=20*mm,
            topMargin=20*mm, bottomMargin=20*mm
        )
        elements = []
        styles = getSampleStyleSheet()

        # TODO: Adicionar el Título, ID
        elements.append(Paragraph("FACTURA", styles['Title']))
        elements.append(Paragraph(f"<b>N° de factura:</b> {texto(factura['numero_factura'])}", styles['Normal']))
        elements.append(Paragraph(f"<b>Fecha de emisión:</b> {texto(factura['fecha_emision'])}", styles['Normal']))
        elements.append(Spacer(1, 8*mm))

        
        # TODO: Agregar Información de la Empresa
        empresa = factura['empresa']
        elements.append(Paragraph("Datos de la Empresa", styles['Heading2']))
        elements.append(Paragraph(f"<b>{texto(empresa['nombre'])}</b>", styles['Normal']))
        elements.append(Paragraph(texto(empresa['direccion']), styles['Normal']))
        elements.append(Paragraph(f"Tel: {texto(empresa['telefono'])}", styles['Normal']))
        elements.append(Paragraph(f"Email: {texto(empresa['email'])}", styles['Normal']))
        elements.append(Spacer(1, 6*mm))

        # TODO: Agregar Información del Cliente
        cliente = factura['cliente']
        elements.append(Paragraph("Datos del Cliente", styles['Heading2']))
        elements.append(Paragraph(f"<b>{texto(cliente['nombre'])}</b>", styles['Normal']))
        elements.append(Paragraph(texto(cliente['direccion']), styles['Normal']))
        elements.append(Paragraph(f"Tel: {texto(cliente['telefono'])}", styles['Normal']))
        elements.append(Spacer(1, 8*mm))

        # TODO: Adicionar el Detalle de la Factura: cantidad, descripción, precio unitario y total
        datos = [['Cant.', 'Descripción', 'Precio unit.', 'Total']]
        for item in factura['detalle']:
            datos.append([
                str(item['cantidad']),
                Paragraph(texto(item['descripcion']), styles['Normal']),
                f"${item['precio_unitario']:,.2f}",
                f"${item['total']:,.2f}",
            ])

        tabla = Table(datos, colWidths=[20*mm, 85*mm, 30*mm, 35*mm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')]),
        ]))
        elements.append(tabla)
        elements.append(Spacer(1, 6*mm))

        # TODO: Adicionar Subtotal, impuesto y Total
        totales = [
            ['Subtotal:', f"${factura['subtotal']:,.2f}"],
            ['IVA (21%):', f"${factura['impuesto']:,.2f}"],
            ['TOTAL:', f"${factura['total']:,.2f}"],
        ]
        tabla_totales = Table(totales, colWidths=[135*mm, 35*mm])
        tabla_totales.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ]))
        elements.append(tabla_totales)

        # Generar el doc y limpiar el buffer
        doc.build(elements)
        buffer.seek(0)
        
        # TODO: Retornar a la página el PDF para visualizar y descargar
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f"factura_{id_factura}.pdf"
        )

    except HTTPException:
        raise

    except requests.exceptions.ConnectionError:
        abort(503, description="Error de conexión con el servidor")
    except Exception as e:
        abort(500, description=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=DEBUG)

