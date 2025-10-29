import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ======================================================
# CONFIGURACIÓN GLOBAL
# ======================================================
SOAP_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionAmenidades.asmx"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ======================================================
# FUNCIÓN: actualizarAmenidad
# ======================================================
def actualizarAmenidad(amenidad: dict) -> dict:
    """
    Actualiza los datos de una amenidad existente en el sistema mediante WS_GestionAmenidades.

    Parámetros:
        amenidad (dict): Datos de la amenidad a actualizar. Ejemplo:
            {
                "Id": 3,
                "Nombre": "Piscina Climatizada",
                "FechaRegistro": "2023-05-10T12:00:00",
                "UltimaFechaCambio": "2025-10-28T09:30:00",
                "EsActivo": True
            }

    Retorna:
        dict:
            {
                "exito": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Actualizando amenidad ID={amenidad.get('Id')} en WS_GestionAmenidades")

        # ======================================================
        # Validar entrada
        # ======================================================
        if "Id" not in amenidad or "Nombre" not in amenidad:
            return {"error": "Faltan campos obligatorios: 'Id' y 'Nombre'."}

        # Asegurar formato ISO de fechas
        fecha_registro = amenidad.get("FechaRegistro") or datetime.now().isoformat()
        ultima_fecha = amenidad.get("UltimaFechaCambio") or datetime.now().isoformat()
        es_activo = str(amenidad.get("EsActivo", True)).lower()

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:actualizarAmenidad>
              <tem:amenidadEditada>
                <tem:Id>{amenidad["Id"]}</tem:Id>
                <tem:Nombre>{amenidad["Nombre"]}</tem:Nombre>
                <tem:FechaRegistro>{fecha_registro}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{ultima_fecha}</tem:UltimaFechaCambio>
                <tem:EsActivo>{es_activo}</tem:EsActivo>
              </tem:amenidadEditada>
            </tem:actualizarAmenidad>
          </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarAmenidad",
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
        result_node = root.find(".//tem:actualizarAmenidadResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'actualizarAmenidadResult' en la respuesta SOAP.")
            return {"exito": False, "mensaje": "No se pudo determinar el resultado de la actualización."}

        exito = result_node.text.strip().lower() == "true"

        if exito:
            logger.info(f"Amenidad ID={amenidad['Id']} actualizada correctamente.")
            return {"exito": True, "mensaje": f"Amenidad ID={amenidad['Id']} actualizada correctamente."}
        else:
            logger.warning(f"No se pudo actualizar la amenidad ID={amenidad['Id']}.")
            return {"exito": False, "mensaje": "No se realizó la actualización (posiblemente no existe la amenidad)."}

    except Exception as ex:
        logger.error(f"Error en actualizarAmenidad(): {ex}")
        return {"error": str(ex)}



# ======================================================
# FUNCIÓN: eliminarAmenidad
# ======================================================
def eliminarAmenidad(amenidad_id: int) -> dict:
    """
    Elimina (desactiva) una amenidad mediante soft delete en WS_GestionAmenidades.asmx.

    Parámetros:
        amenidad_id (int): ID de la amenidad a eliminar.

    Retorna:
        dict:
            {
                "exito": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Eliminando (soft delete) amenidad con ID={amenidad_id} en WS_GestionAmenidades")

        # ======================================================
        # Validación de entrada
        # ======================================================
        if not amenidad_id or amenidad_id <= 0:
            return {"error": "El parámetro 'amenidad_id' debe ser un entero válido mayor que 0."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:eliminarAmenidad>
                 <tem:id>{amenidad_id}</tem:id>
              </tem:eliminarAmenidad>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/eliminarAmenidad",
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
        result_node = root.find(".//tem:eliminarAmenidadResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'eliminarAmenidadResult' en la respuesta SOAP.")
            return {"exito": False, "mensaje": "No se pudo determinar el resultado de la eliminación."}

        exito = result_node.text.strip().lower() == "true"

        if exito:
            logger.info(f"Amenidad ID={amenidad_id} eliminada (desactivada) correctamente.")
            return {"exito": True, "mensaje": f"Amenidad ID={amenidad_id} eliminada correctamente."}
        else:
            logger.warning(f"No se pudo eliminar la amenidad ID={amenidad_id}.")
            return {"exito": False, "mensaje": f"No se pudo eliminar la amenidad ID={amenidad_id} (posiblemente no existe o ya está inactiva)."}

    except Exception as ex:
        logger.error(f"Error en eliminarAmenidad(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: insertarAmenidad
# ======================================================
def insertarAmenidad(amenidad: dict) -> dict:
    """
    Inserta una nueva amenidad en el sistema mediante WS_GestionAmenidades.asmx.

    Parámetros:
        amenidad (dict): Datos de la amenidad a insertar. Ejemplo:
            {
                "Id": 0,  # Puede ser 0 o no incluirse; el servidor lo asigna automáticamente
                "Nombre": "Jacuzzi Exterior",
                "FechaRegistro": "2025-10-28T10:00:00",
                "UltimaFechaCambio": "2025-10-28T10:00:00",
                "EsActivo": True
            }

    Retorna:
        dict:
            {
                "exito": bool,
                "id_generado": int | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Insertando nueva amenidad '{amenidad.get('Nombre')}' en WS_GestionAmenidades")

        # ======================================================
        # Validación de campos obligatorios
        # ======================================================
        if "Nombre" not in amenidad or not amenidad["Nombre"]:
            return {"error": "El campo 'Nombre' es obligatorio para insertar una amenidad."}

        # Fechas por defecto si no se proporcionan
        fecha_actual = datetime.now().isoformat()
        fecha_registro = amenidad.get("FechaRegistro", fecha_actual)
        ultima_fecha_cambio = amenidad.get("UltimaFechaCambio", fecha_actual)
        es_activo = str(amenidad.get("EsActivo", True)).lower()
        amenidad_id = amenidad.get("Id", 0)

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:insertarAmenidad>
              <tem:nuevaAmenidad>
                <tem:Id>{amenidad_id}</tem:Id>
                <tem:Nombre>{amenidad["Nombre"]}</tem:Nombre>
                <tem:FechaRegistro>{fecha_registro}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{ultima_fecha_cambio}</tem:UltimaFechaCambio>
                <tem:EsActivo>{es_activo}</tem:EsActivo>
              </tem:nuevaAmenidad>
            </tem:insertarAmenidad>
          </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/insertarAmenidad",
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
        result_node = root.find(".//tem:insertarAmenidadResult", ns)

        if result_node is None or not result_node.text.strip():
            logger.warning("No se encontró el nodo 'insertarAmenidadResult' en la respuesta SOAP.")
            return {"exito": False, "id_generado": None, "mensaje": "No se obtuvo un ID válido en la respuesta."}

        try:
            id_generado = int(result_node.text.strip())
        except ValueError:
            id_generado = None

        if id_generado and id_generado > 0:
            logger.info(f"Amenidad '{amenidad['Nombre']}' insertada correctamente con ID={id_generado}.")
            return {"exito": True, "id_generado": id_generado, "mensaje": f"Amenidad creada con ID={id_generado}."}
        else:
            logger.warning(f"La respuesta SOAP no devolvió un ID válido: {result_node.text.strip()}")
            return {"exito": False, "id_generado": None, "mensaje": "No se pudo crear la amenidad."}

    except Exception as ex:
        logger.error(f"Error en insertarAmenidad(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: seleccionarAmenidadPorId
# ======================================================
def seleccionarAmenidadPorId(amenidad_id: int) -> dict:
    """
    Obtiene una amenidad específica por su ID desde el servicio WS_GestionAmenidades.asmx.

    Parámetros:
        amenidad_id (int): ID de la amenidad a consultar.

    Retorna:
        dict:
            {
                "exito": bool,
                "amenidad": {
                    "Id": int,
                    "Nombre": str,
                    "FechaRegistro": str,
                    "UltimaFechaCambio": str,
                    "EsActivo": bool
                }
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Consultando amenidad con ID={amenidad_id} en WS_GestionAmenidades")

        # ======================================================
        # Validar parámetro
        # ======================================================
        if not amenidad_id or amenidad_id <= 0:
            return {"error": "El parámetro 'amenidad_id' debe ser un entero válido mayor que 0."}

        # ======================================================
        # Construir envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarAmenidadPorId>
                 <tem:id>{amenidad_id}</tem:id>
              </tem:seleccionarAmenidadPorId>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarAmenidadPorId",
        }

        # ======================================================
        # Enviar solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parsear respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:seleccionarAmenidadPorIdResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarAmenidadPorIdResult' en la respuesta SOAP.")
            return {"exito": False, "mensaje": "No se encontró la amenidad solicitada."}

        # Extraer los campos esperados
        amenidad = {
            "Id": int(result_node.findtext("tem:Id", default="0", namespaces=ns)),
            "Nombre": result_node.findtext("tem:Nombre", default="", namespaces=ns),
            "FechaRegistro": result_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
            "UltimaFechaCambio": result_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
            "EsActivo": result_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
        }

        if not amenidad["Id"]:
            logger.warning(f"No se encontró una amenidad válida para el ID={amenidad_id}.")
            return {"exito": False, "mensaje": "No se encontró la amenidad."}

        logger.info(f"Amenidad ID={amenidad_id} obtenida correctamente.")
        return {"exito": True, "amenidad": amenidad}

    except Exception as ex:
        logger.error(f"Error en seleccionarAmenidadPorId(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: seleccionarAmenidades
# ======================================================
def seleccionarAmenidades() -> dict:
    """
    Obtiene todas las amenidades activas desde WS_GestionAmenidades.asmx.

    Retorna:
        dict:
            {
                "exito": bool,
                "amenidades": [
                    {
                        "Id": int,
                        "Nombre": str,
                        "FechaRegistro": str,
                        "UltimaFechaCambio": str,
                        "EsActivo": bool
                    }, ...
                ],
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info("Consultando todas las amenidades activas en WS_GestionAmenidades")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarAmenidades/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarAmenidades",
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
        result_node = root.find(".//tem:seleccionarAmenidadesResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarAmenidadesResult' en la respuesta SOAP.")
            return {"exito": False, "amenidades": [], "mensaje": "No se encontraron amenidades activas."}

        # ======================================================
        # Recorrer las etiquetas <Amenidades> y construir la lista
        # ======================================================
        amenidades = []
        for amenidad_node in result_node.findall("tem:Amenidades", ns):
            amenidad = {
                "Id": int(amenidad_node.findtext("tem:Id", default="0", namespaces=ns)),
                "Nombre": amenidad_node.findtext("tem:Nombre", default="", namespaces=ns),
                "FechaRegistro": amenidad_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UltimaFechaCambio": amenidad_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                "EsActivo": amenidad_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
            }
            if amenidad["Id"] > 0:
                amenidades.append(amenidad)

        if not amenidades:
            logger.info("No se encontraron amenidades activas en el sistema.")
            return {"exito": True, "amenidades": [], "mensaje": "No existen amenidades activas."}

        logger.info(f"Se obtuvieron {len(amenidades)} amenidades activas correctamente.")
        return {"exito": True, "amenidades": amenidades, "mensaje": "Amenidades obtenidas correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarAmenidades(): {ex}")
        return {"error": str(ex)}