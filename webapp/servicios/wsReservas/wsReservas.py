"""
Módulo de integración SOAP con el servicio remoto:
WS_GestionReservas.asmx

Autor: Carlos Quitus
Descripción:
    Contiene funciones que interpretan los métodos SOAP
    relacionados con la gestión de reservas.
"""

import logging
import xml.etree.ElementTree as ET
import requests

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
WSDL_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionReservas.asmx?WSDL"
SOAP_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionReservas.asmx"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(value)
    except Exception:
        return default

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def safe_float(value, default=0.0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(value)
    except Exception:
        return default


def safe_bool(value):
    try:
        return str(value).strip().lower() == "true"
    except Exception:
        return False

# ==========================================================
# FUNCIÓN: seleccionarReservasPorUsuario
# ==========================================================
def seleccionarReservasPorUsuario(usuario_id: int) -> dict:
    """
    Obtiene todas las reservas asociadas a un usuario desde el servicio SOAP WS_GestionReservas.

    Parámetros:
        usuario_id (int): ID del usuario cuyas reservas se desean consultar.

    Retorna:
        dict: {
            "reservas": [ {...}, {...} ],
            "total": int,
            "mensaje": str
        }
        o en caso de error:
        {"error": str}
    """
    try:
        logger.info(f"Consultando reservas del usuario ID={usuario_id} en WS_GestionReservas")

        # ======================================================
        # Funciones seguras de conversión
        # ======================================================
        def safe_int(value, default=0):
            try:
                if value is None or str(value).strip() == "" or value.lower() == "none":
                    return default
                return int(float(value))
            except Exception:
                return default

        def safe_float(value, default=0.0):
            try:
                if value is None or str(value).strip() == "" or value.lower() == "none":
                    return default
                return float(value)
            except Exception:
                return default

        # ======================================================
        # Construcción del envelope SOAP
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarReservasPorUsuario>
                 <tem:usuarioId>{usuario_id}</tem:usuarioId>
              </tem:seleccionarReservasPorUsuario>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarReservasPorUsuario",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:seleccionarReservasPorUsuarioResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo seleccionarReservasPorUsuarioResult en la respuesta SOAP.")
            return {"reservas": [], "total": 0, "mensaje": "No se encontraron reservas."}

        # ======================================================
        # Extracción de datos de cada <Reservas>
        # ======================================================
        reservas = []
        for nodo in result_node.findall("tem:Reservas", ns):
            reserva = {
                "Id": safe_int(nodo.findtext("tem:Id", "0", ns)),
                "UsuarioId": safe_int(nodo.findtext("tem:UsuarioId", "0", ns)),
                "UsuarioExternoId": safe_int(nodo.findtext("tem:UsuarioExternoId", "0", ns)),
                "Estado": nodo.findtext("tem:Estado", "", ns),
                "Comentarios": nodo.findtext("tem:Comentarios", "", ns),
                "CostoSubtotal": safe_float(nodo.findtext("tem:CostoSubtotal", "0", ns)),
                "CostoIVA": safe_float(nodo.findtext("tem:CostoIVA", "0", ns)),
                "CostoFinal": safe_float(nodo.findtext("tem:CostoFinal", "0", ns)),
                "MinutosRetencion": safe_int(nodo.findtext("tem:MinutosRetencion", "0", ns)),
                "ExpiraEn": safe_int(nodo.findtext("tem:ExpiraEn", "0", ns)),
                "EsBloqueada": nodo.findtext("tem:EsBloqueada", "false", ns).lower() == "true",
                "TokenSesion": nodo.findtext("tem:TokenSesion", "", ns),
                "FechaRegistro": nodo.findtext("tem:FechaRegistro", "", ns),
                "UltimaFechaCambio": nodo.findtext("tem:UltimaFechaCambio", "", ns),
                "EsActivo": nodo.findtext("tem:EsActivo", "false", ns).lower() == "true",
            }
            reservas.append(reserva)

        logger.info(f"Se encontraron {len(reservas)} reservas para el usuario {usuario_id}")
        return {
            "reservas": reservas,
            "total": len(reservas),
            "mensaje": f"Se encontraron {len(reservas)} reservas del usuario."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarReservasPorUsuario(): {ex}")
        return {"error": str(ex)}

# ==========================================================
# FUNCIÓN: seleccionarReservas (versión robusta)
# ==========================================================
def seleccionarReservas() -> dict:
    """
    Obtiene todas las reservas activas desde el servicio SOAP WS_GestionReservas.

    Retorna:
        dict: {
            "reservas": [ {...}, {...} ],
            "total": int,
            "mensaje": str
        }
        o {"error": str} si ocurre un fallo.
    """
    try:
        logger.info("Consultando todas las reservas activas en WS_GestionReservas")

        # Construcción del cuerpo SOAP
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarReservas/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarReservas",
        }

        # Enviar solicitud SOAP
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # Parsear respuesta XML
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:seleccionarReservasResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo seleccionarReservasResult en la respuesta SOAP.")
            return {"reservas": [], "total": 0, "mensaje": "No se encontraron reservas."}

        reservas = []
        for nodo in result_node.findall("tem:Reservas", ns):
            reserva = {
                "Id": safe_int(nodo.findtext("tem:Id", "0", ns)),
                "UsuarioId": safe_int(nodo.findtext("tem:UsuarioId", "0", ns)),
                "UsuarioExternoId": safe_int(nodo.findtext("tem:UsuarioExternoId", "0", ns)),
                "Estado": nodo.findtext("tem:Estado", "", ns),
                "Comentarios": nodo.findtext("tem:Comentarios", "", ns),
                "CostoSubtotal": safe_float(nodo.findtext("tem:CostoSubtotal", "0", ns)),
                "CostoIVA": safe_float(nodo.findtext("tem:CostoIVA", "0", ns)),
                "CostoFinal": safe_float(nodo.findtext("tem:CostoFinal", "0", ns)),
                "MinutosRetencion": safe_int(nodo.findtext("tem:MinutosRetencion", "0", ns)),
                "ExpiraEn": safe_int(nodo.findtext("tem:ExpiraEn", "0", ns)),
                "EsBloqueada": safe_bool(nodo.findtext("tem:EsBloqueada", "false", ns)),
                "TokenSesion": nodo.findtext("tem:TokenSesion", "", ns),
                "FechaRegistro": nodo.findtext("tem:FechaRegistro", "", ns),
                "UltimaFechaCambio": nodo.findtext("tem:UltimaFechaCambio", "", ns),
                "EsActivo": safe_bool(nodo.findtext("tem:EsActivo", "false", ns)),
            }
            reservas.append(reserva)

        logger.info(f"Se encontraron {len(reservas)} reservas activas en el sistema.")

        return {
            "reservas": reservas,
            "total": len(reservas),
            "mensaje": f"Se encontraron {len(reservas)} reservas activas."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarReservas(): {ex}")
        return {"error": str(ex)}
# ==========================================================
# FUNCIÓN: seleccionarReservaPorId
# ==========================================================
def seleccionarReservaPorId(reserva_id: int) -> dict:
    """
    Obtiene una reserva específica por su ID desde el servicio SOAP WS_GestionReservas.

    Parámetros:
        reserva_id (int): ID de la reserva a consultar.

    Retorna:
        dict: {
            "reserva": {...},
            "mensaje": str
        }
        o en caso de error:
        {"error": str}
    """
    try:
        logger.info(f"Consultando reserva con ID={reserva_id} en WS_GestionReservas")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1 con namespaces 'soapenv' y 'tem')
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarReservaPorId>
                 <tem:id>{reserva_id}</tem:id>
              </tem:seleccionarReservaPorId>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarReservaPorId",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:seleccionarReservaPorIdResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo seleccionarReservaPorIdResult en la respuesta SOAP.")
            return {"reserva": None, "mensaje": "No se encontró la reserva solicitada."}

        # ======================================================
        # Extracción de datos de la reserva
        # ======================================================
        reserva = {
            "Id": safe_int(result_node.findtext("tem:Id", "0", ns)),
            "UsuarioId": safe_int(result_node.findtext("tem:UsuarioId", "0", ns)),
            "UsuarioExternoId": safe_int(result_node.findtext("tem:UsuarioExternoId", "0", ns)),
            "Estado": result_node.findtext("tem:Estado", "", ns),
            "Comentarios": result_node.findtext("tem:Comentarios", "", ns),
            "CostoSubtotal": safe_float(result_node.findtext("tem:CostoSubtotal", "0", ns)),
            "CostoIVA": safe_float(result_node.findtext("tem:CostoIVA", "0", ns)),
            "CostoFinal": safe_float(result_node.findtext("tem:CostoFinal", "0", ns)),
            "MinutosRetencion": safe_int(result_node.findtext("tem:MinutosRetencion", "0", ns)),
            "ExpiraEn": safe_int(result_node.findtext("tem:ExpiraEn", "0", ns)),
            "EsBloqueada": result_node.findtext("tem:EsBloqueada", "false", ns).lower() == "true",
            "TokenSesion": result_node.findtext("tem:TokenSesion", "", ns),
            "FechaRegistro": result_node.findtext("tem:FechaRegistro", "", ns),
            "UltimaFechaCambio": result_node.findtext("tem:UltimaFechaCambio", "", ns),
            "EsActivo": result_node.findtext("tem:EsActivo", "false", ns).lower() == "true",
        }

        logger.info(f"Reserva ID={reserva_id} obtenida correctamente.")
        return {"reserva": reserva, "mensaje": "Reserva obtenida correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarReservaPorId(): {ex}")
        return {"error": str(ex)}

