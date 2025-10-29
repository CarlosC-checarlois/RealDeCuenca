"""
Módulo de integración SOAP con el servicio remoto:
WS_GestionUsuarios.asmx

Autor: Carlos Quitus
Descripción:
    Contiene funciones que interpretan los métodos SOAP
    relacionados con la gestión de usuarios.
"""

import logging
import xml.etree.ElementTree as ET
from zeep import Client
from zeep.helpers import serialize_object
import requests

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
WSDL_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionUsuarios.asmx?WSDL"
SOAP_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionUsuarios.asmx"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==========================================================
# FUNCIÓN: actualizarUsuario
# ==========================================================
# ==========================================================
# FUNCIÓN: actualizarUsuario
# ==========================================================
def actualizarUsuario(usuario: dict) -> dict:
    """
    Actualiza los datos de un usuario existente en el sistema SOAP.

    Parámetros:
        usuario (dict): Debe contener las claves:
            Id (int)
            Nombre (str)
            Email (str)
            PasswordHash (str)
            Rol (str)
            FechaRegistro (str, formato 'YYYY-MM-DDTHH:MM:SS')
            UltimaFechaCambio (str, formato 'YYYY-MM-DDTHH:MM:SS')
            EsActivo (bool)
            UltimaFechainicioSesion (str, formato 'YYYY-MM-DDTHH:MM:SS')

    Retorna:
        dict: {"actualizado": bool, "mensaje": str}
    """
    try:
        logger.info(f"Actualizando usuario con ID {usuario.get('Id')} en WS_GestionUsuarios")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1 con namespaces 'soapenv' y 'tem')
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:actualizarUsuario>
                 <tem:usuarioEditado>
                    <tem:Id>{usuario.get('Id', 0)}</tem:Id>
                    <tem:Nombre>{usuario.get('Nombre', '')}</tem:Nombre>
                    <tem:Email>{usuario.get('Email', '')}</tem:Email>
                    <tem:PasswordHash>{usuario.get('PasswordHash', '')}</tem:PasswordHash>
                    <tem:Rol>{usuario.get('Rol', '')}</tem:Rol>
                    <tem:FechaRegistro>{usuario.get('FechaRegistro', '')}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{usuario.get('UltimaFechaCambio', '')}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{str(usuario.get('EsActivo', True)).lower()}</tem:EsActivo>
                    <tem:UltimaFechainicioSesion>{usuario.get('UltimaFechainicioSesion', '')}</tem:UltimaFechainicioSesion>
                 </tem:usuarioEditado>
              </tem:actualizarUsuario>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarUsuario",
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
        result_node = root.find(".//tem:actualizarUsuarioResult", ns)

        if result_node is None:
            logger.error("No se encontró el nodo actualizarUsuarioResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo actualizarUsuarioResult."}

        actualizado = result_node.text.strip().lower() == "true"
        logger.info(f"Usuario {usuario.get('Id')} actualizado: {actualizado}")

        return {
            "actualizado": actualizado,
            "mensaje": "Usuario actualizado correctamente" if actualizado else "No se pudo actualizar el usuario"
        }

    except Exception as ex:
        logger.error(f"Error en actualizarUsuario(): {ex}")
        return {"error": str(ex)}


# ==========================================================
# FUNCIÓN: eliminarUsuario
# ==========================================================
def eliminarUsuario(usuario_id: int) -> dict:
    """
    Desactiva un usuario (eliminación lógica) mediante el servicio SOAP.

    Parámetros:
        usuario_id (int): ID del usuario que se desea desactivar.

    Retorna:
        dict: {"eliminado": bool, "mensaje": str}
    """
    try:
        logger.info(f"Desactivando usuario con ID {usuario_id} mediante WS_GestionUsuarios")

        # ======================================================
        # Construcción del envelope SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <eliminarUsuario xmlns="http://tempuri.org/">
              <id>{usuario_id}</id>
            </eliminarUsuario>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/eliminarUsuario",
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
            "t": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//t:eliminarUsuarioResult", ns)

        if result_node is None:
            logger.error("No se encontró el nodo eliminarUsuarioResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo eliminarUsuarioResult."}

        eliminado = result_node.text.strip().lower() == "true"

        logger.info(f"Usuario ID {usuario_id} eliminado (desactivado): {eliminado}")

        return {
            "eliminado": eliminado,
            "mensaje": "Usuario desactivado correctamente" if eliminado else "No se pudo desactivar el usuario"
        }

    except Exception as ex:
        logger.error(f"Error en eliminarUsuario(): {ex}")
        return {"error": str(ex)}


