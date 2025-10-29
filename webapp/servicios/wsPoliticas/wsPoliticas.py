import logging
import requests
import xml.etree.ElementTree as ET

# ======================================================
# CONFIGURACIÓN GLOBAL
# ======================================================
SOAP_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionPoliticas.asmx"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ======================================================
# FUNCIÓN: actualizarPolitica
# ======================================================
def actualizarPolitica(politica: dict) -> dict:
    """
    Actualiza los datos de una política existente usando WS_GestionPoliticas.asmx.

    Parámetros:
        politica (dict): Objeto con los campos de la política a actualizar:
            {
                "Id": int,
                "DescripcionPolitica": str,
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
        logger.info(f"Actualizando política con ID={politica.get('Id')}")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        campos_requeridos = ["Id", "DescripcionPolitica", "FechaRegistro", "UltimaFechaCambio", "EsActivo"]
        faltantes = [c for c in campos_requeridos if c not in politica]
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
              <tem:actualizarPolitica>
                 <tem:politicaEditada>
                    <tem:Id>{politica['Id']}</tem:Id>
                    <tem:DescripcionPolitica>{politica['DescripcionPolitica']}</tem:DescripcionPolitica>
                    <tem:FechaRegistro>{politica['FechaRegistro']}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{politica['UltimaFechaCambio']}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{"true" if politica["EsActivo"] else "false"}</tem:EsActivo>
                 </tem:politicaEditada>
              </tem:actualizarPolitica>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarPolitica",
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
        result_node = root.find(".//tem:actualizarPoliticaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'actualizarPoliticaResult' en la respuesta SOAP.")
            return {"exito": False, "resultado": None, "mensaje": "No se recibió confirmación del servidor."}

        # Convertir el resultado a booleano
        resultado = result_node.text.strip().lower() == "true"

        logger.info(f"Resultado de actualización: {resultado}")
        return {
            "exito": True,
            "resultado": resultado,
            "mensaje": "Política actualizada correctamente." if resultado else "No se pudo actualizar la política."
        }

    except Exception as ex:
        logger.error(f"Error en actualizarPolitica(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: buscarPoliticasPorTexto
# ======================================================
def buscarPoliticasPorTexto(texto: str) -> dict:
    """
    Busca políticas activas que contengan el texto especificado.

    Parámetros:
        texto (str): Texto a buscar dentro de las descripciones de políticas.

    Retorna:
        dict:
            {
                "exito": bool,
                "politicas": list[dict] | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Buscando políticas que contienen el texto: '{texto}'")

        if not texto or not isinstance(texto, str):
            return {"error": "El parámetro 'texto' es requerido y debe ser una cadena de texto."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:buscarPoliticasPorTexto>
                 <tem:texto>{texto}</tem:texto>
              </tem:buscarPoliticasPorTexto>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/buscarPoliticasPorTexto",
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
        politicas_nodes = root.findall(".//tem:buscarPoliticasPorTextoResult/tem:Politicas", ns)

        if not politicas_nodes:
            logger.warning("No se encontraron políticas que coincidan con el texto.")
            return {"exito": True, "politicas": [], "mensaje": "No se encontraron políticas."}

        # ======================================================
        # Extracción de los datos de cada política
        # ======================================================
        politicas = []
        for node in politicas_nodes:
            politica = {
                "Id": int(node.findtext("tem:Id", default="0", namespaces=ns)),
                "DescripcionPolitica": node.findtext("tem:DescripcionPolitica", default="", namespaces=ns),
                "FechaRegistro": node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UltimaFechaCambio": node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                "EsActivo": node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
            }
            politicas.append(politica)

        logger.info(f"Se encontraron {len(politicas)} políticas que coinciden con el texto '{texto}'.")
        return {
            "exito": True,
            "politicas": politicas,
            "mensaje": f"Se encontraron {len(politicas)} políticas."
        }

    except Exception as ex:
        logger.error(f"Error en buscarPoliticasPorTexto(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: eliminarPolitica
# ======================================================
def eliminarPolitica(id_politica: int) -> dict:
    """
    Elimina (desactiva) una política mediante Soft Delete usando WS_GestionPoliticas.asmx.

    Parámetros:
        id_politica (int): Identificador de la política a eliminar.

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
        logger.info(f"Eliminando (soft delete) la política con ID={id_politica}")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        if not isinstance(id_politica, int) or id_politica <= 0:
            return {"error": "El parámetro 'id_politica' debe ser un número entero positivo."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:eliminarPolitica>
                 <tem:id>{id_politica}</tem:id>
              </tem:eliminarPolitica>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/eliminarPolitica",
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
        result_node = root.find(".//tem:eliminarPoliticaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'eliminarPoliticaResult' en la respuesta SOAP.")
            return {"exito": False, "resultado": None, "mensaje": "No se recibió confirmación del servidor."}

        # Convertir el resultado a booleano
        resultado = result_node.text.strip().lower() == "true"

        logger.info(f"Resultado de eliminación: {resultado}")
        return {
            "exito": True,
            "resultado": resultado,
            "mensaje": "Política eliminada correctamente." if resultado else "No se pudo eliminar la política."
        }

    except Exception as ex:
        logger.error(f"Error en eliminarPolitica(): {ex}")
        return {"error": str(ex)}



# ======================================================
# FUNCIÓN: existePolitica
# ======================================================
def existePolitica(descripcion: str) -> dict:
    """
    Verifica si ya existe una política con la descripción proporcionada.

    Parámetros:
        descripcion (str): Texto exacto de la descripción de la política a verificar.

    Retorna:
        dict:
            {
                "exito": bool,
                "existe": bool | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Verificando existencia de política con descripción: '{descripcion}'")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        if not descripcion or not isinstance(descripcion, str):
            return {"error": "El parámetro 'descripcion' es requerido y debe ser una cadena de texto."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:existePolitica>
                 <tem:descripcion>{descripcion}</tem:descripcion>
              </tem:existePolitica>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/existePolitica",
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
        result_node = root.find(".//tem:existePoliticaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'existePoliticaResult' en la respuesta SOAP.")
            return {"exito": False, "existe": None, "mensaje": "No se recibió confirmación del servidor."}

        # Convertir el resultado a booleano
        existe = result_node.text.strip().lower() == "true"

        logger.info(f"Resultado de existencia: {existe}")
        return {
            "exito": True,
            "existe": existe,
            "mensaje": "La política ya existe." if existe else "No existe una política con esa descripción."
        }

    except Exception as ex:
        logger.error(f"Error en existePolitica(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: insertarPolitica
# ======================================================
def insertarPolitica(politica: dict) -> dict:
    """
    Inserta una nueva política en el sistema mediante WS_GestionPoliticas.asmx.

    Parámetros:
        politica (dict): Objeto con los campos de la política a insertar:
            {
                "Id": int,
                "DescripcionPolitica": str,
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
        logger.info(f"Insertando nueva política: {politica.get('DescripcionPolitica')}")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        campos_requeridos = ["Id", "DescripcionPolitica", "FechaRegistro", "UltimaFechaCambio", "EsActivo"]
        faltantes = [c for c in campos_requeridos if c not in politica]
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
              <tem:insertarPolitica>
                 <tem:nuevaPolitica>
                    <tem:Id>{politica['Id']}</tem:Id>
                    <tem:DescripcionPolitica>{politica['DescripcionPolitica']}</tem:DescripcionPolitica>
                    <tem:FechaRegistro>{politica['FechaRegistro']}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{politica['UltimaFechaCambio']}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{"true" if politica["EsActivo"] else "false"}</tem:EsActivo>
                 </tem:nuevaPolitica>
              </tem:insertarPolitica>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/insertarPolitica",
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
        result_node = root.find(".//tem:insertarPoliticaResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'insertarPoliticaResult' en la respuesta SOAP.")
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
            "mensaje": "Política insertada correctamente." if id_insertado else "No se pudo insertar la política."
        }

    except Exception as ex:
        logger.error(f"Error en insertarPolitica(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: seleccionarPoliticaPorId
# ======================================================
def seleccionarPoliticaPorId(id_politica: int) -> dict:
    """
    Obtiene una política específica por su ID usando WS_GestionPoliticas.asmx.

    Parámetros:
        id_politica (int): Identificador único de la política.

    Retorna:
        dict:
            {
                "exito": bool,
                "politica": dict | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Consultando política con ID={id_politica}")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        if not isinstance(id_politica, int) or id_politica <= 0:
            return {"error": "El parámetro 'id_politica' debe ser un número entero positivo."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarPoliticaPorId>
                 <tem:id>{id_politica}</tem:id>
              </tem:seleccionarPoliticaPorId>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPoliticaPorId",
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
        result_node = root.find(".//tem:seleccionarPoliticaPorIdResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarPoliticaPorIdResult' en la respuesta SOAP.")
            return {"exito": False, "politica": None, "mensaje": "No se recibió información del servidor."}

        # ======================================================
        # Extracción de los campos de la política
        # ======================================================
        politica = {
            "Id": int(result_node.findtext("tem:Id", default="0", namespaces=ns)),
            "DescripcionPolitica": result_node.findtext("tem:DescripcionPolitica", default="", namespaces=ns),
            "FechaRegistro": result_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
            "UltimaFechaCambio": result_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
            "EsActivo": result_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
        }

        logger.info(f"Política encontrada: {politica}")
        return {
            "exito": True,
            "politica": politica,
            "mensaje": f"Política con ID {id_politica} obtenida correctamente."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarPoliticaPorId(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: seleccionarPoliticas
# ======================================================
def seleccionarPoliticas() -> dict:
    """
    Obtiene todas las políticas activas usando WS_GestionPoliticas.asmx.

    Retorna:
        dict:
            {
                "exito": bool,
                "politicas": list[dict] | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info("Consultando todas las políticas activas...")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarPoliticas/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarPoliticas",
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
        politicas_nodes = root.findall(".//tem:seleccionarPoliticasResult/tem:Politicas", ns)

        if not politicas_nodes:
            logger.warning("No se encontraron políticas activas en la respuesta SOAP.")
            return {"exito": True, "politicas": [], "mensaje": "No se encontraron políticas activas."}

        # ======================================================
        # Extracción de datos de cada política
        # ======================================================
        politicas = []
        for node in politicas_nodes:
            politica = {
                "Id": int(node.findtext("tem:Id", default="0", namespaces=ns)),
                "DescripcionPolitica": node.findtext("tem:DescripcionPolitica", default="", namespaces=ns),
                "FechaRegistro": node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UltimaFechaCambio": node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                "EsActivo": node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
            }
            politicas.append(politica)

        logger.info(f"Se encontraron {len(politicas)} políticas activas.")
        return {
            "exito": True,
            "politicas": politicas,
            "mensaje": f"Se encontraron {len(politicas)} políticas activas."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarPoliticas(): {ex}")
        return {"error": str(ex)}