# ==========================================================
# FUNCIÓN: obtenerReservasExpiradas
# ==========================================================
def obtenerReservasExpiradas() -> dict:
    """
    Obtiene todas las reservas que han expirado desde el servicio SOAP WS_GestionReservas.

    Parámetros:
        Ninguno.

    Retorna:
        dict: {
            "reservas": [ {...}, {...} ],
            "total": int,
            "mensaje": str
        }
        o en caso de error:
        {"error": str}
    """
    try:
        logger.info("Consultando reservas expiradas en WS_GestionReservas")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1 con namespaces 'soapenv' y 'tem')
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:obtenerReservasExpiradas/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/obtenerReservasExpiradas",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:obtenerReservasExpiradasResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo obtenerReservasExpiradasResult en la respuesta SOAP.")
            return {"reservas": [], "total": 0, "mensaje": "No se encontraron reservas expiradas."}

        # ======================================================
        # Extracción de datos de cada <Reservas>
        # ======================================================
        reservas = []
        for nodo in result_node.findall("tem:Reservas", ns):
            reserva = {
                "Id": safe_int(nodo.findtext("tem:Id", "0", ns)),
                "UsuarioId": safe_int(nodo.findtext("tem:UsuarioId", "0", ns)),
                "UsuarioExternoId": safe_int(nodo.findtext("tem:UsuarioExternoId", "0", ns)),
                "Estado": nodo.findtext("tem:Estado", "", ns),
                "Comentarios": nodo.findtext("tem:Comentarios", "", ns),
                "CostoSubtotal": safe_float(nodo.findtext("tem:CostoSubtotal", "0", ns)),
                "CostoIVA": safe_float(nodo.findtext("tem:CostoIVA", "0", ns)),
                "CostoFinal": safe_float(nodo.findtext("tem:CostoFinal", "0", ns)),
                "MinutosRetencion": safe_int(nodo.findtext("tem:MinutosRetencion", "0", ns)),
                "ExpiraEn": safe_int(nodo.findtext("tem:ExpiraEn", "0", ns)),
                "EsBloqueada": nodo.findtext("tem:EsBloqueada", "false", ns).lower() == "true",
                "TokenSesion": nodo.findtext("tem:TokenSesion", "", ns),
                "FechaRegistro": nodo.findtext("tem:FechaRegistro", "", ns),
                "UltimaFechaCambio": nodo.findtext("tem:UltimaFechaCambio", "", ns),
                "EsActivo": nodo.findtext("tem:EsActivo", "false", ns).lower() == "true",
            }
            reservas.append(reserva)

        logger.info(f"Se encontraron {len(reservas)} reservas expiradas.")

        return {
            "reservas": reservas,
            "total": len(reservas),
            "mensaje": f"Se encontraron {len(reservas)} reservas expiradas."
        }

    except Exception as ex:
        logger.error(f"Error en obtenerReservasExpiradas(): {ex}")
        return {"error": str(ex)}