# ==========================================================
# FUNCIÓN: iniciarSesion
# ==========================================================
def iniciarSesion(email: str, password: str) -> dict:
    """
    Valida las credenciales de un usuario para iniciar sesión mediante el servicio SOAP.

    Parámetros:
        email (str): Correo electrónico del usuario.
        password (str): Contraseña del usuario.

    Retorna:
        dict:
            - Si es exitoso: contiene los datos del usuario.
            - Si falla: {"error": "mensaje de error"}
    """
    try:
        logger.info(f"Iniciando sesión para usuario: {email}")

        # ======================================================
        # Construcción del envelope SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <iniciarSesion xmlns="http://tempuri.org/">
              <email>{email}</email>
              <password>{password}</password>
            </iniciarSesion>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/iniciarSesion",
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
            "t": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//t:iniciarSesionResult", ns)

        if result_node is None:
            logger.warning("Credenciales inválidas o usuario no encontrado.")
            return {"error": "Credenciales inválidas o usuario no encontrado."}

        # ======================================================
        # Extraer los datos del usuario
        # ======================================================
        def get_text(tag, default=""):
            text = result_node.findtext(f"t:{tag}", default, ns)
            return text.strip() if text else default

        usuario = {
            "Id": int(get_text("Id", "0")),
            "Nombre": get_text("Nombre"),
            "Email": get_text("Email"),
            "PasswordHash": get_text("PasswordHash"),
            "Rol": get_text("Rol"),
            "FechaRegistro": get_text("FechaRegistro"),
            "UltimaFechaCambio": get_text("UltimaFechaCambio"),
            "EsActivo": get_text("EsActivo", "false").lower() == "true",
            "UltimaFechainicioSesion": get_text("UltimaFechainicioSesion"),
        }

        logger.info(f"Inicio de sesión exitoso para usuario {usuario['Email']}")

        return usuario

    except Exception as ex:
        logger.error(f"Error en iniciarSesion(): {ex}")
        return {"error": str(ex)}


# ==========================================================
# FUNCIÓN: insertarUsuario
# ==========================================================
def insertarUsuario(usuario: dict) -> dict:
    """
    Inserta un nuevo usuario en el sistema mediante el servicio SOAP.

    Parámetros:
        usuario (dict): Debe contener los campos:
            - Id (int)
            - Nombre (str)
            - Email (str)
            - PasswordHash (str)
            - Rol (str)
            - FechaRegistro (str, formato ISO: 'YYYY-MM-DDTHH:MM:SS')
            - UltimaFechaCambio (str, formato ISO)
            - EsActivo (bool)
            - UltimaFechainicioSesion (str, formato ISO)

    Retorna:
        dict:
            {"insertado": bool, "nuevoId": int, "mensaje": str}
    """
    try:
        logger.info(f"Insertando nuevo usuario: {usuario.get('Nombre')} ({usuario.get('Email')})")

        # ======================================================
        # Construcción del envelope SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <insertarUsuario xmlns="http://tempuri.org/">
              <nuevoUsuario>
                <Id>{usuario.get('Id', 0)}</Id>
                <Nombre>{usuario.get('Nombre', '')}</Nombre>
                <Email>{usuario.get('Email', '')}</Email>
                <PasswordHash>{usuario.get('PasswordHash', '')}</PasswordHash>
                <Rol>{usuario.get('Rol', '')}</Rol>
                <FechaRegistro>{usuario.get('FechaRegistro', '')}</FechaRegistro>
                <UltimaFechaCambio>{usuario.get('UltimaFechaCambio', '')}</UltimaFechaCambio>
                <EsActivo>{str(usuario.get('EsActivo', True)).lower()}</EsActivo>
                <UltimaFechainicioSesion>{usuario.get('UltimaFechainicioSesion', '')}</UltimaFechainicioSesion>
              </nuevoUsuario>
            </insertarUsuario>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/insertarUsuario",
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
            "t": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//t:insertarUsuarioResult", ns)

        if result_node is None:
            logger.error("No se encontró el nodo insertarUsuarioResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo insertarUsuarioResult."}

        nuevo_id_text = result_node.text.strip() if result_node.text else "0"
        nuevo_id = int(nuevo_id_text) if nuevo_id_text.isdigit() else 0

        logger.info(f"Usuario insertado correctamente con ID {nuevo_id}")

        return {
            "insertado": nuevo_id > 0,
            "nuevoId": nuevo_id,
            "mensaje": f"Usuario insertado correctamente con ID {nuevo_id}" if nuevo_id > 0 else "No se pudo insertar el usuario"
        }

    except Exception as ex:
        logger.error(f"Error en insertarUsuario(): {ex}")
        return {"error": str(ex)}



