import logging
from zeep import Client, helpers
import logging
from datetime import datetime
import requests
import xml.etree.ElementTree as ET
import logging
# URL del servicio SOAP
WSDL_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionEspacios.asmx?WSDL"
SOAP_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionEspacios.asmx"

def safe_str(value, default=""):
    return str(value).strip() if value is not None else default


def safe_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(value)
    except Exception:
        return default


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
def safe_text(value):
    return value.strip() if value else ""
# Configuración del logger
logger = logging.getLogger(__name__)



def eliminarEspacio(id_espacio: int) -> dict:
    """
    Elimina (desactiva) un espacio mediante soft delete usando el servicio SOAP.

    Parámetros:
        id_espacio (int): ID del espacio que se desea eliminar.

    Retorna:
        dict: Resultado de la operación con las claves:
              - exito (bool)
              - mensaje (str)
    """
    try:
        logger.info(f"Intentando eliminar espacio con ID {id_espacio}...")

        # Crear cliente SOAP
        client = Client(WSDL_URL)

        # Llamar al método remoto
        resultado = client.service.eliminarEspacio(id=id_espacio)

        # Validar resultado
        if resultado is True:
            mensaje = f"Espacio con ID {id_espacio} eliminado (soft delete) correctamente."
            logger.info(mensaje)
            return {"exito": True, "mensaje": mensaje}

        else:
            mensaje = f"No se pudo eliminar el espacio con ID {id_espacio}. El servicio retornó False."
            logger.warning(mensaje)
            return {"exito": False, "mensaje": mensaje}

    except Exception as ex:
        logger.error(f"Error al eliminar espacio (ID: {id_espacio}): {ex}")
        return {"exito": False, "mensaje": f"Error al eliminar el espacio: {ex}"}

def insertarEspacio(nuevo_espacio: dict) -> dict:
    """
    Inserta un nuevo espacio en el sistema mediante el servicio SOAP.

    Parámetros:
        nuevo_espacio (dict): Diccionario con los campos requeridos por el servicio.
                              Ejemplo:
                              {
                                  "HotelId": 1,
                                  "TipoServicioId": 2,
                                  "TipoAlimentacionId": 1,
                                  "Nombre": "Suite Deluxe",
                                  "Moneda": "USD",
                                  "CostoDiario": 145.50,
                                  "CapacidadAdultos": 2,
                                  "CapacidadNinios": 1,
                                  "Habitaciones": 1,
                                  "Parqueaderos": 1,
                                  "DimensionesDelLugar": 40,
                                  "DescripcionDelLugar": "Suite moderna con vista panorámica.",
                                  "Puntuacion": 5,
                                  "Ubicacion": "Cuenca - Ecuador",
                                  "MinutosRetencion": 120,
                                  "ExpiraEn": "2025-12-31T00:00:00",
                                  "EsBloqueada": False,
                                  "FechaRegistro": "2025-10-29T14:00:00",
                                  "UltimaFechaCambio": "2025-10-29T14:00:00",
                                  "EsActivo": True
                              }

    Retorna:
        dict: Resultado de la operación con las claves:
              - exito (bool)
              - mensaje (str)
              - nuevo_id (int | None)
    """

    try:
        logger.info(f"Insertando nuevo espacio: {nuevo_espacio.get('Nombre', 'Sin nombre')}")

        # Crear cliente SOAP
        client = Client(WSDL_URL)

        # Definir estructura del espacio
        espacio_data = {
            "Id": 0,  # el servicio lo asigna
            "HotelId": nuevo_espacio.get("HotelId"),
            "TipoServicioId": nuevo_espacio.get("TipoServicioId"),
            "TipoAlimentacionId": nuevo_espacio.get("TipoAlimentacionId"),
            "Nombre": nuevo_espacio.get("Nombre"),
            "Moneda": nuevo_espacio.get("Moneda", "USD"),
            "CostoDiario": nuevo_espacio.get("CostoDiario", 0.0),
            "CapacidadAdultos": nuevo_espacio.get("CapacidadAdultos", 1),
            "CapacidadNinios": nuevo_espacio.get("CapacidadNinios", 0),
            "Habitaciones": nuevo_espacio.get("Habitaciones", 1),
            "Parqueaderos": nuevo_espacio.get("Parqueaderos", 0),
            "DimensionesDelLugar": nuevo_espacio.get("DimensionesDelLugar", 0),
            "DescripcionDelLugar": nuevo_espacio.get("DescripcionDelLugar", ""),
            "Puntuacion": nuevo_espacio.get("Puntuacion", 0),
            "Ubicacion": nuevo_espacio.get("Ubicacion", ""),
            "MinutosRetencion": nuevo_espacio.get("MinutosRetencion", 60),
            "ExpiraEn": nuevo_espacio.get("ExpiraEn", datetime.now().isoformat()),
            "EsBloqueada": nuevo_espacio.get("EsBloqueada", False),
            "FechaRegistro": nuevo_espacio.get("FechaRegistro", datetime.now().isoformat()),
            "UltimaFechaCambio": nuevo_espacio.get("UltimaFechaCambio", datetime.now().isoformat()),
            "EsActivo": nuevo_espacio.get("EsActivo", True),
        }

        # Llamar al método remoto
        resultado = client.service.insertarEspacio(nuevoEspacio=espacio_data)

        # Validar respuesta (devuelve el ID del nuevo registro o 0 si falla)
        if resultado and int(resultado) > 0:
            mensaje = f"Espacio '{espacio_data['Nombre']}' insertado correctamente con ID {resultado}."
            logger.info(mensaje)
            return {"exito": True, "mensaje": mensaje, "nuevo_id": int(resultado)}
        else:
            mensaje = f"No se pudo insertar el espacio '{espacio_data['Nombre']}'."
            logger.warning(mensaje)
            return {"exito": False, "mensaje": mensaje, "nuevo_id": None}

    except Exception as ex:
        logger.error(f"Error en insertarEspacio: {ex}")
        return {"exito": False, "mensaje": f"Error al insertar espacio: {ex}", "nuevo_id": None}