# ==========================================================
# FUNCIÓN: obtenerReservasBloqueadas
# ==========================================================
def obtenerReservasBloqueadas() -> dict:
    """
    Obtiene todas las reservas actualmente bloqueadas desde el servicio SOAP WS_GestionReservas.

    Parámetros:
        Ninguno.

    Retorna:
        dict: {
            "reservas": [ {...}, {...} ],
            "total": int,
            "mensaje": str
        }
        o en caso de error:
        {"error": str}
    """
    try:
        logger.info("Consultando reservas bloqueadas en WS_GestionReservas")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1 con namespaces 'soapenv' y 'tem')
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:obtenerReservasBloqueadas/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/obtenerReservasBloqueadas",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:obtenerReservasBloqueadasResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo obtenerReservasBloqueadasResult en la respuesta SOAP.")
            return {"reservas": [], "total": 0, "mensaje": "No se encontraron reservas bloqueadas."}

        # ======================================================
        # Extracción de datos de cada <Reservas>
        # ======================================================
        reservas = []
        for nodo in result_node.findall("tem:Reservas", ns):
            reserva = {
                "Id": int(nodo.findtext("tem:Id", "0", ns)),
                "UsuarioId": int(nodo.findtext("tem:UsuarioId", "0", ns)),
                "UsuarioExternoId": int(nodo.findtext("tem:UsuarioExternoId", "0", ns)),
                "Estado": nodo.findtext("tem:Estado", "", ns),
                "Comentarios": nodo.findtext("tem:Comentarios", "", ns),
                "CostoSubtotal": float(nodo.findtext("tem:CostoSubtotal", "0", ns)),
                "CostoIVA": float(nodo.findtext("tem:CostoIVA", "0", ns)),
                "CostoFinal": float(nodo.findtext("tem:CostoFinal", "0", ns)),
                "MinutosRetencion": int(nodo.findtext("tem:MinutosRetencion", "0", ns)),
                "ExpiraEn": int(nodo.findtext("tem:ExpiraEn", "0", ns)),
                "EsBloqueada": nodo.findtext("tem:EsBloqueada", "false", ns).lower() == "true",
                "TokenSesion": nodo.findtext("tem:TokenSesion", "", ns),
                "FechaRegistro": nodo.findtext("tem:FechaRegistro", "", ns),
                "UltimaFechaCambio": nodo.findtext("tem:UltimaFechaCambio", "", ns),
                "EsActivo": nodo.findtext("tem:EsActivo", "false", ns).lower() == "true",
            }
            reservas.append(reserva)

        logger.info(f"Se encontraron {len(reservas)} reservas bloqueadas.")

        return {
            "reservas": reservas,
            "total": len(reservas),
            "mensaje": f"Se encontraron {len(reservas)} reservas bloqueadas."
        }

    except Exception as ex:
        logger.error(f"Error en obtenerReservasBloqueadas(): {ex}")
        return {"error": str(ex)}


