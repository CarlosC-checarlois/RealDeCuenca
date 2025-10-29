"""
Módulo de integración SOAP con el servicio remoto:
WS_GestionPagos.asmx

Autor: Carlos Quitus
Descripción:
    Funciones para consumir métodos SOAP relacionados con Pagos.
"""

import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
WSDL_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionPagos.asmx?WSDL"
SOAP_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionPagos.asmx"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Helpers
def _bool_str(v: bool) -> str:
    return "true" if bool(v) else "false"

def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default
def _text(node, tag, ns, default=""):
    val = node.findtext(f"tem:{tag}", default, ns)
    return val if val is not None else default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

# ==========================================================
# FUNCIÓN: actualizarPago
# ==========================================================
def actualizarPago(pago: dict) -> dict:
    """
    Actualiza la información de un pago existente mediante WS_GestionPagos.asmx/actualizarPago.

    Parámetros:
        pago (dict): Estructura esperada (claves mínimas):
            {
                "Id": int,
                "ReservaId": int,
                "Monto": float|int|str,
                "NumeroDeCedula": int|str,
                "Estado": str,
                "TransaccionReferencia": str,
                "Fuente": str,
                "FechaPago": "YYYY-MM-DDTHH:MM:SS",
                "FechaRegistro": "YYYY-MM-DDTHH:MM:SS",
                "UltimaFechaCambio": "YYYY-MM-DDTHH:MM:SS",
                "EsActivo": bool,
                # Opcional: anidar datos de la reserva (si el servicio los requiere)
                "Reservas": {
                    "Id": int,
                    "UsuarioId": int,
                    "UsuarioExternoId": int,
                    "Estado": str,
                    "Comentarios": str,
                    "CostoSubtotal": float|int|str,
                    "CostoIVA": float|int|str,
                    "CostoFinal": float|int|str,
                    "MinutosRetencion": int|str,
                    "ExpiraEn": int|str,
                    "EsBloqueada": bool,
                    "TokenSesion": str,
                    "FechaRegistro": "YYYY-MM-DDTHH:MM:SS",
                    "UltimaFechaCambio": "YYYY-MM-DDTHH:MM:SS",
                    "EsActivo": bool,
                    "UsuarioExterno": {...},
                    "Usuarios": {...}
                }
            }

    Retorna:
        dict:
            {"actualizado": bool, "mensaje": str}
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Actualizando pago ID={pago.get('Id')} (ReservaId={pago.get('ReservaId')}) en WS_GestionPagos")

        # Bloques opcionales de la reserva anidada
        reservas = pago.get("Reservas")

        # Si te piden enviar la reserva completa, la construimos; si no, omitimos el nodo
        reservas_xml = ""
        if isinstance(reservas, dict):
            usuario_externo = reservas.get("UsuarioExterno", {}) or {}
            usuarios = reservas.get("Usuarios", {}) or {}

            reservas_xml = f"""
            <tem:Reservas>
                <tem:Id>{reservas.get('Id', 0)}</tem:Id>
                <tem:UsuarioId>{reservas.get('UsuarioId', 0)}</tem:UsuarioId>
                <tem:UsuarioExternoId>{reservas.get('UsuarioExternoId', 0)}</tem:UsuarioExternoId>
                <tem:Estado>{reservas.get('Estado', '')}</tem:Estado>
                <tem:Comentarios>{reservas.get('Comentarios', '')}</tem:Comentarios>
                <tem:CostoSubtotal>{reservas.get('CostoSubtotal', 0)}</tem:CostoSubtotal>
                <tem:CostoIVA>{reservas.get('CostoIVA', 0)}</tem:CostoIVA>
                <tem:CostoFinal>{reservas.get('CostoFinal', 0)}</tem:CostoFinal>
                <tem:MinutosRetencion>{reservas.get('MinutosRetencion', 0)}</tem:MinutosRetencion>
                <tem:ExpiraEn>{reservas.get('ExpiraEn', 0)}</tem:ExpiraEn>
                <tem:EsBloqueada>{_bool_str(reservas.get('EsBloqueada', False))}</tem:EsBloqueada>
                <tem:TokenSesion>{reservas.get('TokenSesion', '')}</tem:TokenSesion>
                <tem:FechaRegistro>{reservas.get('FechaRegistro', '')}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{reservas.get('UltimaFechaCambio', '')}</tem:UltimaFechaCambio>
                <tem:EsActivo>{_bool_str(reservas.get('EsActivo', True))}</tem:EsActivo>

                <tem:UsuarioExterno>
                    <tem:Id>{usuario_externo.get('Id', 0)}</tem:Id>
                    <tem:Nombre>{usuario_externo.get('Nombre', '')}</tem:Nombre>
                    <tem:Email>{usuario_externo.get('Email', '')}</tem:Email>
                    <tem:PasswordHash>{usuario_externo.get('PasswordHash', '')}</tem:PasswordHash>
                    <tem:Rol>{usuario_externo.get('Rol', '')}</tem:Rol>
                    <tem:FechaRegistro>{usuario_externo.get('FechaRegistro', '')}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{usuario_externo.get('UltimaFechaCambio', '')}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{_bool_str(usuario_externo.get('EsActivo', True))}</tem:EsActivo>
                    <tem:UltimaFechainicioSesion>{usuario_externo.get('UltimaFechainicioSesion', '')}</tem:UltimaFechainicioSesion>
                </tem:UsuarioExterno>

                <tem:Usuarios>
                    <tem:Id>{usuarios.get('Id', 0)}</tem:Id>
                    <tem:Nombre>{usuarios.get('Nombre', '')}</tem:Nombre>
                    <tem:Email>{usuarios.get('Email', '')}</tem:Email>
                    <tem:PasswordHash>{usuarios.get('PasswordHash', '')}</tem:PasswordHash>
                    <tem:Rol>{usuarios.get('Rol', '')}</tem:Rol>
                    <tem:FechaRegistro>{usuarios.get('FechaRegistro', '')}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{usuarios.get('UltimaFechaCambio', '')}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{_bool_str(usuarios.get('EsActivo', True))}</tem:EsActivo>
                    <tem:UltimaFechainicioSesion>{usuarios.get('UltimaFechainicioSesion', '')}</tem:UltimaFechainicioSesion>
                </tem:Usuarios>
            </tem:Reservas>
            """

        # Envelope SOAP 1.1
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:actualizarPago>
              <tem:pagoEditado>
                <tem:Id>{pago.get('Id', 0)}</tem:Id>
                <tem:ReservaId>{pago.get('ReservaId', 0)}</tem:ReservaId>
                <tem:Monto>{pago.get('Monto', 0)}</tem:Monto>
                <tem:NumeroDeCedula>{pago.get('NumeroDeCedula', 0)}</tem:NumeroDeCedula>
                <tem:Estado>{pago.get('Estado', '')}</tem:Estado>
                <tem:TransaccionReferencia>{pago.get('TransaccionReferencia', '')}</tem:TransaccionReferencia>
                <tem:Fuente>{pago.get('Fuente', '')}</tem:Fuente>
                <tem:FechaPago>{pago.get('FechaPago', '')}</tem:FechaPago>
                <tem:FechaRegistro>{pago.get('FechaRegistro', '')}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{pago.get('UltimaFechaCambio', '')}</tem:UltimaFechaCambio>
                <tem:EsActivo>{_bool_str(pago.get('EsActivo', True))}</tem:EsActivo>
                {reservas_xml}
              </tem:pagoEditado>
            </tem:actualizarPago>
          </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarPago",
        }

        # Llamada HTTP
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)
        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # Parseo XML
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }
        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:actualizarPagoResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo actualizarPagoResult en la respuesta SOAP.")
            return {"actualizado": False, "mensaje": "No se pudo confirmar la actualización del pago."}

        actualizado = (result_node.text or "").strip().lower() == "true"
        if actualizado:
            logger.info(f"Pago ID={pago.get('Id')} actualizado correctamente.")
            return {"actualizado": True, "mensaje": "Pago actualizado correctamente."}
        else:
            logger.warning(f"No se pudo actualizar el pago ID={pago.get('Id')}.")
            return {"actualizado": False, "mensaje": "El servicio no confirmó la actualización del pago."}

    except Exception as ex:
        logger.error(f"Error en actualizarPago(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: buscarPorReferencia
# ======================================================
def buscarPorReferencia(referencia: str) -> dict:
    """
    Busca un pago por su referencia de transacción en WS_GestionPagos.asmx.

    Parámetros:
        referencia (str): referencia/transacción del pago

    Retorna:
        dict:
            {
              "pago": { ... },  # dict con datos del pago (o None si no existe)
              "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Buscando pago por referencia='{referencia}' en WS_GestionPagos")

        # Envelope SOAP 1.1
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:buscarPorReferencia>
                 <tem:referencia>{referencia}</tem:referencia>
              </tem:buscarPorReferencia>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/buscarPorReferencia",
        }

        resp = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)
        if resp.status_code != 200:
            logger.error(f"HTTP {resp.status_code}: {resp.text}")
            return {"error": f"HTTP {resp.status_code}", "detalle": resp.text}

        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(resp.text)
        result = root.find(".//tem:buscarPorReferenciaResult", ns)

        if result is None:
            logger.warning("No se encontró el nodo buscarPorReferenciaResult en la respuesta SOAP.")
            return {"pago": None, "mensaje": "No se encontró el pago con la referencia indicada."}

        # Pago principal
        pago = {
            "Id": safe_int(_text(result, "Id", ns, "0")),
            "ReservaId": safe_int(_text(result, "ReservaId", ns, "0")),
            "Monto": safe_float(_text(result, "Monto", ns, "0")),
            "NumeroDeCedula": _text(result, "NumeroDeCedula", ns, "0"),
            "Estado": _text(result, "Estado", ns, ""),
            "TransaccionReferencia": _text(result, "TransaccionReferencia", ns, ""),
            "Fuente": _text(result, "Fuente", ns, ""),
            "FechaPago": _text(result, "FechaPago", ns, ""),
            "FechaRegistro": _text(result, "FechaRegistro", ns, ""),
            "UltimaFechaCambio": _text(result, "UltimaFechaCambio", ns, ""),
            "EsActivo": (_text(result, "EsActivo", ns, "false").lower() == "true"),
        }

        # Reserva anidada (si viene)
        reserva_node = result.find("tem:Reservas", ns)
        if reserva_node is not None:
            pago["Reservas"] = {
                "Id": safe_int(_text(reserva_node, "Id", ns, "0")),
                "UsuarioId": safe_int(_text(reserva_node, "UsuarioId", ns, "0")),
                "UsuarioExternoId": safe_int(_text(reserva_node, "UsuarioExternoId", ns, "0")),
                "Estado": _text(reserva_node, "Estado", ns, ""),
                "Comentarios": _text(reserva_node, "Comentarios", ns, ""),
                "CostoSubtotal": safe_float(_text(reserva_node, "CostoSubtotal", ns, "0")),
                "CostoIVA": safe_float(_text(reserva_node, "CostoIVA", ns, "0")),
                "CostoFinal": safe_float(_text(reserva_node, "CostoFinal", ns, "0")),
                "MinutosRetencion": safe_int(_text(reserva_node, "MinutosRetencion", ns, "0")),
                "ExpiraEn": safe_int(_text(reserva_node, "ExpiraEn", ns, "0")),
                "EsBloqueada": (_text(reserva_node, "EsBloqueada", ns, "false").lower() == "true"),
                "TokenSesion": _text(reserva_node, "TokenSesion", ns, ""),
                "FechaRegistro": _text(reserva_node, "FechaRegistro", ns, ""),
                "UltimaFechaCambio": _text(reserva_node, "UltimaFechaCambio", ns, ""),
                "EsActivo": (_text(reserva_node, "EsActivo", ns, "false").lower() == "true"),
            }

        logger.info(f"Pago con referencia '{referencia}' obtenido correctamente.")
        return {"pago": pago, "mensaje": "Pago obtenido correctamente."}

    except Exception as ex:
        logger.error(f"Error en buscarPorReferencia(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: calcularTotalPagado
# ======================================================
def calcularTotalPagado(reserva_id: int) -> dict:
    """
    Calcula el monto total pagado por una reserva específica en el servicio SOAP WS_GestionPagos.

    Parámetros:
        reserva_id (int): ID de la reserva.

    Retorna:
        dict:
            {
                "reserva_id": int,
                "total_pagado": float,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Calculando total pagado para la reserva ID={reserva_id} en WS_GestionPagos")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:calcularTotalPagado>
                 <tem:reservaId>{reserva_id}</tem:reservaId>
              </tem:calcularTotalPagado>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/calcularTotalPagado",
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
        result_node = root.find(".//tem:calcularTotalPagadoResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo calcularTotalPagadoResult en la respuesta SOAP.")
            return {"reserva_id": reserva_id, "total_pagado": 0.0, "mensaje": "No se pudo obtener el total pagado."}

        # ======================================================
        # Obtención del valor numérico
        # ======================================================
        total_pagado = 0.0
        try:
            total_pagado = float(result_node.text.strip())
        except (ValueError, AttributeError):
            logger.warning("El valor devuelto por calcularTotalPagado no es numérico.")
            total_pagado = 0.0

        logger.info(f"Total pagado para reserva ID={reserva_id}: {total_pagado:.2f}")
        return {
            "reserva_id": reserva_id,
            "total_pagado": total_pagado,
            "mensaje": f"Total pagado calculado correctamente: {total_pagado:.2f}"
        }

    except Exception as ex:
        logger.error(f"Error en calcularTotalPagado(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: eliminarPago
# ======================================================
def eliminarPago(pago_id: int) -> dict:
    """
    Elimina (desactiva mediante Soft Delete) un pago en el servicio SOAP WS_GestionPagos.

    Parámetros:
        pago_id (int): ID del pago a eliminar.

    Retorna:
        dict:
            {
                "eliminado": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Eliminando pago ID={pago_id} en WS_GestionPagos")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:eliminarPago>
                 <tem:id>{pago_id}</tem:id>
              </tem:eliminarPago>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/eliminarPago",
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
        result_node = root.find(".//tem:eliminarPagoResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo eliminarPagoResult en la respuesta SOAP.")
            return {"eliminado": False, "mensaje": "No se pudo confirmar la eliminación del pago."}

        # ======================================================
        # Interpretación del resultado booleano
        # ======================================================
        eliminado = (result_node.text or "").strip().lower() == "true"

        if eliminado:
            logger.info(f"Pago ID={pago_id} eliminado correctamente (Soft Delete).")
            return {"eliminado": True, "mensaje": f"Pago ID={pago_id} eliminado correctamente."}
        else:
            logger.warning(f"El servicio no confirmó la eliminación del pago ID={pago_id}.")
            return {"eliminado": False, "mensaje": f"No se pudo eliminar el pago ID={pago_id}."}

    except Exception as ex:
        logger.error(f"Error en eliminarPago(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: insertarPago
# ======================================================
def insertarPago(nuevo_pago: dict) -> dict:
    """
    Inserta un nuevo registro de pago en el servicio SOAP WS_GestionPagos.

    Parámetros:
        nuevo_pago (dict): Datos del pago. Ejemplo:
            {
                "ReservaId": 1,
                "Monto": 350.46,
                "NumeroDeCedula": "1712345678",
                "Estado": "Pagado",
                "TransaccionReferencia": "PAY-2025-0001",
                "Fuente": "TarjetaCredito",
                "FechaPago": "2025-10-28T14:30:00",
                "FechaRegistro": "2025-10-28T14:30:00",
                "UltimaFechaCambio": "2025-10-28T14:30:00",
                "EsActivo": True
            }

    Retorna:
        dict:
            {
                "pago_id": int,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Insertando nuevo pago en WS_GestionPagos: {nuevo_pago.get('TransaccionReferencia')}")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        def bool_to_str(val):
            return "true" if val else "false"

        # Normaliza fechas en formato ISO si no vienen
        def fmt_fecha(valor):
            if not valor:
                return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            return valor

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:insertarPago>
                 <tem:nuevoPago>
                    <tem:Id>0</tem:Id>
                    <tem:ReservaId>{nuevo_pago.get('ReservaId', 0)}</tem:ReservaId>
                    <tem:Monto>{nuevo_pago.get('Monto', 0)}</tem:Monto>
                    <tem:NumeroDeCedula>{nuevo_pago.get('NumeroDeCedula', '')}</tem:NumeroDeCedula>
                    <tem:Estado>{nuevo_pago.get('Estado', '')}</tem:Estado>
                    <tem:TransaccionReferencia>{nuevo_pago.get('TransaccionReferencia', '')}</tem:TransaccionReferencia>
                    <tem:Fuente>{nuevo_pago.get('Fuente', '')}</tem:Fuente>
                    <tem:FechaPago>{fmt_fecha(nuevo_pago.get('FechaPago'))}</tem:FechaPago>
                    <tem:FechaRegistro>{fmt_fecha(nuevo_pago.get('FechaRegistro'))}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{fmt_fecha(nuevo_pago.get('UltimaFechaCambio'))}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{bool_to_str(nuevo_pago.get('EsActivo', True))}</tem:EsActivo>
                 </tem:nuevoPago>
              </tem:insertarPago>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/insertarPago",
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
        result_node = root.find(".//tem:insertarPagoResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo insertarPagoResult en la respuesta SOAP.")
            return {"pago_id": None, "mensaje": "No se recibió confirmación de inserción."}

        # ======================================================
        # Obtención del ID del nuevo pago
        # ======================================================
        try:
            pago_id = int(result_node.text.strip())
        except (ValueError, AttributeError):
            pago_id = None

        if pago_id and pago_id > 0:
            logger.info(f"Pago insertado correctamente con ID={pago_id}")
            return {"pago_id": pago_id, "mensaje": f"Pago insertado correctamente con ID={pago_id}"}
        else:
            logger.warning("El servicio no devolvió un ID válido para el pago insertado.")
            return {"pago_id": None, "mensaje": "No se pudo insertar el pago o no se devolvió un ID válido."}

    except Exception as ex:
        logger.error(f"Error en insertarPago(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: obtenerPagosPorEstado
# ======================================================
def obtenerPagosPorEstado(estado: str) -> dict:
    """
    Obtiene todos los pagos según su estado desde el servicio SOAP WS_GestionPagos.

    Parámetros:
        estado (str): Estado del pago. Ejemplo: "Pendiente", "Pagado", "Completado".

    Retorna:
        dict:
            {
                "estado": str,
                "cantidad": int,
                "pagos": [
                    {
                        "Id": int,
                        "ReservaId": int,
                        "Monto": float,
                        "NumeroDeCedula": str,
                        "Estado": str,
                        "TransaccionReferencia": str,
                        "Fuente": str,
                        "FechaPago": str,
                        "FechaRegistro": str,
                        "UltimaFechaCambio": str,
                        "EsActivo": bool
                    },
                    ...
                ],
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Consultando pagos con estado='{estado}' en WS_GestionPagos")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:obtenerPagosPorEstado>
                 <tem:estado>{estado}</tem:estado>
              </tem:obtenerPagosPorEstado>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/obtenerPagosPorEstado",
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
        pagos_nodes = root.findall(".//tem:Pagos", ns)

        if not pagos_nodes:
            logger.warning(f"No se encontraron pagos con estado '{estado}'.")
            return {
                "estado": estado,
                "cantidad": 0,
                "pagos": [],
                "mensaje": f"No se encontraron pagos con estado '{estado}'."
            }

        # ======================================================
        # Extracción de datos de cada pago
        # ======================================================
        pagos = []
        for nodo in pagos_nodes:
            try:
                pago = {
                    "Id": int(nodo.findtext("tem:Id", default="0", namespaces=ns)),
                    "ReservaId": int(nodo.findtext("tem:ReservaId", default="0", namespaces=ns)),
                    "Monto": float(nodo.findtext("tem:Monto", default="0", namespaces=ns)),
                    "NumeroDeCedula": nodo.findtext("tem:NumeroDeCedula", default="", namespaces=ns),
                    "Estado": nodo.findtext("tem:Estado", default="", namespaces=ns),
                    "TransaccionReferencia": nodo.findtext("tem:TransaccionReferencia", default="", namespaces=ns),
                    "Fuente": nodo.findtext("tem:Fuente", default="", namespaces=ns),
                    "FechaPago": nodo.findtext("tem:FechaPago", default="", namespaces=ns),
                    "FechaRegistro": nodo.findtext("tem:FechaRegistro", default="", namespaces=ns),
                    "UltimaFechaCambio": nodo.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                    "EsActivo": nodo.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true"
                }
                pagos.append(pago)
            except Exception as ex_p:
                logger.warning(f"Error procesando nodo de pago: {ex_p}")

        logger.info(f"Se obtuvieron {len(pagos)} pagos con estado '{estado}'.")
        return {
            "estado": estado,
            "cantidad": len(pagos),
            "pagos": pagos,
            "mensaje": f"Pagos con estado '{estado}' obtenidos correctamente."
        }

    except Exception as ex:
        logger.error(f"Error en obtenerPagosPorEstado(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: seleccionarPagoPorId
# ======================================================
def seleccionarPagoPorId(pago_id: int) -> dict:
    """
    Obtiene un pago específico por su ID desde el servicio SOAP WS_GestionPagos.

    Parámetros:
        pago_id (int): ID del pago a consultar.

    Retorna:
        dict:
            {
                "pago": {...},
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Consultando pago con ID={pago_id} en WS_GestionPagos")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarPagoPorId>
                 <tem:id>{pago_id}</tem:id>
              </tem:seleccionarPagoPorId>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPagoPorId",
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
        result_node = root.find(".//tem:seleccionarPagoPorIdResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo seleccionarPagoPorIdResult en la respuesta SOAP.")
            return {"pago": None, "mensaje": "No se encontró el pago solicitado."}

        # ======================================================
        # Extracción de datos del pago
        # ======================================================
        pago = {
            "Id": int(result_node.findtext("tem:Id", "0", ns)),
            "ReservaId": int(result_node.findtext("tem:ReservaId", "0", ns)),
            "Monto": float(result_node.findtext("tem:Monto", "0", ns)),
            "NumeroDeCedula": result_node.findtext("tem:NumeroDeCedula", "", ns),
            "Estado": result_node.findtext("tem:Estado", "", ns),
            "TransaccionReferencia": result_node.findtext("tem:TransaccionReferencia", "", ns),
            "Fuente": result_node.findtext("tem:Fuente", "", ns),
            "FechaPago": result_node.findtext("tem:FechaPago", "", ns),
            "FechaRegistro": result_node.findtext("tem:FechaRegistro", "", ns),
            "UltimaFechaCambio": result_node.findtext("tem:UltimaFechaCambio", "", ns),
            "EsActivo": result_node.findtext("tem:EsActivo", "false", ns).lower() == "true"
        }

        # ======================================================
        # Extracción de datos de la reserva anidada (si existe)
        # ======================================================
        reserva_node = result_node.find(".//tem:Reservas", ns)
        if reserva_node is not None:
            pago["Reserva"] = {
                "Id": int(reserva_node.findtext("tem:Id", "0", ns)),
                "UsuarioId": int(reserva_node.findtext("tem:UsuarioId", "0", ns)),
                "UsuarioExternoId": int(reserva_node.findtext("tem:UsuarioExternoId", "0", ns)),
                "Estado": reserva_node.findtext("tem:Estado", "", ns),
                "Comentarios": reserva_node.findtext("tem:Comentarios", "", ns),
                "CostoSubtotal": float(reserva_node.findtext("tem:CostoSubtotal", "0", ns)),
                "CostoIVA": float(reserva_node.findtext("tem:CostoIVA", "0", ns)),
                "CostoFinal": float(reserva_node.findtext("tem:CostoFinal", "0", ns)),
                "MinutosRetencion": int(reserva_node.findtext("tem:MinutosRetencion", "0", ns)),
                "ExpiraEn": int(reserva_node.findtext("tem:ExpiraEn", "0", ns)),
                "EsBloqueada": reserva_node.findtext("tem:EsBloqueada", "false", ns).lower() == "true",
                "TokenSesion": reserva_node.findtext("tem:TokenSesion", "", ns),
                "FechaRegistro": reserva_node.findtext("tem:FechaRegistro", "", ns),
                "UltimaFechaCambio": reserva_node.findtext("tem:UltimaFechaCambio", "", ns),
                "EsActivo": reserva_node.findtext("tem:EsActivo", "false", ns).lower() == "true"
            }

        logger.info(f"Pago ID={pago_id} obtenido correctamente.")
        return {"pago": pago, "mensaje": "Pago obtenido correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarPagoPorId(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: seleccionarPagos
# ======================================================
def seleccionarPagos() -> dict:
    """
    Obtiene todos los pagos activos desde el servicio WS_GestionPagos.asmx.

    Retorna:
        dict: {
            "pagos": [ {...}, {...}, ... ],
            "total": int,
            "mensaje": str
        }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info("Consultando todos los pagos activos en WS_GestionPagos")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarPagos/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPagos",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo del XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        pagos_nodes = root.findall(".//tem:Pagos", ns)

        pagos = []
        for pago_node in pagos_nodes:
            pago = {
                "Id": int(pago_node.findtext("tem:Id", "0", ns)),
                "ReservaId": int(pago_node.findtext("tem:ReservaId", "0", ns)),
                "Monto": float(pago_node.findtext("tem:Monto", "0", ns)),
                "NumeroDeCedula": pago_node.findtext("tem:NumeroDeCedula", "", ns),
                "Estado": pago_node.findtext("tem:Estado", "", ns),
                "TransaccionReferencia": pago_node.findtext("tem:TransaccionReferencia", "", ns),
                "Fuente": pago_node.findtext("tem:Fuente", "", ns),
                "FechaPago": pago_node.findtext("tem:FechaPago", "", ns),
                "FechaRegistro": pago_node.findtext("tem:FechaRegistro", "", ns),
                "UltimaFechaCambio": pago_node.findtext("tem:UltimaFechaCambio", "", ns),
                "EsActivo": pago_node.findtext("tem:EsActivo", "false", ns).lower() == "true",
            }

            # Datos de la reserva (si existen)
            reserva_node = pago_node.find(".//tem:Reservas", ns)
            if reserva_node is not None:
                pago["Reserva"] = {
                    "Id": int(reserva_node.findtext("tem:Id", "0", ns)),
                    "UsuarioId": int(reserva_node.findtext("tem:UsuarioId", "0", ns)),
                    "UsuarioExternoId": int(reserva_node.findtext("tem:UsuarioExternoId", "0", ns)),
                    "Estado": reserva_node.findtext("tem:Estado", "", ns),
                    "Comentarios": reserva_node.findtext("tem:Comentarios", "", ns),
                    "CostoSubtotal": float(reserva_node.findtext("tem:CostoSubtotal", "0", ns)),
                    "CostoIVA": float(reserva_node.findtext("tem:CostoIVA", "0", ns)),
                    "CostoFinal": float(reserva_node.findtext("tem:CostoFinal", "0", ns)),
                    "MinutosRetencion": int(reserva_node.findtext("tem:MinutosRetencion", "0", ns)),
                    "ExpiraEn": int(reserva_node.findtext("tem:ExpiraEn", "0", ns)),
                    "EsBloqueada": reserva_node.findtext("tem:EsBloqueada", "false", ns).lower() == "true",
                    "TokenSesion": reserva_node.findtext("tem:TokenSesion", "", ns),
                    "FechaRegistro": reserva_node.findtext("tem:FechaRegistro", "", ns),
                    "UltimaFechaCambio": reserva_node.findtext("tem:UltimaFechaCambio", "", ns),
                    "EsActivo": reserva_node.findtext("tem:EsActivo", "false", ns).lower() == "true"
                }

            pagos.append(pago)

        logger.info(f"Se obtuvieron {len(pagos)} pagos activos correctamente.")
        return {
            "pagos": pagos,
            "total": len(pagos),
            "mensaje": f"Se encontraron {len(pagos)} pagos activos."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarPagos(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: seleccionarPagosPorReserva
# ======================================================
def seleccionarPagosPorReserva(reserva_id: int) -> dict:
    """
    Obtiene todos los pagos asociados a una reserva específica desde el servicio WS_GestionPagos.asmx.

    Parámetros:
        reserva_id (int): ID de la reserva a consultar.

    Retorna:
        dict:
            {
                "reserva_id": int,
                "pagos": [ {...}, {...} ],
                "total": int,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Consultando pagos asociados a la reserva ID={reserva_id} en WS_GestionPagos")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarPagosPorReserva>
                 <tem:reservaId>{reserva_id}</tem:reservaId>
              </tem:seleccionarPagosPorReserva>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPagosPorReserva",
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
        pagos_nodes = root.findall(".//tem:Pagos", ns)

        if not pagos_nodes:
            logger.warning(f"No se encontraron pagos para la reserva ID={reserva_id}")
            return {
                "reserva_id": reserva_id,
                "pagos": [],
                "total": 0,
                "mensaje": f"No existen pagos asociados a la reserva ID={reserva_id}."
            }

        # ======================================================
        # Extracción de datos
        # ======================================================
        pagos = []
        for pago_node in pagos_nodes:
            pago = {
                "Id": int(pago_node.findtext("tem:Id", "0", ns)),
                "ReservaId": int(pago_node.findtext("tem:ReservaId", "0", ns)),
                "Monto": float(pago_node.findtext("tem:Monto", "0", ns)),
                "NumeroDeCedula": pago_node.findtext("tem:NumeroDeCedula", "", ns),
                "Estado": pago_node.findtext("tem:Estado", "", ns),
                "TransaccionReferencia": pago_node.findtext("tem:TransaccionReferencia", "", ns),
                "Fuente": pago_node.findtext("tem:Fuente", "", ns),
                "FechaPago": pago_node.findtext("tem:FechaPago", "", ns),
                "FechaRegistro": pago_node.findtext("tem:FechaRegistro", "", ns),
                "UltimaFechaCambio": pago_node.findtext("tem:UltimaFechaCambio", "", ns),
                "EsActivo": pago_node.findtext("tem:EsActivo", "false", ns).lower() == "true",
            }

            # Extraer información de la reserva anidada
            reserva_node = pago_node.find(".//tem:Reservas", ns)
            if reserva_node is not None:
                pago["Reserva"] = {
                    "Id": int(reserva_node.findtext("tem:Id", "0", ns)),
                    "UsuarioId": int(reserva_node.findtext("tem:UsuarioId", "0", ns)),
                    "UsuarioExternoId": int(reserva_node.findtext("tem:UsuarioExternoId", "0", ns)),
                    "Estado": reserva_node.findtext("tem:Estado", "", ns),
                    "Comentarios": reserva_node.findtext("tem:Comentarios", "", ns),
                    "CostoSubtotal": float(reserva_node.findtext("tem:CostoSubtotal", "0", ns)),
                    "CostoIVA": float(reserva_node.findtext("tem:CostoIVA", "0", ns)),
                    "CostoFinal": float(reserva_node.findtext("tem:CostoFinal", "0", ns)),
                    "MinutosRetencion": int(reserva_node.findtext("tem:MinutosRetencion", "0", ns)),
                    "ExpiraEn": int(reserva_node.findtext("tem:ExpiraEn", "0", ns)),
                    "EsBloqueada": reserva_node.findtext("tem:EsBloqueada", "false", ns).lower() == "true",
                    "TokenSesion": reserva_node.findtext("tem:TokenSesion", "", ns),
                    "FechaRegistro": reserva_node.findtext("tem:FechaRegistro", "", ns),
                    "UltimaFechaCambio": reserva_node.findtext("tem:UltimaFechaCambio", "", ns),
                    "EsActivo": reserva_node.findtext("tem:EsActivo", "false", ns).lower() == "true"
                }

            pagos.append(pago)

        logger.info(f"Se obtuvieron {len(pagos)} pagos para la reserva ID={reserva_id}.")
        return {
            "reserva_id": reserva_id,
            "pagos": pagos,
            "total": len(pagos),
            "mensaje": f"Pagos asociados a la reserva ID={reserva_id} obtenidos correctamente."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarPagosPorReserva(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: obtenerPagosPorUsuario
# ======================================================
def obtenerPagosPorUsuario(usuarioId: int = None, usuarioExternoId: int = None) -> dict:
    """
    Obtiene los pagos asociados a un usuario interno o externo.

    Parámetros:
        usuarioId (int, opcional): ID del usuario interno.
        usuarioExternoId (int, opcional): ID del usuario externo.

    Retorna:
        dict:
            {
                "exito": bool,
                "pagos": [ {...}, {...} ],
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Obteniendo pagos - usuarioId={usuarioId}, usuarioExternoId={usuarioExternoId}")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        if not usuarioId and not usuarioExternoId:
            return {"error": "Debe especificar al menos 'usuarioId' o 'usuarioExternoId'."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:obtenerPagosPorUsuario>
                 <tem:usuarioId>{usuarioId if usuarioId else 0}</tem:usuarioId>
                 <tem:usuarioExternoId>{usuarioExternoId if usuarioExternoId else 0}</tem:usuarioExternoId>
              </tem:obtenerPagosPorUsuario>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/obtenerPagosPorUsuario",
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
        result_node = root.find(".//tem:obtenerPagosPorUsuarioResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'obtenerPagosPorUsuarioResult' en la respuesta SOAP.")
            return {"exito": False, "pagos": [], "mensaje": "No se encontraron pagos asociados."}

        # ======================================================
        # Procesar nodos DTO_WS_IntegracionPago
        # ======================================================
        pagos = []
        for pago_node in result_node.findall("tem:DTO_WS_IntegracionPago", ns):
            try:
                pago = {
                    "PagoId": int(pago_node.findtext("tem:PagoId", default="0", namespaces=ns)),
                    "ReservaId": int(pago_node.findtext("tem:ReservaId", default="0", namespaces=ns)),
                    "Monto": float(pago_node.findtext("tem:Monto", default="0", namespaces=ns)),
                    "NumeroDeCedula": pago_node.findtext("tem:NumeroDeCedula", default="", namespaces=ns),
                    "Estado": pago_node.findtext("tem:Estado", default="", namespaces=ns),
                    "TransaccionReferencia": pago_node.findtext("tem:TransaccionReferencia", default="", namespaces=ns),
                    "Fuente": pago_node.findtext("tem:Fuente", default="", namespaces=ns),
                    "FechaPago": pago_node.findtext("tem:FechaPago", default="", namespaces=ns),
                    "FechaRegistro": pago_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                    "CostoFinal": float(pago_node.findtext("tem:CostoFinal", default="0", namespaces=ns)),
                    "EstadoReserva": pago_node.findtext("tem:EstadoReserva", default="", namespaces=ns),
                    "FechaReserva": pago_node.findtext("tem:FechaReserva", default="", namespaces=ns),
                    "NombreUsuario": pago_node.findtext("tem:NombreUsuario", default="", namespaces=ns),
                    "EmailUsuario": pago_node.findtext("tem:EmailUsuario", default="", namespaces=ns),
                    "NombreUsuarioExterno": pago_node.findtext("tem:NombreUsuarioExterno", default="", namespaces=ns),
                    "EmailUsuarioExterno": pago_node.findtext("tem:EmailUsuarioExterno", default="", namespaces=ns),
                }
                pagos.append(pago)
            except Exception as e:
                logger.warning(f"Error al procesar un nodo DTO_WS_IntegracionPago: {e}")

        if not pagos:
            logger.info("No se encontraron pagos para este usuario.")
            return {"exito": True, "pagos": [], "mensaje": "No hay pagos registrados para este usuario."}

        logger.info(f"Se encontraron {len(pagos)} pagos asociados al usuario.")
        return {"exito": True, "pagos": pagos, "mensaje": "Pagos obtenidos correctamente."}

    except Exception as ex:
        logger.error(f"Error en obtenerPagosPorUsuario(): {ex}")
        return {"error": str(ex)}