def actualizarEspacio(espacio_editado: dict) -> dict:
    """
    Actualiza los datos de un espacio existente mediante el servicio SOAP WS_GestionEspacios.asmx.

    Parámetros:
        espacio_editado (dict): Diccionario con los campos del espacio a actualizar.

    Retorna:
        dict: {
            "exito": bool,
            "mensaje": str
        }
        o {"error": str} si hay un fallo.
    """

    try:
        logger.info(f"Actualizando espacio con ID {espacio_editado.get('Id')}...")

        # ======================================================
        # Construcción del cuerpo SOAP
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <actualizarEspacio xmlns="http://tempuri.org/">
              <espacioEditado>
                <Id>{safe_int(espacio_editado.get("Id"))}</Id>
                <HotelId>{safe_int(espacio_editado.get("HotelId"))}</HotelId>
                <TipoServicioId>{safe_int(espacio_editado.get("TipoServicioId"))}</TipoServicioId>
                <TipoAlimentacionId>{safe_int(espacio_editado.get("TipoAlimentacionId"))}</TipoAlimentacionId>
                <Nombre>{safe_str(espacio_editado.get("Nombre"))}</Nombre>
                <Moneda>{safe_str(espacio_editado.get("Moneda", "USD"))}</Moneda>
                <CostoDiario>{safe_float(espacio_editado.get("CostoDiario"))}</CostoDiario>
                <CapacidadAdultos>{safe_int(espacio_editado.get("CapacidadAdultos"))}</CapacidadAdultos>
                <CapacidadNinios>{safe_int(espacio_editado.get("CapacidadNinios"))}</CapacidadNinios>
                <Habitaciones>{safe_int(espacio_editado.get("Habitaciones"))}</Habitaciones>
                <Parqueaderos>{safe_int(espacio_editado.get("Parqueaderos"))}</Parqueaderos>
                <DimensionesDelLugar>{safe_int(espacio_editado.get("DimensionesDelLugar"))}</DimensionesDelLugar>
                <DescripcionDelLugar>{safe_str(espacio_editado.get("DescripcionDelLugar"))}</DescripcionDelLugar>
                <Puntuacion>{safe_int(espacio_editado.get("Puntuacion"))}</Puntuacion>
                <Ubicacion>{safe_str(espacio_editado.get("Ubicacion"))}</Ubicacion>
                <MinutosRetencion>{safe_int(espacio_editado.get("MinutosRetencion"))}</MinutosRetencion>
                <ExpiraEn>{safe_str(espacio_editado.get("ExpiraEn", datetime.now().isoformat()))}</ExpiraEn>
                <EsBloqueada>{str(espacio_editado.get("EsBloqueada", False)).lower()}</EsBloqueada>
                <FechaRegistro>{safe_str(espacio_editado.get("FechaRegistro", datetime.now().isoformat()))}</FechaRegistro>
                <UltimaFechaCambio>{safe_str(espacio_editado.get("UltimaFechaCambio", datetime.now().isoformat()))}</UltimaFechaCambio>
                <EsActivo>{str(espacio_editado.get("EsActivo", True)).lower()}</EsActivo>
              </espacioEditado>
            </actualizarEspacio>
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarEspacio",
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
        result_node = root.find(".//tem:actualizarEspacioResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo actualizarEspacioResult en la respuesta SOAP.")
            return {"exito": False, "mensaje": "No se recibió confirmación del servicio."}

        exito = str(result_node.text).strip().lower() == "true"

        if exito:
            mensaje = f"Espacio con ID {espacio_editado.get('Id')} actualizado correctamente."
            logger.info(mensaje)
            return {"exito": True, "mensaje": mensaje}
        else:
            mensaje = f"No se pudo actualizar el espacio con ID {espacio_editado.get('Id')}."
            logger.warning(mensaje)
            return {"exito": False, "mensaje": mensaje}

    except Exception as ex:
        logger.error(f"Error en actualizarEspacio(): {ex}")
        return {"error": str(ex)}