# ==========================================================
# FUNCIÓN: insertarReserva
# ==========================================================
def insertarReserva(nueva_reserva: dict) -> dict:
    """
    Inserta una nueva reserva en el servicio SOAP WS_GestionReservas.

    Parámetros:
        nueva_reserva (dict): Diccionario con la información completa de la reserva. Ejemplo:
            {
                "Id": 0,
                "UsuarioId": 1,
                "UsuarioExternoId": 2,
                "Estado": "Pendiente",
                "Comentarios": "Reserva inicial",
                "CostoSubtotal": 10.50,
                "CostoIVA": 1.26,
                "CostoFinal": 11.76,
                "MinutosRetencion": 15,
                "ExpiraEn": 900,
                "EsBloqueada": False,
                "TokenSesion": "XYZ123",
                "FechaRegistro": "2025-10-27T00:00:00",
                "UltimaFechaCambio": "2025-10-27T00:00:00",
                "EsActivo": True,
                "UsuarioExterno": {
                    "Id": 2,
                    "Nombre": "Cliente Demo",
                    "Email": "cliente@demo.com",
                    "PasswordHash": "",
                    "Rol": "Externo",
                    "FechaRegistro": "2025-10-27T00:00:00",
                    "UltimaFechaCambio": "2025-10-27T00:00:00",
                    "EsActivo": True,
                    "UltimaFechainicioSesion": "2025-10-27T00:00:00"
                },
                "Usuarios": {
                    "Id": 1,
                    "Nombre": "Admin",
                    "Email": "admin@realdecuenca.com",
                    "PasswordHash": "",
                    "Rol": "Administrador",
                    "FechaRegistro": "2025-10-27T00:00:00",
                    "UltimaFechaCambio": "2025-10-27T00:00:00",
                    "EsActivo": True,
                    "UltimaFechainicioSesion": "2025-10-27T00:00:00"
                }
            }

    Retorna:
        dict:
            {"resultado": id_generado, "mensaje": str}
        o en caso de error:
            {"error": str}
    """
    try:
        logger.info("Insertando nueva reserva en WS_GestionReservas")

        # ======================================================
        # Construcción dinámica del bloque <nuevaReserva>
        # ======================================================
        def bool_str(valor: bool) -> str:
            return "true" if valor else "false"

        usuario_externo = nueva_reserva.get("UsuarioExterno", {})
        usuarios = nueva_reserva.get("Usuarios", {})

        reserva_xml = f"""
        <tem:nuevaReserva>
            <tem:Id>{nueva_reserva.get("Id", 0)}</tem:Id>
            <tem:UsuarioId>{nueva_reserva.get("UsuarioId", 0)}</tem:UsuarioId>
            <tem:UsuarioExternoId>{nueva_reserva.get("UsuarioExternoId", 0)}</tem:UsuarioExternoId>
            <tem:Estado>{nueva_reserva.get("Estado", "")}</tem:Estado>
            <tem:Comentarios>{nueva_reserva.get("Comentarios", "")}</tem:Comentarios>
            <tem:CostoSubtotal>{nueva_reserva.get("CostoSubtotal", 0)}</tem:CostoSubtotal>
            <tem:CostoIVA>{nueva_reserva.get("CostoIVA", 0)}</tem:CostoIVA>
            <tem:CostoFinal>{nueva_reserva.get("CostoFinal", 0)}</tem:CostoFinal>
            <tem:MinutosRetencion>{nueva_reserva.get("MinutosRetencion", 0)}</tem:MinutosRetencion>
            <tem:ExpiraEn>{nueva_reserva.get("ExpiraEn", 0)}</tem:ExpiraEn>
            <tem:EsBloqueada>{bool_str(nueva_reserva.get("EsBloqueada", False))}</tem:EsBloqueada>
            <tem:TokenSesion>{nueva_reserva.get("TokenSesion", "")}</tem:TokenSesion>
            <tem:FechaRegistro>{nueva_reserva.get("FechaRegistro", "")}</tem:FechaRegistro>
            <tem:UltimaFechaCambio>{nueva_reserva.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
            <tem:EsActivo>{bool_str(nueva_reserva.get("EsActivo", True))}</tem:EsActivo>

            <tem:UsuarioExterno>
                <tem:Id>{usuario_externo.get("Id", 0)}</tem:Id>
                <tem:Nombre>{usuario_externo.get("Nombre", "")}</tem:Nombre>
                <tem:Email>{usuario_externo.get("Email", "")}</tem:Email>
                <tem:PasswordHash>{usuario_externo.get("PasswordHash", "")}</tem:PasswordHash>
                <tem:Rol>{usuario_externo.get("Rol", "")}</tem:Rol>
                <tem:FechaRegistro>{usuario_externo.get("FechaRegistro", "")}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{usuario_externo.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
                <tem:EsActivo>{bool_str(usuario_externo.get("EsActivo", True))}</tem:EsActivo>
                <tem:UltimaFechainicioSesion>{usuario_externo.get("UltimaFechainicioSesion", "")}</tem:UltimaFechainicioSesion>
            </tem:UsuarioExterno>

            <tem:Usuarios>
                <tem:Id>{usuarios.get("Id", 0)}</tem:Id>
                <tem:Nombre>{usuarios.get("Nombre", "")}</tem:Nombre>
                <tem:Email>{usuarios.get("Email", "")}</tem:Email>
                <tem:PasswordHash>{usuarios.get("PasswordHash", "")}</tem:PasswordHash>
                <tem:Rol>{usuarios.get("Rol", "")}</tem:Rol>
                <tem:FechaRegistro>{usuarios.get("FechaRegistro", "")}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{usuarios.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
                <tem:EsActivo>{bool_str(usuarios.get("EsActivo", True))}</tem:EsActivo>
                <tem:UltimaFechainicioSesion>{usuarios.get("UltimaFechainicioSesion", "")}</tem:UltimaFechainicioSesion>
            </tem:Usuarios>
        </tem:nuevaReserva>
        """

        # ======================================================
        # Construcción del envelope SOAP
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:insertarReserva>
                 {reserva_xml}
              </tem:insertarReserva>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/insertarReserva",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo del resultado XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:insertarReservaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo insertarReservaResult en la respuesta SOAP.")
            return {"resultado": None, "mensaje": "No se pudo obtener el ID de la nueva reserva."}

        reserva_id = int(result_node.text)
        logger.info(f"Nueva reserva insertada correctamente con ID={reserva_id}")

        return {
            "resultado": reserva_id,
            "mensaje": f"Reserva insertada correctamente con ID {reserva_id}"
        }

    except Exception as ex:
        logger.error(f"Error en insertarReserva(): {ex}")
        return {"error": str(ex)}