# ==========================================================
# FUNCIÓN: reactivarUsuario
# ==========================================================
def reactivarUsuario(usuario_id: int) -> dict:
    """
    Reactiva un usuario previamente inactivo mediante el servicio SOAP.

    Parámetros:
        usuario_id (int): ID del usuario que se desea reactivar.

    Retorna:
        dict: {"reactivado": bool, "mensaje": str}
    """
    try:
        logger.info(f"Reactivando usuario con ID {usuario_id} mediante WS_GestionUsuarios")

        # ======================================================
        # Construcción del envelope SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <reactivarUsuario xmlns="http://tempuri.org/">
              <id>{usuario_id}</id>
            </reactivarUsuario>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/reactivarUsuario",
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
            "t": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//t:reactivarUsuarioResult", ns)

        if result_node is None:
            logger.error("No se encontró el nodo reactivarUsuarioResult en la respuesta SOAP.")
            return {"error": "Respuesta SOAP inválida o sin nodo reactivarUsuarioResult."}

        reactivado = result_node.text.strip().lower() == "true"

        logger.info(f"Usuario ID {usuario_id} reactivado: {reactivado}")

        return {
            "reactivado": reactivado,
            "mensaje": "Usuario reactivado correctamente" if reactivado else "No se pudo reactivar el usuario"
        }

    except Exception as ex:
        logger.error(f"Error en reactivarUsuario(): {ex}")
        return {"error": str(ex)}

