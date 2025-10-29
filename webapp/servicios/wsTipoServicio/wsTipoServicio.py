import logging
import requests
import xml.etree.ElementTree as ET

# ======================================================
# CONFIGURACIÓN GLOBAL
# ======================================================
SOAP_URL_TIPO = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionTipoServicio.asmx"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ======================================================
# FUNCIÓN: actualizarTipo
# ======================================================
def actualizarTipo(tipo: dict) -> dict:
    """
    Actualiza los datos de un tipo de servicio existente usando WS_GestionTipoServicio.asmx.

    Parámetros:
        tipo (dict): Objeto con los campos del tipo a actualizar:
            {
                "Id": int,
                "Nombre": str,
                "FechaRegistro": str (ISO 8601),
                "UltimaFechaCambio": str (ISO 8601),
                "EsActivo": bool
            }

    Retorna:
        dict:
            {
                "exito": bool,
                "resultado": bool | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Actualizando tipo de servicio con ID={tipo.get('Id')}")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        campos_requeridos = ["Id", "Nombre", "FechaRegistro", "UltimaFechaCambio", "EsActivo"]
        faltantes = [c for c in campos_requeridos if c not in tipo]
        if faltantes:
            return {"error": f"Faltan campos requeridos: {', '.join(faltantes)}"}

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
                    <tem:Id>{tipo['Id']}</tem:Id>
                    <tem:Nombre>{tipo['Nombre']}</tem:Nombre>
                    <tem:FechaRegistro>{tipo['FechaRegistro']}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{tipo['UltimaFechaCambio']}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{"true" if tipo["EsActivo"] else "false"}</tem:EsActivo>
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
        response = requests.post(SOAP_URL_TIPO, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
            return {"exito": False, "resultado": None, "mensaje": "No se recibió confirmación del servidor."}

        # Convertir el resultado a booleano
        resultado = result_node.text.strip().lower() == "true"

        logger.info(f"Resultado de actualización: {resultado}")
        return {
            "exito": True,
            "resultado": resultado,
            "mensaje": "Tipo de servicio actualizado correctamente." if resultado else "No se pudo actualizar el tipo de servicio."
        }

    except Exception as ex:
        logger.error(f"Error en actualizarTipo(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: eliminarTipo
# ======================================================
def eliminarTipo(id_tipo: int) -> dict:
    """
    Elimina (desactiva) un tipo de servicio mediante Soft Delete usando WS_GestionTipoServicio.asmx.

    Parámetros:
        id_tipo (int): Identificador del tipo de servicio a eliminar.

    Retorna:
        dict:
            {
                "exito": bool,
                "resultado": bool | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Eliminando (soft delete) tipo de servicio con ID={id_tipo}")

        # ======================================================
        # Validación de parámetros
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
        response = requests.post(SOAP_URL_TIPO, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
            return {"exito": False, "resultado": None, "mensaje": "No se recibió confirmación del servidor."}

        # Convertir el resultado a booleano
        resultado = result_node.text.strip().lower() == "true"

        logger.info(f"Resultado de eliminación: {resultado}")
        return {
            "exito": True,
            "resultado": resultado,
            "mensaje": "Tipo de servicio eliminado correctamente." if resultado else "No se pudo eliminar el tipo de servicio."
        }

    except Exception as ex:
        logger.error(f"Error en eliminarTipo(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: insertarTipo
# ======================================================
def insertarTipo(tipo: dict) -> dict:
    """
    Inserta un nuevo tipo de servicio en el sistema mediante WS_GestionTipoServicio.asmx.

    Parámetros:
        tipo (dict): Objeto con los campos del tipo a insertar:
            {
                "Id": int,
                "Nombre": str,
                "FechaRegistro": str (ISO 8601),
                "UltimaFechaCambio": str (ISO 8601),
                "EsActivo": bool
            }

    Retorna:
        dict:
            {
                "exito": bool,
                "id_insertado": int | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Insertando nuevo tipo de servicio: {tipo.get('Nombre')}")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        campos_requeridos = ["Id", "Nombre", "FechaRegistro", "UltimaFechaCambio", "EsActivo"]
        faltantes = [c for c in campos_requeridos if c not in tipo]
        if faltantes:
            return {"error": f"Faltan campos requeridos: {', '.join(faltantes)}"}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:insertarTipo>
                 <tem:nuevoTipo>
                    <tem:Id>{tipo['Id']}</tem:Id>
                    <tem:Nombre>{tipo['Nombre']}</tem:Nombre>
                    <tem:FechaRegistro>{tipo['FechaRegistro']}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{tipo['UltimaFechaCambio']}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{"true" if tipo["EsActivo"] else "false"}</tem:EsActivo>
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
        response = requests.post(SOAP_URL_TIPO, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
        result_node = root.find(".//tem:insertarTipoResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'insertarTipoResult' en la respuesta SOAP.")
            return {"exito": False, "id_insertado": None, "mensaje": "No se recibió confirmación del servidor."}

        # Convertir el resultado a entero (ID insertado)
        try:
            id_insertado = int(result_node.text.strip())
        except (TypeError, ValueError):
            id_insertado = None

        logger.info(f"Resultado de inserción: ID={id_insertado}")
        return {
            "exito": True,
            "id_insertado": id_insertado,
            "mensaje": "Tipo de servicio insertado correctamente." if id_insertado else "No se pudo insertar el tipo de servicio."
        }

    except Exception as ex:
        logger.error(f"Error en insertarTipo(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: reactivarTipo
# ======================================================
def reactivarTipo(id_tipo: int) -> dict:
    """
    Reactiva un tipo de servicio previamente inactivo mediante WS_GestionTipoServicio.asmx.

    Parámetros:
        id_tipo (int): Identificador del tipo de servicio a reactivar.

    Retorna:
        dict:
            {
                "exito": bool,
                "resultado": bool | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Reactivando tipo de servicio con ID={id_tipo}")

        # ======================================================
        # Validación de parámetros
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
        response = requests.post(SOAP_URL_TIPO, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
            return {"exito": False, "resultado": None, "mensaje": "No se recibió confirmación del servidor."}

        # Convertir el resultado a booleano
        resultado = result_node.text.strip().lower() == "true"

        logger.info(f"Resultado de reactivación: {resultado}")
        return {
            "exito": True,
            "resultado": resultado,
            "mensaje": "Tipo de servicio reactivado correctamente." if resultado else "No se pudo reactivar el tipo de servicio."
        }

    except Exception as ex:
        logger.error(f"Error en reactivarTipo(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: seleccionarInactivos
# ======================================================
def seleccionarInactivos() -> dict:
    """
    Obtiene todos los tipos de servicio inactivos usando WS_GestionTipoServicio.asmx.

    Retorna:
        dict:
            {
                "exito": bool,
                "tipos": list[dict] | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info("Obteniendo lista de tipos de servicio inactivos...")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarInactivos/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarInactivos",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_TIPO, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
        result_node = root.find(".//tem:seleccionarInactivosResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarInactivosResult' en la respuesta SOAP.")
            return {"exito": False, "tipos": None, "mensaje": "No se recibió confirmación del servidor."}

        # ======================================================
        # Extracción de los elementos <TipoServicio>
        # ======================================================
        tipos = []
        for tipo_node in result_node.findall(".//tem:TipoServicio", ns):
            tipo = {
                "Id": int(tipo_node.findtext("tem:Id", default="0", namespaces=ns)),
                "Nombre": tipo_node.findtext("tem:Nombre", default="", namespaces=ns),
                "FechaRegistro": tipo_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UltimaFechaCambio": tipo_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                "EsActivo": tipo_node.findtext("tem:EsActivo", default="false", namespaces=ns).strip().lower() == "true",
            }
            tipos.append(tipo)

        logger.info(f"Se encontraron {len(tipos)} tipos de servicio inactivos.")

        return {
            "exito": True,
            "tipos": tipos,
            "mensaje": f"Se encontraron {len(tipos)} tipos de servicio inactivos."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarInactivos(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: seleccionarPorId
# ======================================================
def seleccionarPorId(id_tipo: int) -> dict:
    """
    Obtiene un tipo de servicio por su ID usando WS_GestionTipoServicio.asmx.

    Parámetros:
        id_tipo (int): Identificador del tipo de servicio a consultar.

    Retorna:
        dict:
            {
                "exito": bool,
                "tipo": dict | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Consultando tipo de servicio con ID={id_tipo}")

        # ======================================================
        # Validación de parámetros
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
              <tem:seleccionarPorId>
                 <tem:id>{id_tipo}</tem:id>
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
        response = requests.post(SOAP_URL_TIPO, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
            return {"exito": False, "tipo": None, "mensaje": "No se encontró información para el ID especificado."}

        # ======================================================
        # Extracción de los datos del tipo de servicio
        # ======================================================
        tipo = {
            "Id": int(result_node.findtext("tem:Id", default="0", namespaces=ns)),
            "Nombre": result_node.findtext("tem:Nombre", default="", namespaces=ns),
            "FechaRegistro": result_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
            "UltimaFechaCambio": result_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
            "EsActivo": result_node.findtext("tem:EsActivo", default="false", namespaces=ns).strip().lower() == "true",
        }

        logger.info(f"Tipo de servicio encontrado: {tipo['Nombre']} (Activo: {tipo['EsActivo']})")

        return {
            "exito": True,
            "tipo": tipo,
            "mensaje": f"Tipo de servicio obtenido correctamente (ID={id_tipo})."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarPorId(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: seleccionarPorNombre
# ======================================================
def seleccionarPorNombre(nombre: str) -> dict:
    """
    Busca un tipo de servicio por su nombre usando WS_GestionTipoServicio.asmx.

    Parámetros:
        nombre (str): Nombre del tipo de servicio a buscar.

    Retorna:
        dict:
            {
                "exito": bool,
                "tipo": dict | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Buscando tipo de servicio con nombre='{nombre}'")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        if not isinstance(nombre, str) or not nombre.strip():
            return {"error": "El parámetro 'nombre' debe ser una cadena de texto no vacía."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarPorNombre>
                 <tem:nombre>{nombre}</tem:nombre>
              </tem:seleccionarPorNombre>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPorNombre",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_TIPO, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
        result_node = root.find(".//tem:seleccionarPorNombreResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarPorNombreResult' en la respuesta SOAP.")
            return {"exito": False, "tipo": None, "mensaje": f"No se encontró ningún tipo de servicio con nombre '{nombre}'."}

        # ======================================================
        # Extracción de los datos del tipo de servicio
        # ======================================================
        tipo = {
            "Id": int(result_node.findtext("tem:Id", default="0", namespaces=ns)),
            "Nombre": result_node.findtext("tem:Nombre", default="", namespaces=ns),
            "FechaRegistro": result_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
            "UltimaFechaCambio": result_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
            "EsActivo": result_node.findtext("tem:EsActivo", default="false", namespaces=ns).strip().lower() == "true",
        }

        logger.info(f"Tipo de servicio encontrado: {tipo['Nombre']} (Activo: {tipo['EsActivo']})")

        return {
            "exito": True,
            "tipo": tipo,
            "mensaje": f"Tipo de servicio '{nombre}' obtenido correctamente."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarPorNombre(): {ex}")
        return {"error": str(ex)}



# ======================================================
# FUNCIÓN: seleccionarTipos
# ======================================================
def seleccionarTipos() -> dict:
    """
    Obtiene todos los tipos de servicio activos usando WS_GestionTipoServicio.asmx.

    Retorna:
        dict:
            {
                "exito": bool,
                "tipos": list[dict] | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info("Consultando lista de tipos de servicio activos...")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarTipos/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarTipos",
        }

        # ======================================================
        # Envío de la solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL_TIPO, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

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
        result_node = root.find(".//tem:seleccionarTiposResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarTiposResult' en la respuesta SOAP.")
            return {"exito": False, "tipos": None, "mensaje": "No se encontraron tipos de servicio activos."}

        # ======================================================
        # Extracción de los elementos <TipoServicio>
        # ======================================================
        tipos = []
        for tipo_node in result_node.findall(".//tem:TipoServicio", ns):
            tipo = {
                "Id": int(tipo_node.findtext("tem:Id", default="0", namespaces=ns)),
                "Nombre": tipo_node.findtext("tem:Nombre", default="", namespaces=ns),
                "FechaRegistro": tipo_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UltimaFechaCambio": tipo_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                "EsActivo": tipo_node.findtext("tem:EsActivo", default="false", namespaces=ns).strip().lower() == "true",
            }
            tipos.append(tipo)

        logger.info(f"Se encontraron {len(tipos)} tipos de servicio activos.")

        return {
            "exito": True,
            "tipos": tipos,
            "mensaje": f"Se encontraron {len(tipos)} tipos de servicio activos."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarTipos(): {ex}")
        return {"error": str(ex)}