# ==========================================================
# FUNCIÓN: eliminarReserva
# ==========================================================
def eliminarReserva(reserva_id: int) -> dict:
    """
    Elimina (desactiva mediante Soft Delete) una reserva en el servicio SOAP WS_GestionReservas.

    Parámetros:
        reserva_id (int): ID de la reserva que se desea eliminar.

    Retorna:
        dict:
            {"eliminado": bool, "mensaje": str}
        o en caso de error:
            {"error": str}
    """
    try:
        logger.info(f"Eliminando (Soft Delete) la reserva con ID={reserva_id} en WS_GestionReservas")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:eliminarReserva>
                 <tem:id>{reserva_id}</tem:id>
              </tem:eliminarReserva>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/eliminarReserva",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:eliminarReservaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo eliminarReservaResult en la respuesta SOAP.")
            return {"eliminado": False, "mensaje": "No se pudo confirmar la eliminación de la reserva."}

        eliminado = result_node.text.strip().lower() == "true"

        if eliminado:
            logger.info(f"Reserva ID={reserva_id} eliminada correctamente.")
            return {"eliminado": True, "mensaje": f"Reserva ID={reserva_id} eliminada correctamente."}
        else:
            logger.warning(f"No se pudo eliminar la reserva ID={reserva_id}.")
            return {"eliminado": False, "mensaje": f"No se pudo eliminar la reserva ID={reserva_id}."}

    except Exception as ex:
        logger.error(f"Error en eliminarReserva(): {ex}")
        return {"error": str(ex)}


# ==========================================================
# FUNCIÓN: cambiarEstadoReserva
# ==========================================================
def cambiarEstadoReserva(reserva_id: int, nuevo_estado: str) -> dict:
    """
    Cambia el estado actual de una reserva en el servicio SOAP WS_GestionReservas.

    Parámetros:
        reserva_id (int): ID de la reserva cuyo estado se desea cambiar.
        nuevo_estado (str): Nuevo estado a asignar (por ejemplo: "Confirmada", "Cancelada", "Finalizada", etc.)

    Retorna:
        dict:
            {"actualizado": bool, "mensaje": str}
        o en caso de error:
            {"error": str}
    """
    try:
        logger.info(f"Cambiando estado de la reserva ID={reserva_id} a '{nuevo_estado}'")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:cambiarEstadoReserva>
                 <tem:id>{reserva_id}</tem:id>
                 <tem:nuevoEstado>{nuevo_estado}</tem:nuevoEstado>
              </tem:cambiarEstadoReserva>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/cambiarEstadoReserva",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:cambiarEstadoReservaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo cambiarEstadoReservaResult en la respuesta SOAP.")
            return {"actualizado": False, "mensaje": "No se pudo confirmar el cambio de estado."}

        actualizado = result_node.text.strip().lower() == "true"

        if actualizado:
            logger.info(f"Estado de la reserva ID={reserva_id} actualizado exitosamente a '{nuevo_estado}'.")
            return {"actualizado": True, "mensaje": f"Estado actualizado a '{nuevo_estado}' correctamente."}
        else:
            logger.warning(f"No se pudo cambiar el estado de la reserva ID={reserva_id}.")
            return {"actualizado": False, "mensaje": "El servicio no confirmó el cambio de estado."}

    except Exception as ex:
        logger.error(f"Error en cambiarEstadoReserva(): {ex}")
        return {"error": str(ex)}