# ==========================================
# FUNCIÓN PRINCIPAL: seleccionarEspacios
# ==========================================
def seleccionarEspacios() -> dict:
    """
    Obtiene todos los espacios activos desde el servicio SOAP WS_GestionEspacios.asmx.

    Retorna:
        dict: {
            "exito": bool,
            "mensaje": str,
            "espacios": [ {...}, {...} ]
        }
    """
    try:
        logger.info("Consultando todos los espacios activos en WS_GestionEspacios...")

        # ======================================================
        # Construcción del cuerpo SOAP
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                       xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                       xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <seleccionarEspacios xmlns="http://tempuri.org/" />
          </soap:Body>
        </soap:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarEspacios",
        }

        # ======================================================
        # Envío de solicitud SOAP
        # ======================================================
        response = requests.post(SOAP_URL, data=soap_body.encode("utf-8"), headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"HTTP {response.status_code}: {response.text}")
            return {"exito": False, "mensaje": f"Error HTTP {response.status_code}"}

        # ======================================================
        # Parseo de respuesta XML
        # ======================================================
        ns = {
            "soap": "http://schemas.xmlsoap.org/soap/envelope/",
            "tem": "http://tempuri.org/",
        }

        root = ET.fromstring(response.text)
        result_node = root.find(".//tem:seleccionarEspaciosResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo seleccionarEspaciosResult en la respuesta SOAP.")
            return {"exito": False, "mensaje": "No se encontraron espacios."}

        # Buscar todos los nodos <Espacios>
        espacios_nodes = result_node.findall("tem:Espacios", ns)
        espacios = []

        for nodo in espacios_nodes:
            e = {
                "Id": safe_text(nodo.findtext("tem:Id", "", ns)),
                "HotelId": safe_text(nodo.findtext("tem:HotelId", "", ns)),
                "TipoServicioId": safe_text(nodo.findtext("tem:TipoServicioId", "", ns)),
                "TipoAlimentacionId": safe_text(nodo.findtext("tem:TipoAlimentacionId", "", ns)),
                "Nombre": safe_text(nodo.findtext("tem:Nombre", "", ns)),
                "Moneda": safe_text(nodo.findtext("tem:Moneda", "USD", ns)),
                "CostoDiario": safe_text(nodo.findtext("tem:CostoDiario", "0", ns)),
                "CapacidadAdultos": safe_text(nodo.findtext("tem:CapacidadAdultos", "0", ns)),
                "CapacidadNinios": safe_text(nodo.findtext("tem:CapacidadNinios", "0", ns)),
                "Habitaciones": safe_text(nodo.findtext("tem:Habitaciones", "0", ns)),
                "Parqueaderos": safe_text(nodo.findtext("tem:Parqueaderos", "0", ns)),
                "DimensionesDelLugar": safe_text(nodo.findtext("tem:DimensionesDelLugar", "0", ns)),
                "DescripcionDelLugar": safe_text(nodo.findtext("tem:DescripcionDelLugar", "", ns)),
                "Puntuacion": safe_text(nodo.findtext("tem:Puntuacion", "0", ns)),
                "Ubicacion": safe_text(nodo.findtext("tem:Ubicacion", "", ns)),
                "MinutosRetencion": safe_text(nodo.findtext("tem:MinutosRetencion", "0", ns)),
                "ExpiraEn": safe_text(nodo.findtext("tem:ExpiraEn", "", ns)),
                "EsBloqueada": safe_bool(nodo.findtext("tem:EsBloqueada", "false", ns)),
                "FechaRegistro": safe_text(nodo.findtext("tem:FechaRegistro", "", ns)),
                "UltimaFechaCambio": safe_text(nodo.findtext("tem:UltimaFechaCambio", "", ns)),
                "EsActivo": safe_bool(nodo.findtext("tem:EsActivo", "false", ns)),

                # Subnodos anidados
                "Hotel": safe_text(nodo.findtext("tem:Hotel/tem:Nombre", "", ns)),
                "TipoServicio": safe_text(nodo.findtext("tem:TipoServicio/tem:Nombre", "", ns)),
                "TipoAlimentacion": safe_text(nodo.findtext("tem:TipoAlimentacion/tem:Nombre", "", ns)),
            }
            espacios.append(e)

        if not espacios:
            logger.info("No se encontraron espacios activos en la respuesta SOAP.")
            return {"exito": True, "mensaje": "No se encontraron espacios activos.", "espacios": []}

        logger.info(f"Se encontraron {len(espacios)} espacios activos.")
        return {
            "exito": True,
            "mensaje": f"Se encontraron {len(espacios)} espacio(s) activo(s).",
            "espacios": espacios
        }

    except Exception as ex:
        logger.error(f"Error en seleccionarEspacios(): {ex}")
        return {"exito": False, "mensaje": f"Error al consultar los espacios: {ex}"}






# ==========================================================
if __name__ == "__main__":
    resultado = buscarEspacios()
    print(resultado)