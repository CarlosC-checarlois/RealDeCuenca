import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ======================================================
# CONFIGURACIÓN GLOBAL
# ======================================================
SOAP_URL = "https://realdecuenca-btccaacvcpgyadhb.canadacentral-01.azurewebsites.net/WS_GestionHotel.asmx"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ======================================================
# FUNCIÓN: actualizarHotel
# ======================================================
def actualizarHotel(hotel: dict) -> dict:
    """
    Actualiza los datos de un hotel existente mediante WS_GestionHotel.asmx.

    Parámetros:
        hotel (dict): Datos del hotel a actualizar. Ejemplo:
            {
                "Id": 5,
                "Nombre": "Hotel Real de Cuenca",
                "FechaRegistro": "2023-10-28T10:00:00",
                "UltimaFechaCambio": "2025-10-28T12:00:00",
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
        logger.info(f"Actualizando hotel con ID={hotel.get('Id')} en WS_GestionHotel")

        # ======================================================
        # Validación de campos obligatorios
        # ======================================================
        if "Id" not in hotel or not isinstance(hotel["Id"], int) or hotel["Id"] <= 0:
            return {"error": "El campo 'Id' del hotel es obligatorio y debe ser un número entero válido."}

        if "Nombre" not in hotel or not hotel["Nombre"]:
            return {"error": "El campo 'Nombre' es obligatorio para actualizar un hotel."}

        # Fechas por defecto
        fecha_registro = hotel.get("FechaRegistro", datetime.now().isoformat())
        ultima_fecha_cambio = hotel.get("UltimaFechaCambio", datetime.now().isoformat())
        es_activo = str(hotel.get("EsActivo", True)).lower()

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
          <soapenv:Header/>
          <soapenv:Body>
            <tem:actualizarHotel>
              <tem:hotelEditado>
                <tem:Id>{hotel["Id"]}</tem:Id>
                <tem:Nombre>{hotel["Nombre"]}</tem:Nombre>
                <tem:FechaRegistro>{fecha_registro}</tem:FechaRegistro>
                <tem:UltimaFechaCambio>{ultima_fecha_cambio}</tem:UltimaFechaCambio>
                <tem:EsActivo>{es_activo}</tem:EsActivo>
              </tem:hotelEditado>
            </tem:actualizarHotel>
          </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/actualizarHotel",
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
        result_node = root.find(".//tem:actualizarHotelResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'actualizarHotelResult' en la respuesta SOAP.")
            return {"exito": False, "mensaje": "No se pudo determinar si la actualización fue exitosa."}

        resultado = result_node.text.strip().lower() == "true"

        if resultado:
            logger.info(f"Hotel con ID={hotel['Id']} actualizado correctamente.")
            return {"exito": True, "mensaje": f"Hotel '{hotel['Nombre']}' actualizado exitosamente."}
        else:
            logger.warning(f"No se logró actualizar el hotel con ID={hotel['Id']}.")
            return {"exito": False, "mensaje": "No se pudo actualizar el hotel."}

    except Exception as ex:
        logger.error(f"Error en actualizarHotel(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: buscarHotelPorNombre
# ======================================================
def buscarHotelPorNombre(nombre: str) -> dict:
    """
    Busca hoteles por nombre (coincidencia parcial) usando el WS_GestionHotel.asmx.

    Parámetros:
        nombre (str): Nombre o parte del nombre del hotel a buscar.

    Retorna:
        dict:
            {
                "exito": bool,
                "hoteles": [
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
        logger.info(f"Buscando hoteles con nombre que contenga: '{nombre}'")

        # ======================================================
        # Validación del parámetro
        # ======================================================
        if not nombre or not isinstance(nombre, str):
            return {"error": "El parámetro 'nombre' es obligatorio y debe ser una cadena de texto."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:buscarHotelPorNombre>
                 <tem:nombre>{nombre}</tem:nombre>
              </tem:buscarHotelPorNombre>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/buscarHotelPorNombre",
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
        result_node = root.find(".//tem:buscarHotelPorNombreResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'buscarHotelPorNombreResult' en la respuesta SOAP.")
            return {"exito": False, "hoteles": [], "mensaje": "No se encontraron coincidencias."}

        # ======================================================
        # Recorrer las etiquetas <Hotel> y construir la lista
        # ======================================================
        hoteles = []
        for hotel_node in result_node.findall("tem:Hotel", ns):
            hotel = {
                "Id": int(hotel_node.findtext("tem:Id", default="0", namespaces=ns)),
                "Nombre": hotel_node.findtext("tem:Nombre", default="", namespaces=ns),
                "FechaRegistro": hotel_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                "UltimaFechaCambio": hotel_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                "EsActivo": hotel_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
            }
            if hotel["Id"] > 0:
                hoteles.append(hotel)

        if not hoteles:
            logger.info("No se encontraron hoteles que coincidan con el nombre proporcionado.")
            return {"exito": True, "hoteles": [], "mensaje": "No se encontraron hoteles con ese nombre."}

        logger.info(f"Se encontraron {len(hoteles)} hoteles coincidentes con '{nombre}'.")
        return {"exito": True, "hoteles": hoteles, "mensaje": "Hoteles encontrados correctamente."}

    except Exception as ex:
        logger.error(f"Error en buscarHotelPorNombre(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: eliminarHotel
# ======================================================
def eliminarHotel(hotel_id: int) -> dict:
    """
    Elimina (desactiva) un hotel mediante Soft Delete usando WS_GestionHotel.asmx.

    Parámetros:
        hotel_id (int): ID del hotel a eliminar.

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
        logger.info(f"Solicitando eliminación (soft delete) del hotel con ID={hotel_id}")

        # ======================================================
        # Validación de parámetros
        # ======================================================
        if not isinstance(hotel_id, int) or hotel_id <= 0:
            return {"error": "El parámetro 'hotel_id' debe ser un número entero positivo."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:eliminarHotel>
                 <tem:id>{hotel_id}</tem:id>
              </tem:eliminarHotel>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/eliminarHotel",
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
        result_node = root.find(".//tem:eliminarHotelResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'eliminarHotelResult' en la respuesta SOAP.")
            return {"exito": False, "mensaje": "No se pudo determinar si la eliminación fue exitosa."}

        resultado = result_node.text.strip().lower() == "true"

        if resultado:
            logger.info(f"Hotel con ID={hotel_id} eliminado (soft delete) correctamente.")
            return {"exito": True, "mensaje": f"Hotel con ID={hotel_id} eliminado correctamente."}
        else:
            logger.warning(f"No se logró eliminar el hotel con ID={hotel_id}.")
            return {"exito": False, "mensaje": "No se pudo eliminar el hotel."}

    except Exception as ex:
        logger.error(f"Error en eliminarHotel(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: insertarHotel
# ======================================================
def insertarHotel(hotel: dict) -> dict:
    """
    Inserta un nuevo hotel en el sistema mediante WS_GestionHotel.asmx.

    Parámetros:
        hotel (dict): Datos del nuevo hotel. Ejemplo:
            {
                "Id": 0,  # opcional
                "Nombre": "Hotel Los Andes",
                "FechaRegistro": "2025-10-28T12:00:00",
                "UltimaFechaCambio": "2025-10-28T12:00:00",
                "EsActivo": True
            }

    Retorna:
        dict:
            {
                "exito": bool,
                "id_hotel": int | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """

    try:
        logger.info(f"Insertando nuevo hotel: {hotel.get('Nombre')}")

        # ======================================================
        # Validación de parámetros obligatorios
        # ======================================================
        if not hotel.get("Nombre"):
            return {"error": "El campo 'Nombre' del hotel es obligatorio."}

        # ======================================================
        # Asignar valores por defecto
        # ======================================================
        fecha_actual = datetime.now().isoformat()
        fecha_registro = hotel.get("FechaRegistro", fecha_actual)
        ultima_fecha_cambio = hotel.get("UltimaFechaCambio", fecha_actual)
        es_activo = str(hotel.get("EsActivo", True)).lower()
        hotel_id = hotel.get("Id", 0)

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:insertarHotel>
                 <tem:nuevoHotel>
                    <tem:Id>{hotel_id}</tem:Id>
                    <tem:Nombre>{hotel["Nombre"]}</tem:Nombre>
                    <tem:FechaRegistro>{fecha_registro}</tem:FechaRegistro>
                    <tem:UltimaFechaCambio>{ultima_fecha_cambio}</tem:UltimaFechaCambio>
                    <tem:EsActivo>{es_activo}</tem:EsActivo>
                 </tem:nuevoHotel>
              </tem:insertarHotel>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/insertarHotel",
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
        result_node = root.find(".//tem:insertarHotelResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'insertarHotelResult' en la respuesta SOAP.")
            return {"exito": False, "id_hotel": None, "mensaje": "No se pudo obtener el ID del hotel insertado."}

        nuevo_id = int(result_node.text.strip())

        if nuevo_id > 0:
            logger.info(f"Hotel insertado exitosamente con ID={nuevo_id}")
            return {"exito": True, "id_hotel": nuevo_id, "mensaje": f"Hotel '{hotel['Nombre']}' insertado correctamente."}
        else:
            logger.warning("El servicio no devolvió un ID válido.")
            return {"exito": False, "id_hotel": None, "mensaje": "No se pudo insertar el hotel."}

    except Exception as ex:
        logger.error(f"Error en insertarHotel(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: obtenerEspaciosDelHotel
# ======================================================
def obtenerEspaciosDelHotel(hotel_id: int) -> dict:
    """
    Obtiene los espacios asociados a un hotel específico usando WS_GestionHotel.asmx.

    Parámetros:
        hotel_id (int): ID del hotel del cual se quieren obtener los espacios.

    Retorna:
        dict:
            {
                "exito": bool,
                "espacios": [ {...}, {...} ],
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Consultando espacios del hotel con ID={hotel_id}")

        # ======================================================
        # Validación del parámetro
        # ======================================================
        if not isinstance(hotel_id, int) or hotel_id <= 0:
            return {"error": "El parámetro 'hotel_id' debe ser un número entero positivo."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:obtenerEspaciosDelHotel>
                 <tem:hotelId>{hotel_id}</tem:hotelId>
              </tem:obtenerEspaciosDelHotel>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/obtenerEspaciosDelHotel",
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
        result_node = root.find(".//tem:obtenerEspaciosDelHotelResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'obtenerEspaciosDelHotelResult' en la respuesta SOAP.")
            return {"exito": False, "espacios": [], "mensaje": "No se encontraron espacios."}

        # ======================================================
        # Recorrer los nodos <Espacios>
        # ======================================================
        espacios = []
        for espacio_node in result_node.findall("tem:Espacios", ns):
            try:
                espacio = {
                    "Id": int(espacio_node.findtext("tem:Id", default="0", namespaces=ns)),
                    "HotelId": int(espacio_node.findtext("tem:HotelId", default="0", namespaces=ns)),
                    "TipoServicioId": int(espacio_node.findtext("tem:TipoServicioId", default="0", namespaces=ns)),
                    "TipoAlimentacionId": int(espacio_node.findtext("tem:TipoAlimentacionId", default="0", namespaces=ns)),
                    "Nombre": espacio_node.findtext("tem:Nombre", default="", namespaces=ns),
                    "Moneda": espacio_node.findtext("tem:Moneda", default="", namespaces=ns),
                    "CostoDiario": float(espacio_node.findtext("tem:CostoDiario", default="0", namespaces=ns)),
                    "CapacidadAdultos": int(espacio_node.findtext("tem:CapacidadAdultos", default="0", namespaces=ns)),
                    "CapacidadNinios": int(espacio_node.findtext("tem:CapacidadNinios", default="0", namespaces=ns)),
                    "Habitaciones": int(espacio_node.findtext("tem:Habitaciones", default="0", namespaces=ns)),
                    "Parqueaderos": int(espacio_node.findtext("tem:Parqueaderos", default="0", namespaces=ns)),
                    "DimensionesDelLugar": int(espacio_node.findtext("tem:DimensionesDelLugar", default="0", namespaces=ns)),
                    "DescripcionDelLugar": espacio_node.findtext("tem:DescripcionDelLugar", default="", namespaces=ns),
                    "Puntuacion": int(espacio_node.findtext("tem:Puntuacion", default="0", namespaces=ns)),
                    "Ubicacion": espacio_node.findtext("tem:Ubicacion", default="", namespaces=ns),
                    "MinutosRetencion": int(espacio_node.findtext("tem:MinutosRetencion", default="0", namespaces=ns)),
                    "ExpiraEn": espacio_node.findtext("tem:ExpiraEn", default="", namespaces=ns),
                    "EsBloqueada": espacio_node.findtext("tem:EsBloqueada", default="false", namespaces=ns).lower() == "true",
                    "FechaRegistro": espacio_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                    "UltimaFechaCambio": espacio_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                    "EsActivo": espacio_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
                }

                # Agregar subnodos Hotel / TipoServicio / TipoAlimentacion (si existen)
                hotel_sub = espacio_node.find("tem:Hotel", ns)
                if hotel_sub is not None:
                    espacio["Hotel"] = {
                        "Id": int(hotel_sub.findtext("tem:Id", default="0", namespaces=ns)),
                        "Nombre": hotel_sub.findtext("tem:Nombre", default="", namespaces=ns),
                    }

                tipo_servicio_sub = espacio_node.find("tem:TipoServicio", ns)
                if tipo_servicio_sub is not None:
                    espacio["TipoServicio"] = {
                        "Id": int(tipo_servicio_sub.findtext("tem:Id", default="0", namespaces=ns)),
                        "Nombre": tipo_servicio_sub.findtext("tem:Nombre", default="", namespaces=ns),
                    }

                tipo_alim_sub = espacio_node.find("tem:TipoAlimentacion", ns)
                if tipo_alim_sub is not None:
                    espacio["TipoAlimentacion"] = {
                        "Id": int(tipo_alim_sub.findtext("tem:Id", default="0", namespaces=ns)),
                        "Nombre": tipo_alim_sub.findtext("tem:Nombre", default="", namespaces=ns),
                    }

                espacios.append(espacio)
            except Exception as parse_err:
                logger.warning(f"Error al procesar un nodo <Espacios>: {parse_err}")

        if not espacios:
            logger.info(f"No se encontraron espacios asociados al hotel con ID={hotel_id}.")
            return {"exito": True, "espacios": [], "mensaje": "El hotel no tiene espacios registrados."}

        logger.info(f"Se encontraron {len(espacios)} espacios para el hotel con ID={hotel_id}.")
        return {"exito": True, "espacios": espacios, "mensaje": "Espacios obtenidos correctamente."}

    except Exception as ex:
        logger.error(f"Error en obtenerEspaciosDelHotel(): {ex}")
        return {"error": str(ex)}

# ======================================================
# FUNCIÓN: seleccionarHotelPorId
# ======================================================
def seleccionarHotelPorId(hotel_id: int) -> dict:
    """
    Obtiene un hotel específico por su ID usando WS_GestionHotel.asmx.

    Parámetros:
        hotel_id (int): ID del hotel a consultar.

    Retorna:
        dict:
            {
                "exito": bool,
                "hotel": { ... } | None,
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info(f"Consultando hotel con ID={hotel_id}")

        # ======================================================
        # Validación del parámetro
        # ======================================================
        if not isinstance(hotel_id, int) or hotel_id <= 0:
            return {"error": "El parámetro 'hotel_id' debe ser un número entero positivo."}

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarHotelPorId>
                 <tem:id>{hotel_id}</tem:id>
              </tem:seleccionarHotelPorId>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarHotelPorId",
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
        result_node = root.find(".//tem:seleccionarHotelPorIdResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarHotelPorIdResult' en la respuesta SOAP.")
            return {"exito": False, "hotel": None, "mensaje": "No se encontró información del hotel."}

        # ======================================================
        # Extraer datos del hotel
        # ======================================================
        hotel = {
            "Id": int(result_node.findtext("tem:Id", default="0", namespaces=ns)),
            "Nombre": result_node.findtext("tem:Nombre", default="", namespaces=ns),
            "FechaRegistro": result_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
            "UltimaFechaCambio": result_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
            "EsActivo": result_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
        }

        logger.info(f"Hotel obtenido correctamente: {hotel['Nombre']}")
        return {"exito": True, "hotel": hotel, "mensaje": "Hotel obtenido correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarHotelPorId(): {ex}")
        return {"error": str(ex)}


# ======================================================
# FUNCIÓN: seleccionarHoteles
# ======================================================
def seleccionarHoteles() -> dict:
    """
    Obtiene todos los hoteles activos usando WS_GestionHotel.asmx.

    Retorna:
        dict:
            {
                "exito": bool,
                "hoteles": [ {...}, {...} ],
                "mensaje": str
            }
        o en caso de error:
            {"error": str, "detalle"?: str}
    """
    try:
        logger.info("Consultando todos los hoteles activos...")

        # ======================================================
        # Construcción del envelope SOAP (SOAP 1.1)
        # ======================================================
        soap_body = """<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                          xmlns:tem="http://tempuri.org/">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:seleccionarHoteles/>
           </soapenv:Body>
        </soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://tempuri.org/seleccionarHoteles",
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
        result_node = root.find(".//tem:seleccionarHotelesResult", ns)

        if result_node is None:
            logger.warning("No se encontró el nodo 'seleccionarHotelesResult' en la respuesta SOAP.")
            return {"exito": False, "hoteles": [], "mensaje": "No se encontraron hoteles activos."}

        # ======================================================
        # Recorrer los nodos <Hotel>
        # ======================================================
        hoteles = []
        for hotel_node in result_node.findall("tem:Hotel", ns):
            try:
                hotel = {
                    "Id": int(hotel_node.findtext("tem:Id", default="0", namespaces=ns)),
                    "Nombre": hotel_node.findtext("tem:Nombre", default="", namespaces=ns),
                    "FechaRegistro": hotel_node.findtext("tem:FechaRegistro", default="", namespaces=ns),
                    "UltimaFechaCambio": hotel_node.findtext("tem:UltimaFechaCambio", default="", namespaces=ns),
                    "EsActivo": hotel_node.findtext("tem:EsActivo", default="false", namespaces=ns).lower() == "true",
                }
                hoteles.append(hotel)
            except Exception as parse_err:
                logger.warning(f"Error al procesar un nodo <Hotel>: {parse_err}")

        if not hoteles:
            logger.info("No se encontraron hoteles activos en la respuesta.")
            return {"exito": True, "hoteles": [], "mensaje": "No hay hoteles registrados o activos."}

        logger.info(f"Se encontraron {len(hoteles)} hoteles activos.")
        return {"exito": True, "hoteles": hoteles, "mensaje": "Hoteles obtenidos correctamente."}

    except Exception as ex:
        logger.error(f"Error en seleccionarHoteles(): {ex}")
        return {"error": str(ex)}