# ==========================================================
# FUNCIÓN: calcularTotales
# ==========================================================
def calcularTotales(reserva: dict, porcentaje_iva: float) -> dict:
    """
    Calcula los totales de una reserva aplicando el porcentaje de IVA.

    Parámetros:
        reserva (dict): Diccionario con los datos de la reserva. Ejemplo:
            {
                "Id": 15,
                "UsuarioId": 1,
                "UsuarioExternoId": 2,
                "Estado": "Pendiente",
                "Comentarios": "Reserva inicial",
                "CostoSubtotal": 50.00,
                "CostoIVA": 0.00,
                "CostoFinal": 0.00,
                "MinutosRetencion": 15,
                "ExpiraEn": 900,
                "EsBloqueada": False,
                "TokenSesion": "ABC123",
                "FechaRegistro": "2025-10-27T00:00:00",
                "UltimaFechaCambio": "2025-10-27T00:00:00",
                "EsActivo": True,
                "UsuarioExterno": {...},
                "Usuarios": {...}
            }
        porcentaje_iva (float): Porcentaje de IVA a aplicar (por ejemplo, 12.0 para 12%).

    Retorna:
        dict:
            {"exito": bool, "mensaje": str}
        o en caso de error:
            {"error": str}
    """
    try:
        logger.info(f"Calculando totales de la reserva ID={reserva.get('Id')} con IVA={porcentaje_iva}%")

        # ======================================================
        # Función auxiliar para convertir booleanos a texto
        # ======================================================
        def bool_str(valor: bool) -> str:
            return "true" if valor else "false"

        usuario_externo = reserva.get("UsuarioExterno", {})
        usuarios = reserva.get("Usuarios", {})

        # ======================================================
        # Construcción del bloque XML <reserva>
        # ======================================================
        reserva_xml = f"""
        <tem:reserva>
            <tem:Id>{reserva.get("Id", 0)}</tem:Id>
            <tem:UsuarioId>{reserva.get("UsuarioId", 0)}</tem:UsuarioId>
            <tem:UsuarioExternoId>{reserva.get("UsuarioExternoId", 0)}</tem:UsuarioExternoId>
            <tem:Estado>{reserva.get("Estado", "")}</tem:Estado>
            <tem:Comentarios>{reserva.get("Comentarios", "")}</tem:Comentarios>
            <tem:CostoSubtotal>{reserva.get("CostoSubtotal", 0)}</tem:CostoSubtotal>
            <tem:CostoIVA>{reserva.get("CostoIVA", 0)}</tem:CostoIVA>
            <tem:CostoFinal>{reserva.get("CostoFinal", 0)}</tem:CostoFinal>
            <tem:MinutosRetencion>{reserva.get("MinutosRetencion", 0)}</tem:MinutosRetencion>
            <tem:ExpiraEn>{reserva.get("ExpiraEn", 0)}</tem:ExpiraEn>
            <tem:EsBloqueada>{bool_str(reserva.get("EsBloqueada", False))}</tem:EsBloqueada>
            <tem:TokenSesion>{reserva.get("TokenSesion", "")}</tem:TokenSesion>
            <tem:FechaRegistro>{reserva.get("FechaRegistro", "")}</tem:FechaRegistro>
            <tem:UltimaFechaCambio>{reserva.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
            <tem:EsActivo>{bool_str(reserva.get("EsActivo", True))}</tem:EsActivo>

            <tem:UsuarioExterno>
                <tem:Id>{usuario_externo.get("Id", 0)}</tem:Id>
                <tem:Nombre>{usuario_externo.get("Nombre", "")}</tem:Nombre>
                <tem:Email>{usuario_externo.get("Email", "")}</tem:Email>
                <tem:PasswordHash>{usuario_externo.get("PasswordHash", "")}</tem:PasswordHash>
                <tem:Rol>{usuario_externo.get("Rol", "")}</tem:Rol>
                <tem:FechaRegistro>{usuario_externo.get("FechaRegistro", "")}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{usuario_externo.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
                <tem:EsActivo>{bool_str(usuario_externo.get("EsActivo", True))}</tem:EsActivo>
                <tem:UltimaFechainicioSesion>{usuario_externo.get("UltimaFechainicioSesion", "")}</tem:UltimaFechainicioSesion>
            </tem:UsuarioExterno>

            <tem:Usuarios>
                <tem:Id>{usuarios.get("Id", 0)}</tem:Id>
                <tem:Nombre>{usuarios.get("Nombre", "")}</tem:Nombre>
                <tem:Email>{usuarios.get("Email", "")}</tem:Email>
                <tem:PasswordHash>{usuarios.get("PasswordHash", "")}</tem:PasswordHash>
                <tem:Rol>{usuarios.get("Rol", "")}</tem:Rol>
                <tem:FechaRegistro>{usuarios.get("FechaRegistro", "")}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{usuarios.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
                <tem:EsActivo>{bool_str(usuarios.get("EsActivo", True))}</tem:EsActivo>
                <tem:UltimaFechainicioSesion>{usuarios.get("UltimaFechainicioSesion", "")}</tem:UltimaFechainicioSesion>
            </tem:Usuarios>
        </tem:reserva>
        """

        # ======================================================
        # Construcción del envelope SOAP
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:calcularTotales>
                 {reserva_xml}
                 <tem:porcentajeIVA>{porcentaje_iva}</tem:porcentajeIVA>
              </tem:calcularTotales>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/calcularTotales",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:calcularTotalesResponse", ns)

        if result_node is not None:
            logger.info(f"Totales calculados correctamente para la reserva ID={reserva.get('Id')}")
            return {"exito": True, "mensaje": "Totales calculados correctamente."}
        else:
            logger.warning("No se encontró el nodo calcularTotalesResponse en la respuesta SOAP.")
            return {"exito": False, "mensaje": "No se pudo calcular los totales."}

    except Exception as ex:
        logger.error(f"Error en calcularTotales(): {ex}")
        return {"error": str(ex)}


