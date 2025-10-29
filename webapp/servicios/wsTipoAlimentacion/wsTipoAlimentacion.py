from __future__ import annotations

import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ======================================================
# CONFIGURACIÓN GLOBAL
# ======================================================
SOAP_URL_ALIMENTACION = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionTipoAlimentacion.asmx"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ======================================================
# FUNCIÓN: actualizarTipo
# ======================================================
def actualizarTipo(tipo_editado: dict) -> dict:
    """
    Actualiza los datos de un tipo de alimentación existente usando WS_GestionTipoAlimentacion.asmx.

    Parámetros:
        tipo_editado (dict): Diccionario con los campos del tipo de alimentación a actualizar.
            Ejemplo:
            {
                "Id": 3,
                "Nombre": "Balanceado Premium",
                "FechaRegistro": "2025-01-10T08:30:00",
                "UltimaFechaCambio": "2025-10-28T15:00:00",
                "EsActivo": True
            }

    Retorna:
        dict:
            {
                "exito": bool,
                "resultado": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info(f"Actualizando tipo de alimentación ID={tipo_editado.get('Id')}")

        # ======================================================
        # Validación de datos de entrada
        # ======================================================
        required_keys = ["Id", "Nombre", "FechaRegistro", "UltimaFechaCambio", "EsActivo"]
        if not all(k in tipo_editado for k in required_keys):
            return {"error": "Faltan campos obligatorios en 'tipo_editado'."}

        # Conversión de valores booleanos
        es_activo_str = "true" if tipo_editado["EsActivo"] else "false"

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:actualizarTipo>
              <tem:tipoEditado>
                <tem:Id>{tipo_editado["Id"]}</tem:Id>
                <tem:Nombre>{tipo_editado["Nombre"]}</tem:Nombre>
                <tem:FechaRegistro>{tipo_editado["FechaRegistro"]}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{tipo_editado["UltimaFechaCambio"]}</tem:UltimaFechaCambio>
                <tem:EsActivo>{es_activo_str}</tem:EsActivo>
              </tem:tipoEditado>
            </tem:actualizarTipo>
          </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarTipo",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_ALIMENTACION, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
        result_node = root.find(".//tem:actualizarTipoResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'actualizarTipoResult' en la respuesta SOAP.")
            return {"exito": False, "resultado": False, "mensaje": "No se obtuvo respuesta del servidor."}

        resultado = result_node.text.strip().lower() == "true"

        if resultado:
            mensaje = f"Tipo de alimentación (ID={tipo_editado['Id']}) actualizado correctamente."
        else:
            mensaje = f"No se pudo actualizar el tipo de alimentación (ID={tipo_editado['Id']})."

        logger.info(mensaje)

        return {
            "exito": True,
            "resultado": resultado,
            "mensaje": mensaje
        }

    except Exception as ex:
        logger.error(f"Error en actualizarTipo(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: eliminarTipo
# ======================================================
def eliminarTipo(id_tipo: int) -> dict:
    """
    Elimina (desactiva) un tipo de alimentación mediante Soft Delete
    usando el servicio WS_GestionTipoAlimentacion.asmx.

    Parámetros:
        id_tipo (int): ID del tipo de alimentación a eliminar.

    Retorna:
        dict:
            {
                "exito": bool,
                "resultado": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Eliminando tipo de alimentación ID={id_tipo}")

        # ======================================================
        # Validación de parámetro
        # ======================================================
        if not isinstance(id_tipo, int) or id_tipo <= 0:
            return {"error": "El parámetro 'id_tipo' debe ser un número entero positivo."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:eliminarTipo>
              <tem:id>{id_tipo}</tem:id>
            </tem:eliminarTipo>
          </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/eliminarTipo",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_ALIMENTACION, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
        result_node = root.find(".//tem:eliminarTipoResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'eliminarTipoResult' en la respuesta SOAP.")
            return {"exito": False, "resultado": False, "mensaje": "No se obtuvo respuesta del servidor."}

        resultado = result_node.text.strip().lower() == "true"

        if resultado:
            mensaje = f"Tipo de alimentación (ID={id_tipo}) eliminado correctamente (Soft Delete)."
        else:
            mensaje = f"No se pudo eliminar el tipo de alimentación (ID={id_tipo})."

        logger.info(mensaje)

        return {
            "exito": True,
            "resultado": resultado,
            "mensaje": mensaje
        }

    except Exception as ex:
        logger.error(f"Error en eliminarTipo(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: insertarTipo
# ======================================================
def insertarTipo(nuevoTipo: dict) -> dict:
    """
    Inserta un nuevo tipo de alimentación usando WS_GestionTipoAlimentacion.asmx.

    Parámetros:
        nuevoTipo (dict): Diccionario con los datos del tipo a insertar.
            Ejemplo:
            {
                "Id": 0,
                "Nombre": "Forraje Natural",
                "FechaRegistro": "2025-10-28T10:00:00",
                "UltimaFechaCambio": "2025-10-28T10:00:00",
                "EsActivo": True
            }

    Retorna:
        dict:
            {
                "exito": bool,
                "nuevo_id": int | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Insertando nuevo tipo de alimentación: {nuevoTipo.get('Nombre')}")

        # ======================================================
        # Validación de datos
        # ======================================================
        requiredKeys = ["Id", "Nombre", "FechaRegistro", "UltimaFechaCambio", "EsActivo"]
        if not all(k in nuevoTipo for k in requiredKeys):
            logger.error("Faltan campos obligatorios en 'nuevoTipo'.")
            return {"error": "Faltan campos obligatorios en 'nuevoTipo'."}

        esActivoStr = "true" if nuevoTipo["EsActivo"] else "false"

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soapBody = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:insertarTipo>
              <tem:nuevoTipo>
                <tem:Id>{nuevoTipo["Id"]}</tem:Id>
                <tem:Nombre>{nuevoTipo["Nombre"]}</tem:Nombre>
                <tem:FechaRegistro>{nuevoTipo["FechaRegistro"]}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{nuevoTipo["UltimaFechaCambio"]}</tem:UltimaFechaCambio>
                <tem:EsActivo>{esActivoStr}</tem:EsActivo>
              </tem:nuevoTipo>
            </tem:insertarTipo>
          </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/insertarTipo",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_ALIMENTACION, data=soapBody.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text[:300]}")
            return {"error": f"HTTP {response.status_code}", "detalle": response.text}

        # ======================================================
        # Parseo de la respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error("Error al parsear la respuesta XML del servidor.")
            return {"error": "Respuesta XML inválida.", "detalle": str(e)}

        resultNode = root.find(".//tem:insertarTipoResult", ns)

        if resultNode is None or not resultNode.text:
            logger.warning("No se encontró el nodo 'insertarTipoResult' en la respuesta SOAP.")
            return {"exito": False, "nuevo_id": None, "mensaje": "No se obtuvo respuesta del servidor."}

        nuevoId = int(resultNode.text.strip())

        mensaje = f"✅ Tipo de alimentación '{nuevoTipo['Nombre']}' insertado correctamente con ID={nuevoId}."
        logger.info(mensaje)

        return {
            "exito": True,
            "nuevo_id": nuevoId,
            "mensaje": mensaje
        }

    except requests.exceptions.RequestException as reqErr:
        logger.error(f"Error de conexión con el servicio: {reqErr}")
        return {"error": "Error de conexión con el servicio SOAP.", "detalle": str(reqErr)}
    except Exception as ex:
        logger.exception("Error inesperado en insertarTipo().")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: reactivarTipo
# ======================================================
def reactivarTipo(id_tipo: int) -> dict:
    """
    Reactiva un tipo de alimentación previamente inactivo usando
    el servicio WS_GestionTipoAlimentacion.asmx.

    Parámetros:
        id_tipo (int): ID del tipo de alimentación a reactivar.

    Retorna:
        dict:
            {
                "exito": bool,
                "resultado": bool,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Reactivando tipo de alimentación ID={id_tipo}")

        # ======================================================
        # Validación de parámetro
        # ======================================================
        if not isinstance(id_tipo, int) or id_tipo <= 0:
            return {"error": "El parámetro 'id_tipo' debe ser un número entero positivo."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:reactivarTipo>
              <tem:id>{id_tipo}</tem:id>
            </tem:reactivarTipo>
          </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/reactivarTipo",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_ALIMENTACION, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
        result_node = root.find(".//tem:reactivarTipoResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'reactivarTipoResult' en la respuesta SOAP.")
            return {"exito": False, "resultado": False, "mensaje": "No se obtuvo respuesta del servidor."}

        resultado = result_node.text.strip().lower() == "true"

        if resultado:
            mensaje = f"Tipo de alimentación (ID={id_tipo}) reactivado correctamente."
        else:
            mensaje = f"No se pudo reactivar el tipo de alimentación (ID={id_tipo})."

        logger.info(mensaje)

        return {
            "exito": True,
            "resultado": resultado,
            "mensaje": mensaje
        }

    except Exception as ex:
        logger.error(f"Error en reactivarTipo(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: seleccionarInactivos
# ======================================================
def seleccionarInactivos() -> list:
    """
    Llama al método SOAP 'seleccionarInactivos' del servicio WS_GestionTipoAlimentacion.
    Retorna una lista con los tipos de alimentación inactivos.

    Retorna:
        list[dict]: Lista con los tipos de alimentación inactivos.
    """
    try:
        logger.info("Ejecutando solicitud SOAP: seleccionarInactivos()")

        # ======================================================
        # Encabezados y cuerpo SOAP (SOAP 1.1)
        # ======================================================
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarInactivos"
        }

        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <seleccionarInactivos xmlns="http://tempuri.org/" />
          </soap:Body>
        </soap:Envelope>"""

        # ======================================================
        # Enviar solicitud al servicio SOAP
        # ======================================================
        response = requests.post(SOAP_URL_ALIMENTACION, data=soap_body.encode("utf-8"), headers=headers, timeout=15)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text[:200]}")
            return []

        # ======================================================
        # Parsear respuesta XML
        # ======================================================
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            't': 'http://tempuri.org/'
        }

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error("Error al parsear la respuesta XML del servidor.")
            return []

        tipoAlimentacionList = []

        for tipo in root.findall('.//t:TipoAlimentacion', ns):
            tipoData = {
                'id': tipo.find('t:Id', ns).text if tipo.find('t:Id', ns) is not None else None,
                'nombre': tipo.find('t:Nombre', ns).text if tipo.find('t:Nombre', ns) is not None else None,
                'fechaRegistro': tipo.find('t:FechaRegistro', ns).text if tipo.find('t:FechaRegistro', ns) is not None else None,
                'ultimaFechaCambio': tipo.find('t:UltimaFechaCambio', ns).text if tipo.find('t:UltimaFechaCambio', ns) is not None else None,
                'esActivo': tipo.find('t:EsActivo', ns).text if tipo.find('t:EsActivo', ns) is not None else None
            }
            tipoAlimentacionList.append(tipoData)

        logger.info(f"Consulta completada: {len(tipoAlimentacionList)} tipos de alimentación inactivos encontrados.")
        return tipoAlimentacionList

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servicio: {e}")
        return []
    except Exception as e:
        logger.exception(f"Error inesperado en seleccionarInactivos(): {e}")
        return []

# ======================================================
# FUNCIÓN: seleccionarPorId
# ======================================================
def seleccionarPorId(id: int) -> dict | None:
    """
    Llama al método SOAP 'seleccionarPorId' del servicio WS_GestionTipoAlimentacion.

    Parámetro:
        id (int): Identificador del tipo de alimentación.

    Retorna:
        dict con los datos del tipo de alimentación o None si no se encuentra.
    """
    try:
        logger.info(f"Ejecutando solicitud SOAP: seleccionarPorId(id={id})")

        # ======================================================
        # Encabezados y cuerpo SOAP (SOAP 1.1)
        # ======================================================
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPorId"
        }

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <seleccionarPorId xmlns="http://tempuri.org/">
              <id>{id}</id>
            </seleccionarPorId>
          </soap:Body>
        </soap:Envelope>"""

        # ======================================================
        # Enviar solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_ALIMENTACION, data=soap_body.encode("utf-8"), headers=headers, timeout=15)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text[:300]}")
            return None

        # ======================================================
        # Parsear XML de respuesta
        # ======================================================
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            't': 'http://tempuri.org/'
        }

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error(f"Error al parsear la respuesta XML: {e}")
            return None

        result = root.find('.//t:seleccionarPorIdResult', ns)

        if result is None:
            logger.warning(f"No se encontró información para el ID {id}.")
            return None

        tipoAlimentacion = {
            'id': result.find('t:Id', ns).text if result.find('t:Id', ns) is not None else None,
            'nombre': result.find('t:Nombre', ns).text if result.find('t:Nombre', ns) is not None else None,
            'fechaRegistro': result.find('t:FechaRegistro', ns).text if result.find('t:FechaRegistro', ns) is not None else None,
            'ultimaFechaCambio': result.find('t:UltimaFechaCambio', ns).text if result.find('t:UltimaFechaCambio', ns) is not None else None,
            'esActivo': result.find('t:EsActivo', ns).text if result.find('t:EsActivo', ns) is not None else None
        }

        logger.info(f"Tipo de alimentación obtenido correctamente: {tipoAlimentacion['nombre']} (ID={tipoAlimentacion['id']})")
        return tipoAlimentacion

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servicio SOAP: {e}")
        return None
    except Exception as e:
        logger.exception(f"Error inesperado en seleccionarPorId(): {e}")
        return None


# ======================================================
# FUNCIÓN: seleccionarPorNombre
# ======================================================
def seleccionarPorNombre(nombre: str) -> dict | None:
    """
    Llama al método SOAP 'seleccionarPorNombre' del servicio WS_GestionTipoAlimentacion.

    Parámetro:
        nombre (str): Nombre del tipo de alimentación a buscar.

    Retorna:
        dict con los datos del tipo de alimentación o None si no se encuentra.
    """
    try:
        logger.info(f"Ejecutando solicitud SOAP: seleccionarPorNombre(nombre='{nombre}')")

        # ======================================================
        # Encabezados y cuerpo SOAP (SOAP 1.1)
        # ======================================================
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPorNombre"
        }

        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <seleccionarPorNombre xmlns="http://tempuri.org/">
              <nombre>{nombre}</nombre>
            </seleccionarPorNombre>
          </soap:Body>
        </soap:Envelope>"""

        # ======================================================
        # Enviar solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_ALIMENTACION, data=soap_body.encode("utf-8"), headers=headers, timeout=15)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text[:300]}")
            return None

        # ======================================================
        # Parsear XML de respuesta
        # ======================================================
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            't': 'http://tempuri.org/'
        }

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error(f"Error al parsear la respuesta XML: {e}")
            return None

        result = root.find('.//t:seleccionarPorNombreResult', ns)

        if result is None:
            logger.warning(f"No se encontró información para el nombre '{nombre}'.")
            return None

        tipoAlimentacion = {
            'id': result.find('t:Id', ns).text if result.find('t:Id', ns) is not None else None,
            'nombre': result.find('t:Nombre', ns).text if result.find('t:Nombre', ns) is not None else None,
            'fechaRegistro': result.find('t:FechaRegistro', ns).text if result.find('t:FechaRegistro', ns) is not None else None,
            'ultimaFechaCambio': result.find('t:UltimaFechaCambio', ns).text if result.find('t:UltimaFechaCambio', ns) is not None else None,
            'esActivo': result.find('t:EsActivo', ns).text if result.find('t:EsActivo', ns) is not None else None
        }

        logger.info(f"Tipo de alimentación encontrado: {tipoAlimentacion['nombre']} (ID={tipoAlimentacion['id']})")
        return tipoAlimentacion

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servicio SOAP: {e}")
        return None
    except Exception as e:
        logger.exception(f"Error inesperado en seleccionarPorNombre(): {e}")
        return None
