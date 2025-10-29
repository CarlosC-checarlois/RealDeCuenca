import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ======================================================
# CONFIGURACIÓN GLOBAL
# ======================================================
SOAP_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionResXEsp.asmx"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ======================================================
# FUNCIÓN: seleccionarRelaciones
# ======================================================
def seleccionarRelaciones() -> dict:
    """
    Obtiene todas las relaciones activas entre reservas y espacios desde WS_GestionResXEsp.asmx.

    Retorna:
        dict:
            {
                "exito": bool,
                "relaciones": [ {...}, {...} ],
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info("Consultando todas las relaciones activas entre reservas y espacios...")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarRelaciones/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarRelaciones",
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
        result_node = root.find(".//tem:seleccionarRelacionesResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarRelacionesResult' en la respuesta SOAP.")
            return {"exito": False, "relaciones": [], "mensaje": "No se encontraron relaciones activas."}

        # ======================================================
        # Procesar nodos RESXESP
        # ======================================================
        relaciones = []
        for rel_node in result_node.findall("tem:RESXESP", ns):
            try:
                relacion = {
                    "Id": int(rel_node.findtext("tem:Id", default="0", namespaces=ns)),
                    "CostoCalculado": float(rel_node.findtext("tem:CostoCalculado", default="0", namespaces=ns)),
                    "PuntuacionUsuario": int(rel_node.findtext("tem:PuntuacionUsuario", default="0", namespaces=ns)),
                    "FechaInicio": rel_node.findtext("tem:FechaInicio", default="", namespaces=ns),
                    "FechaFin": rel_node.findtext("tem:FechaFin", default="", namespaces=ns),
                    "ReservaId": int(rel_node.findtext("tem:ReservaId", default="0", namespaces=ns)),
                    "EspacioId": int(rel_node.findtext("tem:EspacioId", default="0", namespaces=ns)),
                    "MinutosRetencion": int(rel_node.findtext("tem:MinutosRetencion", default="0", namespaces=ns)),
                    "ExpiraEn": int(rel_node.findtext("tem:ExpiraEn", default="0", namespaces=ns)),
                    "EsBloqueada": rel_node.findtext("tem:EsBloqueada", default="false", namespaces=ns).lower() == "true",
                    "TokenSesion": rel_node.findtext("tem:TokenSesion", default="", namespaces=ns),
                    "FechaRegistro": rel_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                    "UltimaFechaCambio": rel_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                    "EsActivo": rel_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
                }

                # Extraer datos básicos de la reserva y espacio (si existen)
                espacio_node = rel_node.find("tem:Espacios", ns)
                reserva_node = rel_node.find("tem:Reservas", ns)

                if espacio_node is not None:
                    relacion["Espacio"] = {
                        "Id": int(espacio_node.findtext("tem:Id", default="0", namespaces=ns)),
                        "Nombre": espacio_node.findtext("tem:Nombre", default="", namespaces=ns),
                        "Moneda": espacio_node.findtext("tem:Moneda", default="", namespaces=ns),
                        "CostoDiario": float(espacio_node.findtext("tem:CostoDiario", default="0", namespaces=ns)),
                        "CapacidadAdultos": int(espacio_node.findtext("tem:CapacidadAdultos", default="0", namespaces=ns)),
                        "CapacidadNinios": int(espacio_node.findtext("tem:CapacidadNinios", default="0", namespaces=ns)),
                        "Ubicacion": espacio_node.findtext("tem:Ubicacion", default="", namespaces=ns),
                    }

                if reserva_node is not None:
                    relacion["Reserva"] = {
                        "Id": int(reserva_node.findtext("tem:Id", default="0", namespaces=ns)),
                        "UsuarioId": int(reserva_node.findtext("tem:UsuarioId", default="0", namespaces=ns)),
                        "Estado": reserva_node.findtext("tem:Estado", default="", namespaces=ns),
                        "CostoFinal": float(reserva_node.findtext("tem:CostoFinal", default="0", namespaces=ns)),
                        "Comentarios": reserva_node.findtext("tem:Comentarios", default="", namespaces=ns),
                    }

                relaciones.append(relacion)

            except Exception as e:
                logger.warning(f"Error al procesar una relación: {e}")

        if not relaciones:
            logger.info("No se encontraron relaciones activas.")
            return {"exito": True, "relaciones": [], "mensaje": "No hay relaciones activas registradas."}

        logger.info(f"Se encontraron {len(relaciones)} relaciones activas.")
        return {"exito": True, "relaciones": relaciones, "mensaje": "Relaciones obtenidas correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarRelaciones(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: seleccionarPorReserva
# ======================================================
def seleccionarPorReserva(reservaId: int) -> dict:
    """
    Obtiene todas las relaciones asociadas a una reserva específica desde WS_GestionResXEsp.asmx.
    """

    try:
        if not isinstance(reservaId, int) or reservaId <= 0:
            return {"error": "Debe proporcionar un 'reservaId' válido (entero mayor que 0)."}

        logger.info(f"Consultando relaciones asociadas a la reserva ID={reservaId}...")

        # Envelope SOAP correcto
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <seleccionarPorReserva xmlns="http://tempuri.org/">
              <reservaId>{reservaId}</reservaId>
            </seleccionarPorReserva>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPorReserva",
        }

        # Envío de la solicitud
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # Parsear XML
        root = ET.fromstring(response.text)

        # Detectar namespace del servicio
        ns_tempuri = "{http://tempuri.org/}"

        # Buscar los elementos RESXESP dentro del resultado
        relaciones = []
        for rel_node in root.findall(f".//{ns_tempuri}RESXESP"):
            relacion = {
                "Id": int(rel_node.findtext(f"{ns_tempuri}Id", "0")),
                "CostoCalculado": float(rel_node.findtext(f"{ns_tempuri}CostoCalculado", "0")),
                "PuntuacionUsuario": rel_node.findtext(f"{ns_tempuri}PuntuacionUsuario"),
                "FechaInicio": rel_node.findtext(f"{ns_tempuri}FechaInicio"),
                "FechaFin": rel_node.findtext(f"{ns_tempuri}FechaFin"),
                "ReservaId": int(rel_node.findtext(f"{ns_tempuri}ReservaId", "0")),
                "EspacioId": int(rel_node.findtext(f"{ns_tempuri}EspacioId", "0")),
                "MinutosRetencion": int(rel_node.findtext(f"{ns_tempuri}MinutosRetencion", "0")),
                "ExpiraEn": int(rel_node.findtext(f"{ns_tempuri}ExpiraEn", "0")),
                "EsBloqueada": rel_node.findtext(f"{ns_tempuri}EsBloqueada", "false").lower() == "true",
                "TokenSesion": rel_node.findtext(f"{ns_tempuri}TokenSesion", ""),
                "FechaRegistro": rel_node.findtext(f"{ns_tempuri}FechaRegistro"),
                "UltimaFechaCambio": rel_node.findtext(f"{ns_tempuri}UltimaFechaCambio"),
                "EsActivo": rel_node.findtext(f"{ns_tempuri}EsActivo", "false").lower() == "true",
            }
            relaciones.append(relacion)

        if not relaciones:
            logger.info("No se encontraron relaciones asociadas a esta reserva.")
            return {"exito": True, "relaciones": [], "mensaje": "No existen relaciones para esta reserva."}

        logger.info(f"Se encontraron {len(relaciones)} relaciones para la reserva {reservaId}.")
        return {"exito": True, "relaciones": relaciones, "mensaje": "Relaciones obtenidas correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarPorReserva(): {ex}")
        return {"error": str(ex)}
# ======================================================
# FUNCIÓN: seleccionarPorId
# ======================================================
def seleccionarPorId(relacionId: int) -> dict:
    """
    Obtiene una relación específica entre reserva y espacio por su ID desde WS_GestionResXEsp.asmx.

    Parámetros:
        relacionId (int): ID de la relación a consultar.

    Retorna:
        dict:
            {
                "exito": bool,
                "relacion": {...},
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        if not isinstance(relacionId, int) or relacionId <= 0:
            return {"error": "Debe proporcionar un 'relacionId' válido (entero mayor que 0)."}

        logger.info(f"Consultando relación con ID={relacionId}...")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarPorId>
                 <tem:id>{relacionId}</tem:id>
              </tem:seleccionarPorId>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPorId",
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
        result_node = root.find(".//tem:seleccionarPorIdResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarPorIdResult' en la respuesta SOAP.")
            return {"exito": False, "relacion": None, "mensaje": "No se encontró la relación solicitada."}

        # ======================================================
        # Procesar nodo principal RESXESP
        # ======================================================
        relacion = {
            "Id": int(result_node.findtext("tem:Id", default="0", namespaces=ns)),
            "CostoCalculado": float(result_node.findtext("tem:CostoCalculado", default="0", namespaces=ns)),
            "PuntuacionUsuario": int(result_node.findtext("tem:PuntuacionUsuario", default="0", namespaces=ns)),
            "FechaInicio": result_node.findtext("tem:FechaInicio", default="", namespaces=ns),
            "FechaFin": result_node.findtext("tem:FechaFin", default="", namespaces=ns),
            "ReservaId": int(result_node.findtext("tem:ReservaId", default="0", namespaces=ns)),
            "EspacioId": int(result_node.findtext("tem:EspacioId", default="0", namespaces=ns)),
            "MinutosRetencion": int(result_node.findtext("tem:MinutosRetencion", default="0", namespaces=ns)),
            "ExpiraEn": int(result_node.findtext("tem:ExpiraEn", default="0", namespaces=ns)),
            "EsBloqueada": result_node.findtext("tem:EsBloqueada", default="false", namespaces=ns).lower() == "true",
            "TokenSesion": result_node.findtext("tem:TokenSesion", default="", namespaces=ns),
            "FechaRegistro": result_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
            "UltimaFechaCambio": result_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
            "EsActivo": result_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
        }

        # ------------------------------------------------------
        # Procesar el nodo Espacios
        # ------------------------------------------------------
        espacio_node = result_node.find("tem:Espacios", ns)
        if espacio_node is not None:
            relacion["Espacio"] = {
                "Id": int(espacio_node.findtext("tem:Id", default="0", namespaces=ns)),
                "Nombre": espacio_node.findtext("tem:Nombre", default="", namespaces=ns),
                "Moneda": espacio_node.findtext("tem:Moneda", default="", namespaces=ns),
                "CostoDiario": float(espacio_node.findtext("tem:CostoDiario", default="0", namespaces=ns)),
                "CapacidadAdultos": int(espacio_node.findtext("tem:CapacidadAdultos", default="0", namespaces=ns)),
                "CapacidadNinios": int(espacio_node.findtext("tem:CapacidadNinios", default="0", namespaces=ns)),
                "Ubicacion": espacio_node.findtext("tem:Ubicacion", default="", namespaces=ns),
                "DescripcionDelLugar": espacio_node.findtext("tem:DescripcionDelLugar", default="", namespaces=ns),
                "Puntuacion": int(espacio_node.findtext("tem:Puntuacion", default="0", namespaces=ns)),
                "Hotel": {
                    "Id": int(espacio_node.findtext("tem:Hotel/tem:Id", default="0", namespaces=ns)),
                    "Nombre": espacio_node.findtext("tem:Hotel/tem:Nombre", default="", namespaces=ns),
                },
                "TipoServicio": {
                    "Id": int(espacio_node.findtext("tem:TipoServicio/tem:Id", default="0", namespaces=ns)),
                    "Nombre": espacio_node.findtext("tem:TipoServicio/tem:Nombre", default="", namespaces=ns),
                },
                "TipoAlimentacion": {
                    "Id": int(espacio_node.findtext("tem:TipoAlimentacion/tem:Id", default="0", namespaces=ns)),
                    "Nombre": espacio_node.findtext("tem:TipoAlimentacion/tem:Nombre", default="", namespaces=ns),
                },
            }

        # ------------------------------------------------------
        # Procesar el nodo Reservas
        # ------------------------------------------------------
        reserva_node = result_node.find("tem:Reservas", ns)
        if reserva_node is not None:
            relacion["Reserva"] = {
                "Id": int(reserva_node.findtext("tem:Id", default="0", namespaces=ns)),
                "UsuarioId": int(reserva_node.findtext("tem:UsuarioId", default="0", namespaces=ns)),
                "UsuarioExternoId": int(reserva_node.findtext("tem:UsuarioExternoId", default="0", namespaces=ns)),
                "Estado": reserva_node.findtext("tem:Estado", default="", namespaces=ns),
                "CostoFinal": float(reserva_node.findtext("tem:CostoFinal", default="0", namespaces=ns)),
                "Comentarios": reserva_node.findtext("tem:Comentarios", default="", namespaces=ns),
                "FechaRegistro": reserva_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UsuarioInterno": {
                    "Id": int(reserva_node.findtext("tem:Usuarios/tem:Id", default="0", namespaces=ns)),
                    "Nombre": reserva_node.findtext("tem:Usuarios/tem:Nombre", default="", namespaces=ns),
                    "Email": reserva_node.findtext("tem:Usuarios/tem:Email", default="", namespaces=ns),
                    "Rol": reserva_node.findtext("tem:Usuarios/tem:Rol", default="", namespaces=ns),
                },
                "UsuarioExterno": {
                    "Id": int(reserva_node.findtext("tem:UsuarioExterno/tem:Id", default="0", namespaces=ns)),
                    "Nombre": reserva_node.findtext("tem:UsuarioExterno/tem:Nombre", default="", namespaces=ns),
                    "Email": reserva_node.findtext("tem:UsuarioExterno/tem:Email", default="", namespaces=ns),
                    "Rol": reserva_node.findtext("tem:UsuarioExterno/tem:Rol", default="", namespaces=ns),
                },
            }

        logger.info(f"Relación ID={relacionId} obtenida correctamente.")
        return {"exito": True, "relacion": relacion, "mensaje": "Relación obtenida correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarPorId(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: seleccionarPorEspacio
# ======================================================
def seleccionarPorEspacio(espacioId: int) -> dict:
    """
    Obtiene todas las relaciones (RESXESP) asociadas a un espacio.

    Parámetros:
        espacioId (int): ID del espacio para obtener las relaciones.

    Retorna:
        dict:
            {
                "exito": bool,
                "relaciones": [ {...}, {...} ],
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        if not isinstance(espacioId, int) or espacioId <= 0:
            return {"error": "Debe proporcionar un 'espacioId' válido (entero mayor que 0)."}

        logger.info(f"Consultando relaciones del espacio con ID={espacioId}...")

        # ======================================================
        # Construcción del cuerpo SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarPorEspacio>
                 <tem:espacioId>{espacioId}</tem:espacioId>
              </tem:seleccionarPorEspacio>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPorEspacio",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo del XML de respuesta
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_nodes = root.findall(".//tem:seleccionarPorEspacioResult/tem:RESXESP", ns)

        if not result_nodes:
            return {"exito": False, "relaciones": [], "mensaje": "No se encontraron relaciones para el espacio indicado."}

        relaciones = []

        # ======================================================
        # Procesamiento de cada nodo RESXESP
        # ======================================================
        for node in result_nodes:
            relacion = {
                "Id": int(node.findtext("tem:Id", default="0", namespaces=ns)),
                "CostoCalculado": float(node.findtext("tem:CostoCalculado", default="0", namespaces=ns)),
                "PuntuacionUsuario": int(node.findtext("tem:PuntuacionUsuario", default="0", namespaces=ns)),
                "FechaInicio": node.findtext("tem:FechaInicio", default="", namespaces=ns),
                "FechaFin": node.findtext("tem:FechaFin", default="", namespaces=ns),
                "ReservaId": int(node.findtext("tem:ReservaId", default="0", namespaces=ns)),
                "EspacioId": int(node.findtext("tem:EspacioId", default="0", namespaces=ns)),
                "MinutosRetencion": int(node.findtext("tem:MinutosRetencion", default="0", namespaces=ns)),
                "ExpiraEn": int(node.findtext("tem:ExpiraEn", default="0", namespaces=ns)),
                "EsBloqueada": node.findtext("tem:EsBloqueada", default="false", namespaces=ns).lower() == "true",
                "TokenSesion": node.findtext("tem:TokenSesion", default="", namespaces=ns),
                "FechaRegistro": node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UltimaFechaCambio": node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                "EsActivo": node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
            }

            # ------------------------------------------------------
            # Espacio asociado
            # ------------------------------------------------------
            espacio_node = node.find("tem:Espacios", ns)
            if espacio_node is not None:
                relacion["Espacio"] = {
                    "Id": int(espacio_node.findtext("tem:Id", default="0", namespaces=ns)),
                    "Nombre": espacio_node.findtext("tem:Nombre", default="", namespaces=ns),
                    "Moneda": espacio_node.findtext("tem:Moneda", default="", namespaces=ns),
                    "CostoDiario": float(espacio_node.findtext("tem:CostoDiario", default="0", namespaces=ns)),
                    "CapacidadAdultos": int(espacio_node.findtext("tem:CapacidadAdultos", default="0", namespaces=ns)),
                    "CapacidadNinios": int(espacio_node.findtext("tem:CapacidadNinios", default="0", namespaces=ns)),
                    "DescripcionDelLugar": espacio_node.findtext("tem:DescripcionDelLugar", default="", namespaces=ns),
                    "Ubicacion": espacio_node.findtext("tem:Ubicacion", default="", namespaces=ns),
                    "Puntuacion": int(espacio_node.findtext("tem:Puntuacion", default="0", namespaces=ns)),
                    "EsActivo": espacio_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
                }

            # ------------------------------------------------------
            # Reserva asociada
            # ------------------------------------------------------
            reserva_node = node.find("tem:Reservas", ns)
            if reserva_node is not None:
                relacion["Reserva"] = {
                    "Id": int(reserva_node.findtext("tem:Id", default="0", namespaces=ns)),
                    "UsuarioId": int(reserva_node.findtext("tem:UsuarioId", default="0", namespaces=ns)),
                    "Estado": reserva_node.findtext("tem:Estado", default="", namespaces=ns),
                    "CostoFinal": float(reserva_node.findtext("tem:CostoFinal", default="0", namespaces=ns)),
                    "Comentarios": reserva_node.findtext("tem:Comentarios", default="", namespaces=ns),
                    "FechaRegistro": reserva_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                    "EsActivo": reserva_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
                }

            relaciones.append(relacion)

        logger.info(f"{len(relaciones)} relaciones encontradas para espacio {espacioId}.")
        return {"exito": True, "relaciones": relaciones, "mensaje": "Relaciones obtenidas correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarPorEspacio(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: obtenerRelacionesExpiradas
# ======================================================
def obtenerRelacionesExpiradas() -> dict:
    """
    Obtiene todas las relaciones Reserva × Espacio que han expirado.

    Retorna:
        dict:
            {
                "exito": bool,
                "relaciones": [ {...}, {...} ],
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info("Consultando relaciones Reserva×Espacio expiradas...")

        # ======================================================
        # Cuerpo SOAP (versión 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:obtenerRelacionesExpiradas/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/obtenerRelacionesExpiradas",
        }

        # ======================================================
        # Envío de solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_nodes = root.findall(".//tem:obtenerRelacionesExpiradasResult/tem:RESXESP", ns)

        if not result_nodes:
            return {
                "exito": False,
                "relaciones": [],
                "mensaje": "No se encontraron relaciones expiradas."
            }

        relaciones = []

        # ======================================================
        # Procesamiento de cada relación RESXESP
        # ======================================================
        for node in result_nodes:
            relacion = {
                "Id": int(node.findtext("tem:Id", default="0", namespaces=ns)),
                "CostoCalculado": float(node.findtext("tem:CostoCalculado", default="0", namespaces=ns)),
                "PuntuacionUsuario": int(node.findtext("tem:PuntuacionUsuario", default="0", namespaces=ns)),
                "FechaInicio": node.findtext("tem:FechaInicio", default="", namespaces=ns),
                "FechaFin": node.findtext("tem:FechaFin", default="", namespaces=ns),
                "ReservaId": int(node.findtext("tem:ReservaId", default="0", namespaces=ns)),
                "EspacioId": int(node.findtext("tem:EspacioId", default="0", namespaces=ns)),
                "MinutosRetencion": int(node.findtext("tem:MinutosRetencion", default="0", namespaces=ns)),
                "ExpiraEn": int(node.findtext("tem:ExpiraEn", default="0", namespaces=ns)),
                "EsBloqueada": node.findtext("tem:EsBloqueada", default="false", namespaces=ns).lower() == "true",
                "TokenSesion": node.findtext("tem:TokenSesion", default="", namespaces=ns),
                "FechaRegistro": node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UltimaFechaCambio": node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                "EsActivo": node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
            }

            # ------------------------------------------------------
            # Espacio relacionado
            # ------------------------------------------------------
            espacio_node = node.find("tem:Espacios", ns)
            if espacio_node is not None:
                relacion["Espacio"] = {
                    "Id": int(espacio_node.findtext("tem:Id", default="0", namespaces=ns)),
                    "Nombre": espacio_node.findtext("tem:Nombre", default="", namespaces=ns),
                    "Moneda": espacio_node.findtext("tem:Moneda", default="", namespaces=ns),
                    "CostoDiario": float(espacio_node.findtext("tem:CostoDiario", default="0", namespaces=ns)),
                    "CapacidadAdultos": int(espacio_node.findtext("tem:CapacidadAdultos", default="0", namespaces=ns)),
                    "CapacidadNinios": int(espacio_node.findtext("tem:CapacidadNinios", default="0", namespaces=ns)),
                    "DescripcionDelLugar": espacio_node.findtext("tem:DescripcionDelLugar", default="", namespaces=ns),
                    "Ubicacion": espacio_node.findtext("tem:Ubicacion", default="", namespaces=ns),
                    "Puntuacion": int(espacio_node.findtext("tem:Puntuacion", default="0", namespaces=ns)),
                    "EsActivo": espacio_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
                }

            # ------------------------------------------------------
            # Reserva relacionada
            # ------------------------------------------------------
            reserva_node = node.find("tem:Reservas", ns)
            if reserva_node is not None:
                relacion["Reserva"] = {
                    "Id": int(reserva_node.findtext("tem:Id", default="0", namespaces=ns)),
                    "UsuarioId": int(reserva_node.findtext("tem:UsuarioId", default="0", namespaces=ns)),
                    "Estado": reserva_node.findtext("tem:Estado", default="", namespaces=ns),
                    "CostoFinal": float(reserva_node.findtext("tem:CostoFinal", default="0", namespaces=ns)),
                    "Comentarios": reserva_node.findtext("tem:Comentarios", default="", namespaces=ns),
                    "FechaRegistro": reserva_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                    "EsActivo": reserva_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
                }

            relaciones.append(relacion)

        logger.info(f"{len(relaciones)} relaciones expiradas encontradas.")
        return {
            "exito": True,
            "relaciones": relaciones,
            "mensaje": f"{len(relaciones)} relaciones expiradas obtenidas correctamente."
        }

    except Exception as ex:
        logger.error(f"Error en obtenerRelacionesExpiradas(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: insertarRelacion
# ======================================================
def insertarRelacion(nuevaRelacion: dict) -> dict:
    """
    Inserta una nueva relación entre Reserva y Espacio.

    Parámetros:
        nuevaRelacion (dict): Datos de la nueva relación a insertar.

    Retorna:
        dict:
            {
                "exito": bool,
                "id_relacion": int,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info("Insertando nueva relación Reserva × Espacio...")

        # ======================================================
        # Conversión de campos
        # ======================================================
        def bool_to_str(value):
            return "true" if value else "false"

        fecha_actual = datetime.now().isoformat()

        # ======================================================
        # Construcción del XML SOAP Body
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <insertarRelacion xmlns="http://tempuri.org/">
              <nuevaRelacion>
                <Id>0</Id>
                <CostoCalculado>{nuevaRelacion.get("CostoCalculado", 0)}</CostoCalculado>
                <PuntuacionUsuario>{nuevaRelacion.get("PuntuacionUsuario", 0)}</PuntuacionUsuario>
                <FechaInicio>{nuevaRelacion.get("FechaInicio", fecha_actual)}</FechaInicio>
                <FechaFin>{nuevaRelacion.get("FechaFin", fecha_actual)}</FechaFin>
                <ReservaId>{nuevaRelacion["ReservaId"]}</ReservaId>
                <EspacioId>{nuevaRelacion["EspacioId"]}</EspacioId>
                <MinutosRetencion>{nuevaRelacion.get("MinutosRetencion", 0)}</MinutosRetencion>
                <ExpiraEn>{nuevaRelacion.get("ExpiraEn", 0)}</ExpiraEn>
                <EsBloqueada>{bool_to_str(nuevaRelacion.get("EsBloqueada", False))}</EsBloqueada>
                <TokenSesion>{nuevaRelacion.get("TokenSesion", "")}</TokenSesion>
                <FechaRegistro>{nuevaRelacion.get("FechaRegistro", fecha_actual)}</FechaRegistro>
                <UltimaFechaCambio>{nuevaRelacion.get("UltimaFechaCambio", fecha_actual)}</UltimaFechaCambio>
                <EsActivo>{bool_to_str(nuevaRelacion.get("EsActivo", True))}</EsActivo>
              </nuevaRelacion>
            </insertarRelacion>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/insertarRelacion",
        }

        # ======================================================
        # Envío de solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo manual del XML de respuesta
        # ======================================================
        if "<insertarRelacionResult>" not in response.text:
            logger.warning("No se encontró el nodo <insertarRelacionResult> en la respuesta SOAP.")
            return {"exito": False, "id_relacion": None, "mensaje": "Respuesta SOAP sin resultado válido."}

        # Extraer el valor de <insertarRelacionResult>
        start_tag = "<insertarRelacionResult>"
        end_tag = "</insertarRelacionResult>"
        id_str = response.text.split(start_tag)[1].split(end_tag)[0].strip()

        try:
            id_insertado = int(id_str)
        except ValueError:
            id_insertado = None

        if id_insertado and id_insertado > 0:
            logger.info(f"Relación insertada correctamente con ID: {id_insertado}")
            return {
                "exito": True,
                "id_relacion": id_insertado,
                "mensaje": f"Relación insertada correctamente con ID {id_insertado}."
            }
        else:
            return {
                "exito": False,
                "id_relacion": None,
                "mensaje": "La operación no devolvió un ID válido."
            }

    except Exception as ex:
        logger.error(f"Error en insertarRelacion(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: espacioDisponible
# ======================================================
def espacioDisponible(espacioId: int, fechaInicio: str, fechaFin: str) -> dict:
    """
    Verifica si un espacio está disponible entre las fechas especificadas.

    Parámetros:
        espacioId (int): ID del espacio a consultar.
        fechaInicio (str): Fecha de inicio en formato ISO (YYYY-MM-DDTHH:MM:SS).
        fechaFin (str): Fecha de fin en formato ISO (YYYY-MM-DDTHH:MM:SS).

    Retorna:
        dict:
            {
                "exito": bool,
                "disponible": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info(f"Verificando disponibilidad del espacio ID={espacioId} entre {fechaInicio} y {fechaFin}...")

        # ======================================================
        # Validaciones
        # ======================================================
        if not isinstance(espacioId, int) or espacioId <= 0:
            return {"error": "Debe proporcionar un 'espacioId' válido (entero mayor que 0)."}
        if not fechaInicio or not fechaFin:
            return {"error": "Debe proporcionar 'fechaInicio' y 'fechaFin' válidas."}

        # ======================================================
        # Cuerpo SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <espacioDisponible xmlns="http://tempuri.org/">
              <espacioId>{espacioId}</espacioId>
              <fechaInicio>{fechaInicio}</fechaInicio>
              <fechaFin>{fechaFin}</fechaFin>
            </espacioDisponible>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/espacioDisponible",
        }

        # ======================================================
        # Envío de la solicitud
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Extracción del resultado (<espacioDisponibleResult>)
        # ======================================================
        if "<espacioDisponibleResult>" not in response.text:
            logger.warning("No se encontró el nodo <espacioDisponibleResult> en la respuesta SOAP.")
            return {"exito": False, "disponible": None, "mensaje": "Respuesta inválida del servicio."}

        start_tag = "<espacioDisponibleResult>"
        end_tag = "</espacioDisponibleResult>"
        result_str = response.text.split(start_tag)[1].split(end_tag)[0].strip().lower()

        disponible = result_str == "true"

        mensaje = (
            "El espacio está disponible para las fechas indicadas."
            if disponible
            else "El espacio NO está disponible en el rango de fechas especificado."
        )

        logger.info(mensaje)

        return {"exito": True, "disponible": disponible, "mensaje": mensaje}

    except Exception as ex:
        logger.error(f"Error en espacioDisponible(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: eliminarRelacion
# ======================================================
def eliminarRelacion(id_relacion: int) -> dict:
    """
    Elimina (soft delete) una relación Reserva × Espacio.

    Parámetros:
        id_relacion (int): ID de la relación a eliminar.

    Retorna:
        dict:
            {
                "exito": bool,
                "eliminado": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info(f"Eliminando relación Reserva×Espacio con ID={id_relacion}...")

        # ======================================================
        # Validación de entrada
        # ======================================================
        if not isinstance(id_relacion, int) or id_relacion <= 0:
            return {"error": "Debe proporcionar un 'id_relacion' válido (entero mayor que 0)."}

        # ======================================================
        # Cuerpo SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <eliminarRelacion xmlns="http://tempuri.org/">
              <id>{id_relacion}</id>
            </eliminarRelacion>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/eliminarRelacion",
        }

        # ======================================================
        # Envío de la solicitud
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Extracción del resultado (<eliminarRelacionResult>)
        # ======================================================
        if "<eliminarRelacionResult>" not in response.text:
            logger.warning("No se encontró el nodo <eliminarRelacionResult> en la respuesta SOAP.")
            return {"exito": False, "eliminado": None, "mensaje": "Respuesta inválida del servicio."}

        start_tag = "<eliminarRelacionResult>"
        end_tag = "</eliminarRelacionResult>"
        result_str = response.text.split(start_tag)[1].split(end_tag)[0].strip().lower()

        eliminado = result_str == "true"

        mensaje = (
            f"Relación con ID {id_relacion} eliminada correctamente (Soft Delete)."
            if eliminado
            else f"No se pudo eliminar la relación con ID {id_relacion}."
        )

        logger.info(mensaje)

        return {"exito": True, "eliminado": eliminado, "mensaje": mensaje}

    except Exception as ex:
        logger.error(f"Error en eliminarRelacion(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: desbloquearRelacion
# ======================================================
def desbloquearRelacion(id_relacion: int) -> dict:
    """
    Desbloquea una relación Reserva × Espacio, liberando el espacio reservado.

    Parámetros:
        id_relacion (int): ID de la relación a desbloquear.

    Retorna:
        dict:
            {
                "exito": bool,
                "desbloqueado": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info(f"Desbloqueando relación Reserva×Espacio con ID={id_relacion}...")

        # ======================================================
        # Validación de entrada
        # ======================================================
        if not isinstance(id_relacion, int) or id_relacion <= 0:
            return {"error": "Debe proporcionar un 'id_relacion' válido (entero mayor que 0)."}

        # ======================================================
        # Cuerpo SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <desbloquearRelacion xmlns="http://tempuri.org/">
              <id>{id_relacion}</id>
            </desbloquearRelacion>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/desbloquearRelacion",
        }

        # ======================================================
        # Envío de la solicitud
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Extracción del resultado (<desbloquearRelacionResult>)
        # ======================================================
        if "<desbloquearRelacionResult>" not in response.text:
            logger.warning("No se encontró el nodo <desbloquearRelacionResult> en la respuesta SOAP.")
            return {"exito": False, "desbloqueado": None, "mensaje": "Respuesta inválida del servicio."}

        start_tag = "<desbloquearRelacionResult>"
        end_tag = "</desbloquearRelacionResult>"
        result_str = response.text.split(start_tag)[1].split(end_tag)[0].strip().lower()

        desbloqueado = result_str == "true"

        mensaje = (
            f"Relación con ID {id_relacion} desbloqueada correctamente (espacio liberado)."
            if desbloqueado
            else f"No se pudo desbloquear la relación con ID {id_relacion}."
        )

        logger.info(mensaje)

        return {"exito": True, "desbloqueado": desbloqueado, "mensaje": mensaje}

    except Exception as ex:
        logger.error(f"Error en desbloquearRelacion(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: calcularCosto
# ======================================================
def calcularCosto(espacioId: int, fechaInicio: str, fechaFin: str) -> dict:
    """
    Calcula el costo total de un espacio entre las fechas especificadas.

    Parámetros:
        espacioId (int): ID del espacio a consultar.
        fechaInicio (str): Fecha de inicio (ISO 8601, ej. '2025-11-01T12:00:00').
        fechaFin (str): Fecha de fin (ISO 8601, ej. '2025-11-05T12:00:00').

    Retorna:
        dict:
            {
                "exito": bool,
                "costoTotal": float,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info(f"Calculando costo del espacio ID={espacioId} entre {fechaInicio} y {fechaFin}...")

        # ======================================================
        # Validaciones básicas
        # ======================================================
        if not isinstance(espacioId, int) or espacioId <= 0:
            return {"error": "Debe proporcionar un 'espacioId' válido (entero mayor que 0)."}
        if not fechaInicio or not fechaFin:
            return {"error": "Debe proporcionar 'fechaInicio' y 'fechaFin' válidas."}

        # ======================================================
        # Cuerpo SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <calcularCosto xmlns="http://tempuri.org/">
              <espacioId>{espacioId}</espacioId>
              <fechaInicio>{fechaInicio}</fechaInicio>
              <fechaFin>{fechaFin}</fechaFin>
            </calcularCosto>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/calcularCosto",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Extracción del resultado (<calcularCostoResult>)
        # ======================================================
        if "<calcularCostoResult>" not in response.text:
            logger.warning("No se encontró el nodo <calcularCostoResult> en la respuesta SOAP.")
            return {"exito": False, "costoTotal": None, "mensaje": "Respuesta inválida del servicio."}

        start_tag = "<calcularCostoResult>"
        end_tag = "</calcularCostoResult>"
        result_str = response.text.split(start_tag)[1].split(end_tag)[0].strip()

        try:
            costo_total = float(result_str)
        except ValueError:
            costo_total = None

        if costo_total is not None:
            mensaje = f"Costo total calculado correctamente: ${costo_total:.2f}"
            logger.info(mensaje)
            return {"exito": True, "costoTotal": costo_total, "mensaje": mensaje}
        else:
            logger.warning(f"Valor no numérico en la respuesta: {result_str}")
            return {"exito": False, "costoTotal": None, "mensaje": "El valor devuelto no es numérico."}

    except Exception as ex:
        logger.error(f"Error en calcularCosto(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: actualizarRelacion
# ======================================================
def actualizarRelacion(relacion: dict) -> dict:
    """
    Actualiza una relación existente entre reserva y espacio.

    Parámetros:
        relacion (dict): Diccionario que contiene los campos requeridos por el servicio.
            Ejemplo mínimo:
            {
                "Id": 101,
                "CostoCalculado": 250.0,
                "PuntuacionUsuario": 5,
                "FechaInicio": "2025-11-01T12:00:00",
                "FechaFin": "2025-11-05T10:00:00",
                "ReservaId": 23,
                "EspacioId": 7,
                "MinutosRetencion": 30,
                "ExpiraEn": 60,
                "EsBloqueada": False,
                "TokenSesion": "ABC123XYZ",
                "FechaRegistro": "2025-10-20T15:00:00",
                "UltimaFechaCambio": "2025-10-28T12:00:00",
                "EsActivo": True
            }

    Retorna:
        dict:
            {
                "exito": bool,
                "actualizado": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info(f"Actualizando relación ID={relacion.get('Id')}...")

        # ======================================================
        # Validación de campos esenciales
        # ======================================================
        required_fields = ["Id", "CostoCalculado", "FechaInicio", "FechaFin", "ReservaId", "EspacioId"]
        for field in required_fields:
            if field not in relacion or relacion[field] is None:
                return {"error": f"Falta el campo obligatorio: {field}"}

        # ======================================================
        # Función auxiliar para booleanos
        # ======================================================
        def bool_to_str(value):
            return "true" if value else "false"

        # ======================================================
        # Cuerpo SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <actualizarRelacion xmlns="http://tempuri.org/">
              <relacionEditada>
                <Id>{relacion["Id"]}</Id>
                <CostoCalculado>{relacion.get("CostoCalculado", 0)}</CostoCalculado>
                <PuntuacionUsuario>{relacion.get("PuntuacionUsuario", 0)}</PuntuacionUsuario>
                <FechaInicio>{relacion["FechaInicio"]}</FechaInicio>
                <FechaFin>{relacion["FechaFin"]}</FechaFin>
                <ReservaId>{relacion["ReservaId"]}</ReservaId>
                <EspacioId>{relacion["EspacioId"]}</EspacioId>
                <MinutosRetencion>{relacion.get("MinutosRetencion", 0)}</MinutosRetencion>
                <ExpiraEn>{relacion.get("ExpiraEn", 0)}</ExpiraEn>
                <EsBloqueada>{bool_to_str(relacion.get("EsBloqueada", False))}</EsBloqueada>
                <TokenSesion>{relacion.get("TokenSesion", "")}</TokenSesion>
                <FechaRegistro>{relacion.get("FechaRegistro", datetime.utcnow().isoformat())}</FechaRegistro>
                <UltimaFechaCambio>{relacion.get("UltimaFechaCambio", datetime.utcnow().isoformat())}</UltimaFechaCambio>
                <EsActivo>{bool_to_str(relacion.get("EsActivo", True))}</EsActivo>
              </relacionEditada>
            </actualizarRelacion>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarRelacion",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Extracción del resultado (<actualizarRelacionResult>)
        # ======================================================
        if "<actualizarRelacionResult>" not in response.text:
            logger.warning("No se encontró el nodo <actualizarRelacionResult> en la respuesta SOAP.")
            return {"exito": False, "actualizado": None, "mensaje": "Respuesta inválida del servicio."}

        start_tag = "<actualizarRelacionResult>"
        end_tag = "</actualizarRelacionResult>"
        result_str = response.text.split(start_tag)[1].split(end_tag)[0].strip().lower()

        actualizado = result_str == "true"

        mensaje = (
            f"Relación con ID {relacion['Id']} actualizada correctamente."
            if actualizado
            else f"No se pudo actualizar la relación con ID {relacion['Id']}."
        )

        logger.info(mensaje)

        return {"exito": True, "actualizado": actualizado, "mensaje": mensaje}

    except Exception as ex:
        logger.error(f"Error en actualizarRelacion(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: actualizarPuntuacion
# ======================================================
def actualizarPuntuacion(idRelacion: int, puntuacion: int) -> dict:
    """
    Actualiza la puntuación asignada por el usuario al espacio reservado.

    Parámetros:
        idRelacion (int): ID de la relación Reserva × Espacio.
        puntuacion (int): Puntuación asignada (por ejemplo, entre 1 y 5).

    Retorna:
        dict:
            {
                "exito": bool,
                "actualizado": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info(f"Actualizando puntuación de la relación ID={idRelacion} a {puntuacion} estrellas...")

        # ======================================================
        # Validaciones básicas
        # ======================================================
        if not isinstance(idRelacion, int) or idRelacion <= 0:
            return {"error": "Debe proporcionar un 'idRelacion' válido (entero mayor que 0)."}
        if not isinstance(puntuacion, int) or not (0 <= puntuacion <= 5):
            return {"error": "La 'puntuacion' debe ser un número entero entre 0 y 5."}

        # ======================================================
        # Cuerpo SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <actualizarPuntuacion xmlns="http://tempuri.org/">
              <idRelacion>{idRelacion}</idRelacion>
              <puntuacion>{puntuacion}</puntuacion>
            </actualizarPuntuacion>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarPuntuacion",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Extracción del resultado (<actualizarPuntuacionResult>)
        # ======================================================
        if "<actualizarPuntuacionResult>" not in response.text:
            logger.warning("No se encontró el nodo <actualizarPuntuacionResult> en la respuesta SOAP.")
            return {"exito": False, "actualizado": None, "mensaje": "Respuesta inválida del servicio."}

        start_tag = "<actualizarPuntuacionResult>"
        end_tag = "</actualizarPuntuacionResult>"
        result_str = response.text.split(start_tag)[1].split(end_tag)[0].strip().lower()

        actualizado = result_str == "true"

        mensaje = (
            f"Puntuación actualizada correctamente ({puntuacion} estrellas) para relación ID {idRelacion}."
            if actualizado
            else f"No se pudo actualizar la puntuación para la relación ID {idRelacion}."
        )

        logger.info(mensaje)

        return {"exito": True, "actualizado": actualizado, "mensaje": mensaje}

    except Exception as ex:
        logger.error(f"Error en actualizarPuntuacion(): {ex}")
        return {"error": str(ex)}