# ==========================================================
# FUNCIÓN: bloquearReserva
# ==========================================================
def bloquearReserva(reserva_id: int, minutos_retencion: int) -> dict:
    """
    Bloquea temporalmente una reserva por un número determinado de minutos.

    Parámetros:
        reserva_id (int): ID de la reserva que se desea bloquear.
        minutos_retencion (int): Número de minutos durante los cuales la reserva estará bloqueada.

    Retorna:
        dict:
            {"bloqueado": bool, "mensaje": str}
        o en caso de error:
            {"error": str}
    """
    try:
        logger.info(f"Bloqueando reserva ID={reserva_id} por {minutos_retencion} minutos.")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:bloquearReserva>
                 <tem:id>{reserva_id}</tem:id>
                 <tem:minutosRetencion>{minutos_retencion}</tem:minutosRetencion>
              </tem:bloquearReserva>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/bloquearReserva",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:bloquearReservaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo bloquearReservaResult en la respuesta SOAP.")
            return {"bloqueado": False, "mensaje": "No se pudo confirmar el bloqueo de la reserva."}

        bloqueado = result_node.text.strip().lower() == "true"

        if bloqueado:
            logger.info(f"Reserva ID={reserva_id} bloqueada correctamente por {minutos_retencion} minutos.")
            return {"bloqueado": True, "mensaje": f"Reserva bloqueada correctamente por {minutos_retencion} minutos."}
        else:
            logger.warning(f"No se pudo bloquear la reserva ID={reserva_id}.")
            return {"bloqueado": False, "mensaje": "El servicio no confirmó el bloqueo de la reserva."}

    except Exception as ex:
        logger.error(f"Error en bloquearReserva(): {ex}")
        return {"error": str(ex)}