# ==========================================================
# FUNCIÓN: seleccionarInactivos
# ==========================================================
def seleccionarInactivos() -> dict:
    """
    Obtiene todos los usuarios inactivos del sistema (auditoría) mediante el servicio SOAP.

    Retorna:
        dict:
            {
                "usuarios": [ {datos...}, ... ],
                "total": int,
                "mensaje": str
            }
            o {"error": "mensaje"} en caso de fallo.
    """
    try:
        logger.info("Obteniendo lista de usuarios inactivos desde WS_GestionUsuarios")

        # ======================================================
        # Construcción del envelope SOAP (versión 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <seleccionarInactivos xmlns="http://tempuri.org/" />
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarInactivos",
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
            "t": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        usuarios_nodes = root.findall(".//t:Usuarios", ns)

        if not usuarios_nodes:
            logger.warning("No se encontraron usuarios inactivos en la respuesta SOAP.")
            return {"usuarios": [], "total": 0, "mensaje": "No hay usuarios inactivos."}

        # ======================================================
        # Extraer datos de cada usuario
        # ======================================================
        usuarios = []
        for u in usuarios_nodes:
            def get_text(tag, default=""):
                text = u.findtext(f"t:{tag}", default, ns)
                return text.strip() if text else default

            usuarios.append({
                "Id": int(get_text("Id", "0")),
                "Nombre": get_text("Nombre"),
                "Email": get_text("Email"),
                "PasswordHash": get_text("PasswordHash"),
                "Rol": get_text("Rol"),
                "FechaRegistro": get_text("FechaRegistro"),
                "UltimaFechaCambio": get_text("UltimaFechaCambio"),
                "EsActivo": get_text("EsActivo", "false").lower() == "true",
                "UltimaFechainicioSesion": get_text("UltimaFechainicioSesion"),
            })

        logger.info(f"Usuarios inactivos obtenidos: {len(usuarios)}")

        return {
            "usuarios": usuarios,
            "total": len(usuarios),
            "mensaje": f"Se encontraron {len(usuarios)} usuarios inactivos."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarInactivos(): {ex}")
        return {"error": str(ex)}
# ==========================================================
# FUNCIÓN: seleccionarPorId
# ==========================================================
def seleccionarPorId(usuario_id: int) -> dict:
    """
    Obtiene la información completa de un usuario por su ID mediante el servicio SOAP WS_GestionUsuarios.

    Parámetros:
        usuario_id (int): ID del usuario a consultar.

    Retorna:
        dict con los datos del usuario, o {"error": "mensaje"} si ocurre un problema.
    """
    try:
        logger.info(f"Consultando usuario por ID: {usuario_id}")

        # ======================================================
        # Construcción del envelope SOAP (versión 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <seleccionarPorId xmlns="http://tempuri.org/">
              <id>{usuario_id}</id>
            </seleccionarPorId>
          </soap:Body>
        </soap:Envelope>"""

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
        # Parseo del XML de respuesta
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "t": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//t:seleccionarPorIdResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo seleccionarPorIdResult en la respuesta SOAP.")
            return {"error": f"No se encontró ningún usuario con ID {usuario_id}."}

        # ======================================================
        # Extraer los datos del usuario
        # ======================================================
        def get_text(tag, default=""):
            text = result_node.findtext(f"t:{tag}", default, ns)
            return text.strip() if text else default

        usuario = {
            "Id": int(get_text("Id", "0")),
            "Nombre": get_text("Nombre"),
            "Email": get_text("Email"),
            "PasswordHash": get_text("PasswordHash"),
            "Rol": get_text("Rol"),
            "FechaRegistro": get_text("FechaRegistro"),
            "UltimaFechaCambio": get_text("UltimaFechaCambio"),
            "EsActivo": get_text("EsActivo", "false").lower() == "true",
            "UltimaFechainicioSesion": get_text("UltimaFechainicioSesion"),
        }

        logger.info(f"Usuario encontrado por ID {usuario_id}: {usuario['Nombre']} ({usuario['Email']})")

        return usuario

    except Exception as ex:
        logger.error(f"Error en seleccionarPorId(): {ex}")
        return {"error": str(ex)}
# ==========================================================
# FUNCIÓN: seleccionarUsuarios
# ==========================================================
def seleccionarUsuarios() -> dict:
    """
    Obtiene todos los usuarios activos del sistema mediante el servicio SOAP WS_GestionUsuarios.

    Retorna:
        dict:
            {
                "usuarios": [ {datos...}, ... ],
                "total": int,
                "mensaje": str
            }
            o {"error": "mensaje"} en caso de fallo.
    """
    try:
        logger.info("Obteniendo lista de usuarios activos desde WS_GestionUsuarios")

        # ======================================================
        # Construcción del envelope SOAP (versión 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <seleccionarUsuarios xmlns="http://tempuri.org/" />
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarUsuarios",
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
            "t": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        usuarios_nodes = root.findall(".//t:Usuarios", ns)

        if not usuarios_nodes:
            logger.warning("No se encontraron usuarios activos en la respuesta SOAP.")
            return {"usuarios": [], "total": 0, "mensaje": "No hay usuarios activos."}

        # ======================================================
        # Extraer datos de cada usuario
        # ======================================================
        usuarios = []
        for u in usuarios_nodes:
            def get_text(tag, default=""):
                text = u.findtext(f"t:{tag}", default, ns)
                return text.strip() if text else default

            usuarios.append({
                "Id": int(get_text("Id", "0")),
                "Nombre": get_text("Nombre"),
                "Email": get_text("Email"),
                "PasswordHash": get_text("PasswordHash"),
                "Rol": get_text("Rol"),
                "FechaRegistro": get_text("FechaRegistro"),
                "UltimaFechaCambio": get_text("UltimaFechaCambio"),
                "EsActivo": get_text("EsActivo", "false").lower() == "true",
                "UltimaFechainicioSesion": get_text("UltimaFechainicioSesion"),
            })

        logger.info(f"Usuarios activos obtenidos: {len(usuarios)}")

        return {
            "usuarios": usuarios,
            "total": len(usuarios),
            "mensaje": f"Se encontraron {len(usuarios)} usuarios activos."
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarUsuarios(): {ex}")
        return {"error": str(ex)}


