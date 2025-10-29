# wsIntegracionDetalleServicios.py
"""
Módulo de integración SOAP con el servicio remoto:
WS_GestionIntegracionDetalleEspacio.asmx
Autor: Carlos Quitus
Descripción:
    Contiene funciones que interpretan los métodos SOAP
    en Python, para ser reutilizados desde las vistas Django.
"""

import logging
import xml.etree.ElementTree as ET
from zeep import Client
from zeep.helpers import serialize_object
import logging
import requests

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
WSDL_URL = "https://realdecuencaintegracion-abachrhfgzcrb0af.canadacentral-01.azurewebsites.net/WS_GestionIntegracionDetalleEspacio.asmx?WSDL"
SOAP_URL_seleccionarEspaciosDetalladosPorPaginas = "https://realdecuencaintegracion-abachrhfgzcrb0af.canadacentral-01.azurewebsites.net/WS_GestionIntegracionDetalleEspacio.asmx"
SOAP_ACTION_seleccionarEspaciosDetalladosPorPaginas = "http://tempuri.org/seleccionarEspaciosDetalladosPorPaginas"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================================================
# FUNCIÓN: obtenerDetalleServicio
# ======================================================
def obtenerDetalleServicio(id: int) -> dict:
    """
    Obtiene el detalle de un servicio (espacio) por su ID desde el servicio SOAP.

    Parámetros:
        id (int): Identificador del espacio.

    Retorna:
        dict: Un diccionario con los datos del espacio. Si ocurre un error o no se encuentra,
              devuelve un diccionario con la clave "error".
    """
    try:
        # Crear cliente SOAP
        client = Client(WSDL_URL)

        # Llamar al método remoto
        logger.info(f"Llamando a obtenerDetalleServicio con id={id}")
        response = client.service.obtenerDetalleServicio(id=id)

        # Convertir el resultado a diccionario Python
        result = serialize_object(response)

        # Validar respuesta
        if not result:
            return {"error": f"No se encontró el servicio con ID {id}"}

        # Estructura limpia (según el WSDL)
        detalle = {
            "Id": result.get("Id"),
            "Nombre": result.get("Nombre"),
            "NombreHotel": result.get("NombreHotel"),
            "NombreTipoServicio": result.get("NombreTipoServicio"),
            "NombreTipoAlimentacion": result.get("NombreTipoAlimentacion"),
            "Moneda": result.get("Moneda"),
            "CostoDiario": result.get("CostoDiario"),
            "Ubicacion": result.get("Ubicacion"),
            "DescripcionDelLugar": result.get("DescripcionDelLugar"),
            "Capacidad": result.get("Capacidad"),
            "Puntuacion": result.get("Puntuacion"),
            "Amenidades": result.get("Amenidades") or [],
            "Politicas": result.get("Politicas") or [],
            "Imagenes": result.get("Imagenes") or [],
            "EsActivo": result.get("EsActivo", False),
        }

        return detalle

    except Exception as ex:
        logger.error(f"Error en obtenerDetalleServicio({id}): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: obtenerHoteles
# ======================================================
def obtenerHoteles() -> list:
    """
    Obtiene un catálogo con los nombres de hoteles activos desde el servicio SOAP.

    Retorna:
        list: Lista de strings con los nombres de los hoteles.
              Si ocurre un error, retorna una lista vacía o un diccionario con clave 'error'.
    """
    try:
        # Crear cliente SOAP
        client = Client(WSDL_URL)

        logger.info("Llamando a obtenerHoteles()")

        # Llamada al método remoto (sin parámetros)
        response = client.service.obtenerHoteles()

        # Convertir el resultado SOAP a lista de Python
        result = serialize_object(response)

        # Validar resultado
        if not result:
            logger.warning("No se encontraron hoteles activos en la respuesta SOAP.")
            return []

        # Normalizar (en caso de recibir un único string o lista)
        if isinstance(result, str):
            return [result]

        if isinstance(result, list):
            return [str(h).strip() for h in result if h]

        # Caso inesperado
        logger.warning(f"Formato inesperado en la respuesta: {result}")
        return []

    except Exception as ex:
        logger.error(f"Error en obtenerHoteles(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: obtenerUbicaciones
# ======================================================
def obtenerUbicaciones() -> list:
    """
    Obtiene un catálogo con las ubicaciones únicas de los espacios activos desde el servicio SOAP.

    Retorna:
        list: Lista de strings con las ubicaciones.
              Si ocurre un error, retorna una lista vacía o un diccionario con clave 'error'.
    """
    try:
        # Crear cliente SOAP
        client = Client(WSDL_URL)

        logger.info("Llamando a obtenerUbicaciones()")

        # Llamada al método remoto (sin parámetros)
        response = client.service.obtenerUbicaciones()

        # Convertir resultado SOAP → lista de Python
        result = serialize_object(response)

        # Validar respuesta
        if not result:
            logger.warning("No se encontraron ubicaciones en la respuesta SOAP.")
            return []

        # Normalizar (si viene un string único o una lista de strings)
        if isinstance(result, str):
            return [result]

        if isinstance(result, list):
            return [str(u).strip() for u in result if u]

        logger.warning(f"Formato inesperado en la respuesta SOAP: {result}")
        return []

    except Exception as ex:
        logger.error(f"Error en obtenerUbicaciones(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: seleccionarEspaciosDetalladosPorPaginas
# ======================================================
def seleccionarEspaciosDetalladosPorPaginas(pagina: int = 1, tamanoPagina: int = 10) -> dict:
    """
    Realiza una llamada SOAP manual al servicio seleccionarEspaciosDetalladosPorPaginas.
    Interpreta directamente la respuesta XML (sin usar Zeep).
    """
    try:
        logger.info(f"Llamando a seleccionarEspaciosDetalladosPorPaginas(pagina={pagina}, tamanoPagina={tamanoPagina})")

        # Construir el envelope SOAP manualmente
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <seleccionarEspaciosDetalladosPorPaginas xmlns="http://tempuri.org/">
              <pagina>{pagina}</pagina>
              <tamanoPagina>{tamanoPagina}</tamanoPagina>
            </seleccionarEspaciosDetalladosPorPaginas>
          </soap12:Body>
        </soap12:Envelope>
        """

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": SOAP_ACTION_seleccionarEspaciosDetalladosPorPaginas,
        }

        # Enviar la solicitud SOAP al servidor WCF
        response = requests.post(SOAP_URL_seleccionarEspaciosDetalladosPorPaginas, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}: {response.text}"}

        xml_text = response.text

        # Namespaces SOAP
        ns = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "t": "http://tempuri.org/",
        }

        # Parsear XML con ElementTree
        root = ET.fromstring(xml_text)

        result_node = root.find(".//t:seleccionarEspaciosDetalladosPorPaginasResult", ns)
        if result_node is None:
            logger.error("No se encontró el nodo seleccionarEspaciosDetalladosPorPaginasResult.")
            return {"error": "No se encontró el nodo seleccionarEspaciosDetalladosPorPaginasResult."}

        pagina_actual = int(result_node.findtext("t:PaginaActual", default="0", namespaces=ns))
        tamano_pagina = int(result_node.findtext("t:TamanoPagina", default="0", namespaces=ns))
        total_registros = int(result_node.findtext("t:TotalRegistros", default="0", namespaces=ns))

        # Extraer los DTOs
        datos = []
        for item in result_node.findall(".//t:DTO_WS_IntegracionDetalleEspacio", ns):
            politicas = [p.text for p in item.findall(".//t:Politicas/t:string", ns) if p.text]
            imagenes = [i.text for i in item.findall(".//t:Imagenes/t:string", ns) if i.text]
            amenidades = [a.text for a in item.findall(".//t:Amenidades/t:string", ns) if a.text]

            datos.append({
                "Id": int(item.findtext("t:Id", "0", ns)),
                "Nombre": item.findtext("t:Nombre", "", ns),
                "NombreHotel": item.findtext("t:NombreHotel", "", ns),
                "NombreTipoServicio": item.findtext("t:NombreTipoServicio", "", ns),
                "NombreTipoAlimentacion": item.findtext("t:NombreTipoAlimentacion", "", ns),
                "Moneda": item.findtext("t:Moneda", "", ns),
                "CostoDiario": float(item.findtext("t:CostoDiario", "0", ns)),
                "Ubicacion": item.findtext("t:Ubicacion", "", ns),
                "DescripcionDelLugar": item.findtext("t:DescripcionDelLugar", "", ns),
                "Capacidad": item.findtext("t:Capacidad", "", ns),
                "Puntuacion": int(item.findtext("t:Puntuacion", "0", ns)),
                "EsActivo": item.findtext("t:EsActivo", "false", ns).lower() == "true",
                "Amenidades": amenidades,
                "Politicas": politicas,
                "Imagenes": imagenes,
            })

        logger.info(f"Parseados correctamente {len(datos)} registros de espacios detallados.")

        return {
            "PaginaActual": pagina_actual,
            "TamanoPagina": tamano_pagina,
            "TotalRegistros": total_registros,
            "Datos": datos
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarEspaciosDetalladosPorPaginas(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: verificarDisponibilidad
# ======================================================
def verificarDisponibilidad(espacioId: int, fechaInicio: str, fechaFin: str) -> dict:
    """
    Verifica si un espacio está disponible entre las fechas indicadas.
    Parámetros:
        espacioId: int → ID del espacio a consultar
        fechaInicio: str → en formato ISO 8601 ("YYYY-MM-DDTHH:MM:SS")
        fechaFin: str → en formato ISO 8601 ("YYYY-MM-DDTHH:MM:SS")
    Retorna:
        dict con {"espacioId": id, "disponible": bool}
    """
    try:
        logger.info(f"Verificando disponibilidad del espacio {espacioId} entre {fechaInicio} y {fechaFin}")

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <verificarDisponibilidad xmlns="http://tempuri.org/">
              <espacioId>{espacioId}</espacioId>
              <fechaInicio>{fechaInicio}</fechaInicio>
              <fechaFin>{fechaFin}</fechaFin>
            </verificarDisponibilidad>
          </soap12:Body>
        </soap12:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/verificarDisponibilidad",
        }

        response = requests.post(WSDL_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"Error HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        xml_text = response.text

        ns = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "t": "http://tempuri.org/",
        }

        root = ET.fromstring(xml_text)
        result_node = root.find(".//t:verificarDisponibilidadResult", ns)

        if result_node is None:
            logger.error("No se encontró el nodo verificarDisponibilidadResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo de resultado."}

        # Convertir texto a booleano
        disponible = result_node.text.strip().lower() == "true"

        logger.info(f"Disponibilidad para espacio {espacioId}: {disponible}")

        return {
            "espacioId": espacioId,
            "fechaInicio": fechaInicio,
            "fechaFin": fechaFin,
            "disponible": disponible
        }

    except Exception as ex:
        logger.error(f"Error en verificarDisponibilidad(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: crearPreReserva
# ======================================================

def crearPreReserva(listaEspacios, usuarioId=None, usuarioExternoId=None, fechaInicio=None, fechaFin=None, comentarios="") -> dict:
    """
    Crea una PRE-RESERVA (bloqueo temporal de espacios).
    Parámetros:
        listaEspacios: list[int] → lista de IDs de espacios a reservar
        usuarioId: int | None → ID del usuario interno (opcional)
        usuarioExternoId: int | None → ID del usuario externo (opcional)
        fechaInicio: str → Fecha/hora en formato ISO (YYYY-MM-DDTHH:MM:SS)
        fechaFin: str → Fecha/hora en formato ISO (YYYY-MM-DDTHH:MM:SS)
        comentarios: str → Texto opcional
    Retorna:
        dict con los datos de la pre-reserva o error
    """
    try:
        logger.info(
            f"Creando pre-reserva para espacios {listaEspacios} "
            f"entre {fechaInicio} y {fechaFin} "
            f"(usuarioId={usuarioId}, usuarioExternoId={usuarioExternoId})"
        )

        # Validar parámetros mínimos
        if not listaEspacios:
            return {"error": "Debe proporcionar al menos un espacio para la pre-reserva."}
        if not fechaInicio or not fechaFin:
            return {"error": "Debe proporcionar fechaInicio y fechaFin válidas."}

        # Construir el XML de listaEspacios dinámicamente
        espacios_xml = "".join([f"<espacioId>{e}</espacioId>" for e in listaEspacios])

        # Construir secciones opcionales
        usuario_id_xml = f"<usuarioId>{usuarioId}</usuarioId>" if usuarioId is not None else ""
        usuario_ext_xml = f"<usuarioExternoId>{usuarioExternoId}</usuarioExternoId>" if usuarioExternoId is not None else ""

        # Construir el cuerpo SOAP completo
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <crearPreReserva xmlns="http://tempuri.org/">
              <listaEspacios>
                {espacios_xml}
              </listaEspacios>
              {usuario_id_xml}
              {usuario_ext_xml}
              <fechaInicio>{fechaInicio}</fechaInicio>
              <fechaFin>{fechaFin}</fechaFin>
              <comentarios>{comentarios}</comentarios>
            </crearPreReserva>
          </soap12:Body>
        </soap12:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/crearPreReserva",
        }

        response = requests.post(WSDL_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"Error HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        xml_text = response.text

        # Definir namespaces
        ns = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "t": "http://tempuri.org/",
        }

        # Parsear el XML de respuesta
        root = ET.fromstring(xml_text)
        result_node = root.find(".//t:crearPreReservaResult", ns)
        if result_node is None:
            logger.error("No se encontró el nodo crearPreReservaResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo crearPreReservaResult."}

        # Funciones seguras para convertir valores
        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def get_text(tag, default=""):
            text = result_node.findtext(f"t:{tag}", default, ns)
            return text.strip() if text else default

        # Extraer campos de respuesta
        data = {
            "ReservaId": safe_int(get_text("ReservaId")),
            "UsuarioExternoId": safe_int(get_text("UsuarioExternoId")),
            "TokenSesion": get_text("TokenSesion"),
            "Estado": get_text("Estado"),
            "CostoTotal": safe_float(get_text("CostoTotal")),
            "DiasReservados": safe_int(get_text("DiasReservados")),
            "MinutosRetencion": safe_int(get_text("MinutosRetencion")),
            "EsBloqueadaInt": safe_int(get_text("EsBloqueadaInt")),
            "ExitoInt": safe_int(get_text("ExitoInt")),
            "Mensaje": get_text("Mensaje"),
        }

        logger.info(f"Pre-reserva creada exitosamente: ID {data['ReservaId']} - Estado: {data['Estado']}")
        return data

    except Exception as ex:
        logger.error(f"Error en crearPreReserva(): {ex}")
        return {"error": str(ex)}


def cotizarReserva(espacioId: int, checkIn: str, checkOut: str, costoPorNoche: float = None) -> dict:
    """
    💰 Cotiza una reserva de espacio con fechas y costo opcional por noche.

    Parámetros:
        espacioId: int → ID del espacio a cotizar
        checkIn: str → Fecha/hora de inicio (YYYY-MM-DDTHH:MM:SS)
        checkOut: str → Fecha/hora de fin (YYYY-MM-DDTHH:MM:SS)
        costoPorNoche: float | None → Costo opcional por noche (si se proporciona)

    Retorna:
        dict con los datos de la cotización o error
    """
    try:
        logger.info(
            f"Cotizando reserva: espacioId={espacioId}, checkIn={checkIn}, checkOut={checkOut}, costoPorNoche={costoPorNoche}"
        )

        # Validaciones básicas
        if not espacioId or not checkIn or not checkOut:
            return {"error": "Debe proporcionar espacioId, checkIn y checkOut válidos."}

        # Construir bloque opcional del costo
        costo_xml = f"<costoPorNoche>{costoPorNoche}</costoPorNoche>" if costoPorNoche is not None else ""

        # Crear cuerpo SOAP
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <cotizarReserva xmlns="http://tempuri.org/">
              <espacioId>{espacioId}</espacioId>
              <checkIn>{checkIn}</checkIn>
              <checkOut>{checkOut}</checkOut>
              {costo_xml}
            </cotizarReserva>
          </soap12:Body>
        </soap12:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/cotizarReserva",
        }

        response = requests.post(WSDL_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"Error HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        xml_text = response.text

        # Namespaces SOAP
        ns = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "t": "http://tempuri.org/",
        }

        # Parsear XML
        root = ET.fromstring(xml_text)
        result_node = root.find(".//t:cotizarReservaResult", ns)
        if result_node is None:
            logger.error("No se encontró el nodo cotizarReservaResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo cotizarReservaResult."}

        # Funciones seguras
        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def safe_bool(value):
            return str(value).strip().lower() in ("true", "1", "yes")

        def get_text(tag, default=""):
            text = result_node.findtext(f"t:{tag}", default, ns)
            return text.strip() if text else default

        # Amenidades: pueden venir como lista de <string>
        amenities_nodes = result_node.findall(".//t:Amenities/t:string", ns)
        amenities = [a.text for a in amenities_nodes if a is not None and a.text]

        # Crear estructura de salida
        data = {
            "EspacioId": safe_int(get_text("EspacioId")),
            "HotelId": safe_int(get_text("HotelId")),
            "RoomType": get_text("RoomType"),
            "NumberBeds": safe_int(get_text("NumberBeds")),
            "OccupancyAdultos": safe_int(get_text("OccupancyAdultos")),
            "OccupancyNinos": safe_int(get_text("OccupancyNinos")),
            "Board": get_text("Board"),
            "Amenities": amenities,
            "BreakfastIncluded": safe_bool(get_text("BreakfastIncluded")),
            "CheckIn": get_text("CheckIn"),
            "CheckOut": get_text("CheckOut"),
            "PricePerNight": safe_float(get_text("PricePerNight")),
            "TotalPrice": safe_float(get_text("TotalPrice")),
            "Currency": get_text("Currency"),
            "PreBookingId": get_text("PreBookingId"),
            "BookingId": get_text("BookingId"),
            "Estado": get_text("Estado"),
            "EsActivoInt": safe_int(get_text("EsActivoInt")),
            "ExitoInt": safe_int(get_text("ExitoInt")),
            "ExpiraEn": get_text("ExpiraEn"),
            "Mensaje": get_text("Mensaje"),
        }

        logger.info(
            f"Cotización exitosa para espacio {data['EspacioId']} - Total: {data['TotalPrice']} {data['Currency']}")
        return data

    except Exception as ex:
        logger.error(f"Error en cotizarReserva(): {ex}")
        return {"error": str(ex)}


def buscarServicios(
        ubicacion: str = None,
        hotel: str = None,
        fechaInicio: str = None,
        fechaFin: str = None,
        puntuacion: int = None,
        pagina: int = 1,
        tamanoPagina: int = 10
) -> dict:
    """
    🔍 Busca espacios detallados aplicando filtros opcionales.

    Parámetros:
        ubicacion: str | None → Ciudad, dirección o sector
        hotel: str | None → Nombre del hotel
        fechaInicio: str | None → Fecha/hora inicial (YYYY-MM-DDTHH:MM:SS)
        fechaFin: str | None → Fecha/hora final (YYYY-MM-DDTHH:MM:SS)
        puntuacion: int | None → Puntuación mínima del espacio
        pagina: int → Página solicitada (por defecto 1)
        tamanoPagina: int → Tamaño de página (por defecto 10)

    Retorna:
        dict con los campos de paginación y una lista de espacios encontrados
    """
    try:
        logger.info(
            f"Buscando servicios con filtros: ubicacion={ubicacion}, hotel={hotel}, "
            f"fechas=({fechaInicio}, {fechaFin}), puntuacion={puntuacion}, pagina={pagina}, tamanoPagina={tamanoPagina}"
        )

        # Validar que al menos un filtro tenga valor
        if not any([ubicacion, hotel, fechaInicio, fechaFin, puntuacion]):
            return {"error": "Debe proporcionar al menos un criterio de búsqueda."}

        # Construir XML condicionalmente
        xml_fields = ""
        if ubicacion:
            xml_fields += f"<ubicacion>{ubicacion}</ubicacion>"
        if hotel:
            xml_fields += f"<hotel>{hotel}</hotel>"
        if fechaInicio:
            xml_fields += f"<fechaInicio>{fechaInicio}</fechaInicio>"
        if fechaFin:
            xml_fields += f"<fechaFin>{fechaFin}</fechaFin>"
        if puntuacion is not None:
            xml_fields += f"<puntuacion>{puntuacion}</puntuacion>"

        xml_fields += f"<pagina>{pagina}</pagina><tamanoPagina>{tamanoPagina}</tamanoPagina>"

        # Construir cuerpo SOAP completo
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <buscarServicios xmlns="http://tempuri.org/">
              {xml_fields}
            </buscarServicios>
          </soap12:Body>
        </soap12:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/buscarServicios",
        }

        response = requests.post(WSDL_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"Error HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        xml_text = response.text

        # Namespaces SOAP
        ns = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "t": "http://tempuri.org/",
        }

        # Parsear XML
        root = ET.fromstring(xml_text)
        result_node = root.find(".//t:buscarServiciosResult", ns)
        if result_node is None:
            logger.error("No se encontró el nodo buscarServiciosResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo buscarServiciosResult."}

        # Helpers de parseo seguro
        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def safe_bool(value):
            return str(value).strip().lower() in ("true", "1", "yes")

        def get_text(node, tag, default=""):
            el = node.find(f"t:{tag}", ns)
            if el is not None and el.text:
                return el.text.strip()
            return default

        # Extraer info de paginación
        pagina_actual = safe_int(get_text(result_node, "PaginaActual"))
        tamano_pagina = safe_int(get_text(result_node, "TamanoPagina"))
        total_registros = safe_int(get_text(result_node, "TotalRegistros"))

        # Extraer lista de espacios
        espacios_nodes = result_node.findall(".//t:Datos/t:DTO_WS_IntegracionDetalleEspacio", ns)
        espacios = []
        for e in espacios_nodes:
            espacios.append({
                "Id": safe_int(get_text(e, "Id")),
                "Nombre": get_text(e, "Nombre"),
                "NombreHotel": get_text(e, "NombreHotel"),
                "NombreTipoServicio": get_text(e, "NombreTipoServicio"),
                "NombreTipoAlimentacion": get_text(e, "NombreTipoAlimentacion"),
                "Moneda": get_text(e, "Moneda"),
                "CostoDiario": safe_float(get_text(e, "CostoDiario")),
                "Ubicacion": get_text(e, "Ubicacion"),
                "DescripcionDelLugar": get_text(e, "DescripcionDelLugar"),
                "Capacidad": get_text(e, "Capacidad"),
                "Puntuacion": safe_int(get_text(e, "Puntuacion")),
                "EsActivo": safe_bool(get_text(e, "EsActivo")),
            })

        logger.info(f"{len(espacios)} espacios encontrados. Total registros: {total_registros}")

        return {
            "PaginaActual": pagina_actual,
            "TamanoPagina": tamano_pagina,
            "TotalRegistros": total_registros,
            "Datos": espacios
        }

    except Exception as ex:
        logger.error(f"Error en buscarServicios(): {ex}")
        return {"error": str(ex)}


def confirmarReserva(reservaId: int, pagoId: int = None, datosPago: str = "", monto: float = None) -> dict:
    """
    💳 Confirma una reserva existente y registra el pago asociado.

    Parámetros:
        reservaId: int → ID de la reserva a confirmar (obligatorio)
        pagoId: int | None → ID del pago registrado (opcional)
        datosPago: str → Información adicional del pago (ej: transacción, método, referencia)
        monto: float | None → Monto total pagado (opcional)

    Retorna:
        dict con la información confirmada de la reserva o el error
    """
    try:
        logger.info(f"Confirmando reservaId={reservaId}, pagoId={pagoId}, monto={monto}")

        if not reservaId:
            return {"error": "Debe especificar el ID de la reserva para confirmar."}

        # Campos opcionales
        pago_xml = f"<pagoId>{pagoId}</pagoId>" if pagoId is not None else ""
        monto_xml = f"<monto>{monto}</monto>" if monto is not None else ""

        # Construir cuerpo SOAP
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <ConfirmarReserva xmlns="http://tempuri.org/">
              <reservaId>{reservaId}</reservaId>
              {pago_xml}
              <datosPago>{datosPago}</datosPago>
              {monto_xml}
            </ConfirmarReserva>
          </soap12:Body>
        </soap12:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/ConfirmarReserva",
        }

        response = requests.post(WSDL_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"Error HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        xml_text = response.text

        # Namespaces SOAP
        ns = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "t": "http://tempuri.org/",
        }

        # Parsear XML
        root = ET.fromstring(xml_text)
        result_node = root.find(".//t:ConfirmarReservaResult", ns)
        if result_node is None:
            logger.error("No se encontró el nodo ConfirmarReservaResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo ConfirmarReservaResult."}

        # Funciones de parseo seguro
        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        def safe_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        def get_text(tag, default=""):
            text = result_node.findtext(f"t:{tag}", default, ns)
            return text.strip() if text else default

        # Extraer campos de la respuesta
        data = {
            "ReservaId": safe_int(get_text("ReservaId")),
            "PagoId": safe_int(get_text("PagoId")),
            "Monto": safe_float(get_text("Monto")),
            "ReferenciaPago": get_text("ReferenciaPago"),
            "Estado": get_text("Estado"),
            "TotalPrice": safe_float(get_text("TotalPrice")),
            "Currency": get_text("Currency"),
            "EsActivoInt": safe_int(get_text("EsActivoInt")),
            "ExitoInt": safe_int(get_text("ExitoInt")),
            "Mensaje": get_text("Mensaje"),
            "ExpiraEn": get_text("ExpiraEn"),
            "BookingId": get_text("BookingId"),
        }

        logger.info(f"Reserva confirmada exitosamente: ID {data['ReservaId']} - Estado: {data['Estado']}")
        return data

    except Exception as ex:
        logger.error(f"Error en confirmarReserva(): {ex}")
        return {"error": str(ex)}

def cancelarReservaIntegracion(bookingId: int, motivo: str = "") -> dict:
    """
    ❌ Cancela una reserva existente utilizando el BookingId y un motivo opcional.

    Parámetros:
        bookingId: int → Identificador único de la reserva (obligatorio)
        motivo: str → Texto opcional con el motivo de cancelación

    Retorna:
        dict con los datos del resultado de la cancelación o un error
    """
    try:
        logger.info(f"Cancelando reserva (BookingId={bookingId}) con motivo: '{motivo}'")

        if not bookingId:
            return {"error": "Debe especificar el BookingId de la reserva para cancelarla."}

        # Construir cuerpo SOAP dinámico
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
          <soap12:Body>
            <CancelarReservaIntegracion xmlns="http://tempuri.org/">
              <bookingId>{bookingId}</bookingId>
              <motivo>{motivo}</motivo>
            </CancelarReservaIntegracion>
          </soap12:Body>
        </soap12:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/CancelarReservaIntegracion",
        }

        # Enviar la solicitud SOAP
        response = requests.post(WSDL_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"Error HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        xml_text = response.text

        # Namespaces SOAP
        ns = {
            "soap": "http://www.w3.org/2003/05/soap-envelope",
            "t": "http://tempuri.org/",
        }

        # Parsear respuesta XML
        root = ET.fromstring(xml_text)
        result_node = root.find(".//t:CancelarReservaIntegracionResult", ns)
        if result_node is None:
            logger.error("No se encontró el nodo CancelarReservaIntegracionResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo CancelarReservaIntegracionResult."}

        # Funciones de parseo seguro
        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        def get_text(tag, default=""):
            text = result_node.findtext(f"t:{tag}", default, ns)
            return text.strip() if text else default

        # Extraer campos
        data = {
            "ReservaId": safe_int(get_text("ReservaId")),
            "Estado": get_text("Estado"),
            "ExitoInt": safe_int(get_text("ExitoInt")),
            "Mensaje": get_text("Mensaje"),
            "FechaCancelacion": get_text("FechaCancelacion"),
        }

        if data["ExitoInt"] == 1:
            logger.info(f"Reserva {data['ReservaId']} cancelada correctamente. Estado: {data['Estado']}")
        else:
            logger.warning(f"Cancelación fallida para BookingId={bookingId}: {data['Mensaje']}")

        return data

    except Exception as ex:
        logger.error(f"Error en cancelarReservaIntegracion(): {ex}")
        return {"error": str(ex)}