# ==========================================================
# FUNCIÓN: actualizarReserva
# ==========================================================
def actualizarReserva(reserva: dict) -> dict:
    """
    Actualiza los datos de una reserva existente mediante el servicio SOAP WS_GestionReservas.

    Parámetros:
        reserva (dict): Diccionario con los datos de la reserva a actualizar. Ejemplo:
            {
                "Id": 15,
                "UsuarioId": 1,
                "UsuarioExternoId": 2,
                "Estado": "Confirmada",
                "Comentarios": "Reserva actualizada por el usuario",
                "CostoSubtotal": 80.00,
                "CostoIVA": 9.60,
                "CostoFinal": 89.60,
                "MinutosRetencion": 30,
                "ExpiraEn": 1800,
                "EsBloqueada": False,
                "TokenSesion": "ABC123",
                "FechaRegistro": "2025-10-27T00:00:00",
                "UltimaFechaCambio": "2025-10-27T14:22:00",
                "EsActivo": True,
                "UsuarioExterno": {...},
                "Usuarios": {...}
            }

    Retorna:
        dict:
            {"actualizado": bool, "mensaje": str}
        o en caso de error:
            {"error": str}
    """
    try:
        logger.info(f"Actualizando reserva ID={reserva.get('Id')} en WS_GestionReservas...")

        # ======================================================
        # Función auxiliar: conversión de booleanos a string
        # ======================================================
        def bool_str(valor: bool) -> str:
            return "true" if valor else "false"

        usuario_externo = reserva.get("UsuarioExterno", {})
        usuarios = reserva.get("Usuarios", {})

        # ======================================================
        # Construcción del bloque XML <reservaEditada>
        # ======================================================
        reserva_xml = f"""
        <tem:reservaEditada>
            <tem:Id>{reserva.get("Id", 0)}</tem:Id>
            <tem:UsuarioId>{reserva.get("UsuarioId", 0)}</tem:UsuarioId>
            <tem:UsuarioExternoId>{reserva.get("UsuarioExternoId", 0)}</tem:UsuarioExternoId>
            <tem:Estado>{reserva.get("Estado", "")}</tem:Estado>
            <tem:Comentarios>{reserva.get("Comentarios", "")}</tem:Comentarios>
            <tem:CostoSubtotal>{reserva.get("CostoSubtotal", 0)}</tem:CostoSubtotal>
            <tem:CostoIVA>{reserva.get("CostoIVA", 0)}</tem:CostoIVA>
            <tem:CostoFinal>{reserva.get("CostoFinal", 0)}</tem:CostoFinal>
            <tem:MinutosRetencion>{reserva.get("MinutosRetencion", 0)}</tem:MinutosRetencion>
            <tem:ExpiraEn>{reserva.get("ExpiraEn", 0)}</tem:ExpiraEn>
            <tem:EsBloqueada>{bool_str(reserva.get("EsBloqueada", False))}</tem:EsBloqueada>
            <tem:TokenSesion>{reserva.get("TokenSesion", "")}</tem:TokenSesion>
            <tem:FechaRegistro>{reserva.get("FechaRegistro", "")}</tem:FechaRegistro>
            <tem:UltimaFechaCambio>{reserva.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
            <tem:EsActivo>{bool_str(reserva.get("EsActivo", True))}</tem:EsActivo>

            <tem:UsuarioExterno>
                <tem:Id>{usuario_externo.get("Id", 0)}</tem:Id>
                <tem:Nombre>{usuario_externo.get("Nombre", "")}</tem:Nombre>
                <tem:Email>{usuario_externo.get("Email", "")}</tem:Email>
                <tem:PasswordHash>{usuario_externo.get("PasswordHash", "")}</tem:PasswordHash>
                <tem:Rol>{usuario_externo.get("Rol", "")}</tem:Rol>
                <tem:FechaRegistro>{usuario_externo.get("FechaRegistro", "")}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{usuario_externo.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
                <tem:EsActivo>{bool_str(usuario_externo.get("EsActivo", True))}</tem:EsActivo>
                <tem:UltimaFechainicioSesion>{usuario_externo.get("UltimaFechainicioSesion", "")}</tem:UltimaFechainicioSesion>
            </tem:UsuarioExterno>

            <tem:Usuarios>
                <tem:Id>{usuarios.get("Id", 0)}</tem:Id>
                <tem:Nombre>{usuarios.get("Nombre", "")}</tem:Nombre>
                <tem:Email>{usuarios.get("Email", "")}</tem:Email>
                <tem:PasswordHash>{usuarios.get("PasswordHash", "")}</tem:PasswordHash>
                <tem:Rol>{usuarios.get("Rol", "")}</tem:Rol>
                <tem:FechaRegistro>{usuarios.get("FechaRegistro", "")}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{usuarios.get("UltimaFechaCambio", "")}</tem:UltimaFechaCambio>
                <tem:EsActivo>{bool_str(usuarios.get("EsActivo", True))}</tem:EsActivo>
                <tem:UltimaFechainicioSesion>{usuarios.get("UltimaFechainicioSesion", "")}</tem:UltimaFechainicioSesion>
            </tem:Usuarios>
        </tem:reservaEditada>
        """

        # ======================================================
        # Construcción del envelope SOAP
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:actualizarReserva>
                 {reserva_xml}
              </tem:actualizarReserva>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarReserva",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:actualizarReservaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo actualizarReservaResult en la respuesta SOAP.")
            return {"actualizado": False, "mensaje": "No se pudo confirmar la actualización de la reserva."}

        actualizado = result_node.text.strip().lower() == "true"

        if actualizado:
            logger.info(f"Reserva ID={reserva.get('Id')} actualizada correctamente.")
            return {"actualizado": True, "mensaje": "Reserva actualizada correctamente."}
        else:
            logger.warning(f"No se pudo actualizar la reserva ID={reserva.get('Id')}.")
            return {"actualizado": False, "mensaje": "El servicio no confirmó la actualización."}

    except Exception as ex:
        logger.error(f"Error en actualizarReserva(): {ex}")
        return {"error": str(ex)}

# Ejecutar directamente
if __name__ == "__main__":
    resultado = seleccionarReservas()
    print(resultado)