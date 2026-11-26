// Métodos auxiliares para la interfaz Web

// Elementos de la página (definidos en index.html)
const formulario = document.getElementById('form-factura');
const inputFactura = document.getElementById('id_factura');
const btnGenerar = document.getElementById('btn-generar');
const mensajeError = document.getElementById('mensaje-error');
const vistaPrevia = document.getElementById('vista-previa');
const visorPdf = document.getElementById('visor-pdf');
const btnDescargar = document.getElementById('btn-descargar');

// URL temporal del PDF que se está mostrando
let urlPdfActual = null;

// Mensajes según el código de error que devuelva el servidor
const MENSAJES_ERROR = {
    404: 'La factura no fue encontrada. Verifica el número e intenta de nuevo.',
    503: 'No hay conexión con el servidor de facturas. Intenta más tarde.',
};

function mostrarError(mensaje) {
    mensajeError.textContent = mensaje;
    mensajeError.hidden = false;
    vistaPrevia.hidden = true;
}

function ocultarError() {
    mensajeError.textContent = '';
    mensajeError.hidden = true;
}

function setCargando(cargando) {
    btnGenerar.disabled = cargando;
    btnGenerar.textContent = cargando ? 'Generando...' : 'Generar Factura';
}

function liberarPdfAnterior() {
    if (urlPdfActual) {
        URL.revokeObjectURL(urlPdfActual);
        urlPdfActual = null;
    }
}

function mostrarPdf(blob, idFactura) {
    liberarPdfAnterior();
    urlPdfActual = URL.createObjectURL(blob);

    visorPdf.src = urlPdfActual;
    btnDescargar.href = urlPdfActual;
    btnDescargar.download = `factura_${idFactura}.pdf`;

    vistaPrevia.hidden = false;
    vistaPrevia.scrollIntoView({ behavior: 'smooth' });
}

formulario.addEventListener('submit', async (evento) => {
    // Evita que la página se recargue al enviar el formulario
    evento.preventDefault();

    const idFactura = inputFactura.value.trim();
    if (!idFactura) {
        mostrarError('Ingresa un número de factura.');
        return;
    }

    ocultarError();
    setCargando(true);

    try {
        const datos = new FormData(formulario);
        datos.set('id_factura', idFactura);

        const respuesta = await fetch(formulario.action, {
            method: 'POST',
            body: datos,
        });

        if (!respuesta.ok) {
            throw new Error(
                MENSAJES_ERROR[respuesta.status] ||
                `Error al generar la factura (código ${respuesta.status}).`
            );
        }

        const pdf = await respuesta.blob();
        mostrarPdf(pdf, idFactura);
    } catch (error) {
        // fetch lanza TypeError cuando no logra conectarse con el frontend
        if (error instanceof TypeError) {
            mostrarError('No se pudo conectar con el servidor. Revisa que la aplicación esté en ejecución.');
        } else {
            mostrarError(error.message);
        }
    } finally {
        setCargando(false);
    }
});
