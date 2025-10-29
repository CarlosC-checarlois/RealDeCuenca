import uuid

from django.views.generic import TemplateView
from django.http import JsonResponse
from datetime import datetime
import hashlib
import datetime
import logging
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from webapp.servicios.wsUsuarios.wsUsuarios import insertarUsuario
from webapp.servicios.wsIntegracionDetalleServicios import wsIntegracionDetalleServicios as ws
from django.views import View
from django.shortcuts import render, redirect
from django.http import Http404
from decimal import Decimal
from django.http import JsonResponse
from django.contrib import messages
from webapp.servicios.wsUsuarios import wsUsuarios
from django.http import JsonResponse
from webapp.servicios.wsReservas.wsReservas import *
from webapp.servicios.wsPagos import wsPagos
logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_exempt
import json
from webapp.servicios.wsUsuarios.wsUsuarios import insertarUsuario
from webapp.servicios.wsPoliticas.wsPoliticas import seleccionarPoliticas, insertarPolitica, actualizarPolitica, eliminarPolitica

# ===============================
# 🔹 SECCIÓN: INICIO
# ===============================
class HomeView(TemplateView):
    template_name = "webapp/inicio/index.html"

# ===============================
# 🔹 SECCIÓN: AUTENTIFICACIÓN
# ===============================

# ===============================
# 🔹 SECCIÓN: LOGIN
# ===============================
class LoginView(TemplateView):
    template_name = "webapp/autentificacion/login.html"
# ===============================
# 🔹 SECCIÓN: REGISTRO
# ===============================

class RegisterView(TemplateView):
    template_name = "webapp/autentificacion/register.html"

# ===============================
# 🔹 SECCIÓN: SERVICIOS
# ===============================
class ServiciosView(View):
    template_name = "webapp/servicios/servicios.html"

    def get(self, request):
        try:
            ubicaciones = ws.obtenerUbicaciones() if hasattr(ws, "obtenerUbicaciones") else []
            hoteles = ws.obtenerHoteles() if hasattr(ws, "obtenerHoteles") else []
        except Exception as e:
            logger.error(f"Error al obtener datos SOAP: {e}")
            ubicaciones, hoteles = [], []

        context = {
            "ubicaciones": ubicaciones,
            "hoteles": hoteles,
            "usuario_id": request.session.get("usuario_id"),
            "token_sesion": request.session.session_key or "anon-" + str(uuid.uuid4())
        }
        return render(request, self.template_name, context)

class CargarEspaciosView(View):
    """
    Endpoint AJAX que devuelve los espacios según los filtros aplicados.
    Si no hay filtros válidos, ejecuta seleccionarEspaciosDetalladosPorPaginas().
    Si existen filtros reales, utiliza buscarServicios().
    """

    def get(self, request):
        try:
            pagina = int(request.GET.get("pagina", 1))
            tamano_pagina = int(request.GET.get("tamanoPagina", 5))

            # Extraer filtros y limpiar valores vacíos
            ubicacion = (request.GET.get("ubicacion") or "").strip()
            hotel = (request.GET.get("hotel") or "").strip()
            fecha_inicio = (request.GET.get("fechaInicio") or "").strip()
            fecha_fin = (request.GET.get("fechaFin") or "").strip()
            puntuacion = (request.GET.get("puntuacion") or "").strip()
            if (fecha_inicio and not fecha_fin) or (fecha_fin and not fecha_inicio):
                return JsonResponse({
                    "success": False,
                    "error": "Debe seleccionar tanto fecha de inicio como fecha de fin."
                })

            # Detectar si hay filtros válidos (no vacíos, no placeholders)
            filtros_validos = any([
                ubicacion not in ("", "Ubicaciones", "null", None),
                hotel not in ("", "Hoteles", "Tipo de Hotel", "null", None),
                fecha_inicio not in ("", "null", None),
                fecha_fin not in ("", "null", None),
                puntuacion not in ("", "null", None),
            ])

            # Elegir el servicio según haya filtros o no
            if filtros_validos:
                logger.info("➡️ Ejecutando buscarServicios() con filtros aplicados.")
                resultado = ws.buscarServicios(
                    ubicacion=ubicacion or None,
                    hotel=hotel or None,
                    fechaInicio=fecha_inicio or None,
                    fechaFin=fecha_fin or None,
                    puntuacion=int(puntuacion) if puntuacion.isdigit() else None,
                    pagina=pagina,
                    tamanoPagina=tamano_pagina
                )
                origen = "buscarServicios"
            else:
                logger.info("➡️ Ejecutando seleccionarEspaciosDetalladosPorPaginas() sin filtros.")
                resultado = ws.seleccionarEspaciosDetalladosPorPaginas(
                    pagina=pagina,
                    tamanoPagina=tamano_pagina
                )
                origen = "seleccionarEspaciosDetalladosPorPaginas"

            # Validar tipo del resultado
            if not isinstance(resultado, dict):
                logger.error(f"Respuesta inesperada desde {origen}: tipo {type(resultado)}")
                return JsonResponse({
                    "success": False,
                    "error": f"Respuesta inesperada del servicio: {str(resultado)[:500]}"
                })

            if "error" in resultado:
                logger.error(f"Error en {origen}: {resultado['error']}")
                return JsonResponse({"success": False, "error": resultado["error"]})

            # Normalizar datos
            datos = resultado.get("Datos", []) or []
            for e in datos:
                imagenes = e.get("Imagenes", [])
                if isinstance(imagenes, list) and imagenes:
                    e["ImagenPrincipal"] = (
                        imagenes[0] if isinstance(imagenes[0], str)
                        else imagenes[0].get("Url", "")
                    )
                else:
                    e["ImagenPrincipal"] = "https://imageness3realdecuenca.s3.us-east-2.amazonaws.com/Imagen5.png"

                try:
                    e["CostoDiario"] = float(e.get("CostoDiario", 0) or 0)
                except (ValueError, TypeError):
                    e["CostoDiario"] = 0.0

            total = resultado.get("TotalRegistros", len(datos))
            logger.info(f"{origen} devolvió {len(datos)} registros (total: {total}).")

            return JsonResponse({
                "success": True,
                "datos": datos,
                "total": resultado.get("TotalRegistros", len(datos)),
                "carrito_metadata": {
                    "usuario_id": request.session.get("usuario_id"),
                    "token_sesion": request.session.session_key or "anon-" + str(uuid.uuid4())
                }
            })

        except Exception as ex:
            logger.error(f"Error en CargarEspaciosView: {ex}")
            return JsonResponse({"success": False, "error": str(ex)})

class ServiciosDetalleView(TemplateView):
    template_name = "webapp/servicios/serviciosDetalle.html"

    def get(self, request, id):
        try:
            espacio = ws.obtenerDetalleServicio(id)
            if not espacio:
                raise Http404("El servicio solicitado no fue encontrado.")

            # 🧩 Normalizar estructuras complejas
            def normalizar_campo(obj):
                if isinstance(obj, dict) and "string" in obj:
                    return obj["string"]
                elif isinstance(obj, list):
                    return obj
                return []

            espacio["Politicas"] = normalizar_campo(espacio.get("Politicas"))
            espacio["Imagenes"] = normalizar_campo(espacio.get("Imagenes"))
            espacio["Amenidades"] = normalizar_campo(espacio.get("Amenidades"))

            # 🧩 Imagen principal
            espacio["ImagenPrincipal"] = (
                espacio["Imagenes"][0]
                if espacio["Imagenes"]
                else "https://imageness3realdecuenca.s3.us-east-2.amazonaws.com/Imagen5.png"
            )

            # 🧩 Normalizar tipo de datos
            from decimal import Decimal
            espacio["Moneda"] = espacio.get("Moneda") or "$"
            costo = espacio.get("CostoDiario", 0)
            espacio["CostoDiario"] = float(costo) if isinstance(costo, Decimal) else costo

            # 🧠 Recomendados
            recomendados = []
            try:
                resp = ws.buscarServicios(
                    ubicacion=espacio.get("Ubicacion"),
                    pagina=1,
                    tamanoPagina=3
                )
                if isinstance(resp, dict):
                    recomendados = resp.get("Datos", [])
                    # Asignar imagen principal a cada recomendado
                    for r in recomendados:
                        imgs = r.get("Imagenes", [])
                        if isinstance(imgs, dict) and "string" in imgs:
                            imgs = imgs["string"]
                        r["ImagenPrincipal"] = imgs[0] if imgs else "https://imageness3realdecuenca.s3.us-east-2.amazonaws.com/Imagen5.png"
            except Exception as suberr:
                logger.warning(f"No se pudieron obtener recomendados: {suberr}")

            context = {
                "espacio": espacio,
                "recomendados": recomendados,
                "usuario_id": request.session.get("usuario_id"),
                "token_sesion": request.session.session_key or "anon-" + str(uuid.uuid4())
            }
            return render(request, self.template_name, context)


        except Http404:
            raise
        except Exception as e:
            logger.error(f"Error al cargar el detalle del servicio {id}: {e}")
            raise Http404("Ocurrió un error al cargar el detalle del servicio.")

# ===============================
# 🔹 SECCIÓN: CARRITO
# ===============================
class CarritoView(TemplateView):
    template_name = "webapp/carrito/carrito.html"

# webapp/views.py

class ServiciosDetalleJsonView(View):
    def get(self, request, id):
        try:
            espacio = ws.obtenerDetalleServicio(id)
            if not espacio:
                return JsonResponse({"success": False, "error": "No encontrado"})
            return JsonResponse({"success": True, "espacio": espacio})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

class CarritoDetalleView(TemplateView):
    template_name = "webapp/carrito/carrito_detalle.html"


class CarritoDetalleViewLocalStorage(TemplateView):
    """
    Vista de carrito simulada con LocalStorage
    - GET: Renderiza la página del carrito.
    - POST: Recibe datos JSON del navegador.
    """
    template_name = "webapp/carrito/carrito_detalle.html"

    def post(self, request, *args, **kwargs):
        data = request.POST.get("productos", "[]")
        return JsonResponse({"status": "ok", "received": data})

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CarritoDetalleViewVerificarDisponibilidad(TemplateView):
    """
    Simula una verificación de disponibilidad de un servicio o producto
    por rango de fechas.
    """
    template_name = "webapp/carrito/carrito_detalle.html"

    def get(self, request, *args, **kwargs):
        fecha_inicio = request.GET.get("fechaInicio")
        fecha_fin = request.GET.get("fechaFin")

        disponible = True
        if fecha_inicio and fecha_fin:
            try:
                fi = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                ff = datetime.strptime(fecha_fin, "%Y-%m-%d")
                if fi > ff:
                    disponible = False
            except ValueError:
                return JsonResponse({"error": "Formato de fecha inválido"}, status=400)

        return JsonResponse({
            "disponible": disponible,
            "fechaInicio": fecha_inicio,
            "fechaFin": fecha_fin
        })


# ===============================
# 🔹 SECCIÓN: ERROR / AUXILIARES
# ===============================
class Error404View(TemplateView):
    template_name = "webapp/errores/404.html"


class Error500View(TemplateView):
    template_name = "webapp/errores/500.html"


# ===============================
# 🔹 APIS NECESARIAS
# ===============================
def verificar_disponibilidad(request):
    """
    Endpoint AJAX para validar la disponibilidad de un espacio.
    """
    try:
        espacio_id = int(request.GET.get("espacioId"))
        fecha_inicio = request.GET.get("fechaInicio")
        fecha_fin = request.GET.get("fechaFin")

        if not all([espacio_id, fecha_inicio, fecha_fin]):
            return JsonResponse({"success": False, "error": "Faltan parámetros requeridos."})

        # Llamar al método del WS
        resultado = ws.verificarDisponibilidad(espacio_id, fecha_inicio, fecha_fin)

        if "error" in resultado:
            return JsonResponse({"success": False, "error": resultado["error"]})

        return JsonResponse({
            "success": True,
            "espacioId": resultado["espacioId"],
            "disponible": resultado["disponible"]
        })
    except Exception as ex:
        logger.error(f"Error al verificar disponibilidad: {ex}")
        return JsonResponse({"success": False, "error": str(ex)})



class LoginAPIView(View):
    def post(self, request, *args, **kwargs):

        email = request.POST.get("correo")
        password = request.POST.get("contrasena")

        if not email or not password:
            return JsonResponse({"success": False, "error": "Por favor completa todos los campos."})

        resultado = wsUsuarios.iniciarSesion(email, password)

        if "error" in resultado:
            return JsonResponse({"success": False, "error": resultado["error"]})
        print("Inicio de sesion correcto")
        return JsonResponse({
            "success": True,
            "usuario": {
                "Id": resultado.get("Id"),
                "Nombre": resultado.get("Nombre"),
                "Email": resultado.get("Email"),
                "Rol": resultado.get("Rol")
            }
        })

@csrf_exempt
def api_register(request):
    """
    🧾 Registro de usuario usando el servicio SOAP (insertarUsuario)
    Envío directo de la contraseña en texto plano.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido."}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        nombre = data.get("nombre", "").strip()
        email = data.get("correo", "").strip().lower()
        contrasena = data.get("contrasena", "").strip()

        if not nombre or not email or not contrasena:
            return JsonResponse({"success": False, "error": "Todos los campos son obligatorios."}, status=400)

        ahora_iso = datetime.datetime.now().isoformat()

        # 🔑 Contraseña sin hash, texto plano
        usuario_data = {
            "Id": 0,
            "Nombre": nombre,
            "Email": email,
            "PasswordHash": contrasena,  # 👈 sin SHA, se envía tal cual
            "Rol": "Usuario",
            "FechaRegistro": ahora_iso,
            "UltimaFechaCambio": ahora_iso,
            "EsActivo": True,
            "UltimaFechainicioSesion": ahora_iso
        }

        logger.info(f"🟢 Enviando registro SOAP (usuario={email})...")
        resultado = insertarUsuario(usuario_data)

        if "error" in resultado:
            return JsonResponse({"success": False, "error": resultado["error"]}, status=500)

        if not resultado.get("insertado", False):
            return JsonResponse({"success": False, "error": "No se pudo registrar el usuario."}, status=500)

        nuevo_id = resultado.get("nuevoId", 0)

        return JsonResponse({
            "success": True,
            "usuario": {
                "Id": nuevo_id,
                "Nombre": nombre,
                "Email": email,
                "Rol": "Usuario"
            },
            "mensaje": resultado.get("mensaje", "Usuario registrado correctamente.")
        })

    except Exception as ex:
        logger.error(f"❌ Error en api_register: {ex}")
        return JsonResponse({"success": False, "error": str(ex)}, status=500)

class ReservasView(TemplateView):
    """
    Vista principal para mostrar reservas del usuario (SOAP + carrito local).
    El frontend usa AJAX para obtener los datos del WS.
    """
    template_name = "webapp/reservas/reservas.html"

    def get_context_data(self, **kwargs):
        """
        Renderiza solo la estructura inicial; el JS se encarga de cargar las reservas.
        """
        context = super().get_context_data(**kwargs)
        context.update({
            "reservas": [],
            "total_reservas": 0,
            "mensaje": ""
        })
        return context


def api_reservas_por_usuario(request, usuario_id: int):
    """
    API JSON que retorna las reservas de un usuario consultando el WS SOAP.
    """
    try:
        if not usuario_id or int(usuario_id) <= 0:
            logger.warning("Intento de consulta con ID de usuario inválido.")
            return JsonResponse(
                {"error": "El ID de usuario proporcionado no es válido."},
                status=400
            )

        logger.info(f"Solicitud de reservas para usuario ID={usuario_id}")
        resultado = seleccionarReservasPorUsuario(int(usuario_id))

        # Validar errores del WS
        if "error" in resultado:
            logger.error(f"Error en WS seleccionarReservasPorUsuario: {resultado['error']}")
            return JsonResponse(
                {"error": "No se pudieron obtener las reservas.", "detalle": resultado["error"]},
                status=502
            )

        # Respuesta exitosa
        logger.info(f"Reservas obtenidas correctamente ({resultado.get('total', 0)} registros)")
        return JsonResponse(resultado, status=200)

    except Exception as ex:
        logger.exception(f"Error general en api_reservas_por_usuario(): {ex}")
        return JsonResponse({"error": str(ex)}, status=500)





class PagosView(TemplateView):
    """
    Vista principal para la página /pago/
    El frontend carga los pagos desde el servicio SOAP usando fetch() → /api/pagos/<usuario_id>/
    """
    template_name = "webapp/pagos/pagos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "pagos": [],
            "total_pagos": 0,
            "mensaje": "",
        })
        return context


def api_pagos_por_usuario(request, usuario_id: int):
    """
    API JSON que obtiene los pagos del usuario desde el WS SOAP (obtenerPagosPorUsuario).
    """
    try:
        if not usuario_id or int(usuario_id) <= 0:
            return JsonResponse({"error": "ID de usuario inválido."}, status=400)

        logger.info(f"Consultando pagos del usuario ID={usuario_id} en WS_GestionPagos")

        resultado = wsPagos.obtenerPagosPorUsuario(usuarioId=int(usuario_id))

        # Validar errores
        if "error" in resultado:
            logger.error(f"Error al obtener pagos: {resultado['error']}")
            return JsonResponse(
                {"error": "No se pudieron obtener los pagos.", "detalle": resultado["error"]},
                status=502
            )

        pagos = resultado.get("pagos", [])
        logger.info(f"Se encontraron {len(pagos)} pagos para el usuario {usuario_id}")

        return JsonResponse({
            "exito": True,
            "pagos": pagos,
            "mensaje": resultado.get("mensaje", "Pagos obtenidos correctamente."),
            "total": len(pagos)
        })

    except Exception as ex:
        logger.exception(f"Error general en api_pagos_por_usuario(): {ex}")
        return JsonResponse({"error": str(ex)}, status=500)


class UsuarioDetalleView(TemplateView):
    """
    Muestra la página del perfil del usuario.
    """
    template_name = "webapp/usuario/perfil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario"] = {}
        return context


def api_usuario_por_id(request, usuario_id: int):
    """
    API que consulta la información del usuario desde el WS SOAP.
    """
    try:
        if not usuario_id or int(usuario_id) <= 0:
            return JsonResponse({"error": "ID de usuario inválido."}, status=400)

        logger.info(f"Consultando datos del usuario con ID={usuario_id}")

        resultado = wsUsuarios.seleccionarPorId(int(usuario_id))

        if "error" in resultado:
            return JsonResponse({"error": resultado["error"]}, status=502)

        return JsonResponse({"exito": True, "usuario": resultado})

    except Exception as ex:
        logger.exception("Error al obtener datos del usuario")
        return JsonResponse({"error": str(ex)}, status=500)


"""
--------------------------------------------------
APIS
--------------------------------------------------
"""
from django.http import JsonResponse
from webapp.servicios.wsEspXRes.wsEspXRes import seleccionarPorReserva
from webapp.servicios.wsPagos.wsPagos import seleccionarPagosPorReserva
from webapp.servicios.wsIntegracionDetalleServicios.wsIntegracionDetalleServicios import obtenerDetalleServicio, \
    crearPreReserva


def api_detalles_reserva(request, reserva_id):
    """Devuelve relaciones + detalles de los espacios para una reserva."""
    try:
        data = seleccionarPorReserva(reserva_id)

        if data.get("error"):
            return JsonResponse({"error": data["error"]}, status=400)

        relaciones = data.get("relaciones", [])
        detalles_completos = []

        # Enriquecer cada relación con los datos del espacio
        for rel in relaciones:
            espacio_id = rel.get("EspacioId")
            detalle_espacio = obtenerDetalleServicio(espacio_id) if espacio_id else {}
            detalles_completos.append({
                "Id": rel.get("Id"),
                "FechaInicio": rel.get("FechaInicio"),
                "FechaFin": rel.get("FechaFin"),
                "CostoCalculado": rel.get("CostoCalculado"),
                "EspacioId": espacio_id,
                "FechaRegistro": rel.get("FechaRegistro"),
                "EsBloqueada": rel.get("EsBloqueada"),
                "Espacio": detalle_espacio
            })

        return JsonResponse({
            "relaciones": detalles_completos,
            "mensaje": data.get("mensaje", "Relaciones obtenidas correctamente.")
        })
    except Exception as ex:
        return JsonResponse({"error": str(ex)}, status=500)


def api_pagos_reserva(request, reserva_id):
    """Devuelve los pagos asociados a una reserva."""
    try:
        data = seleccionarPagosPorReserva(reserva_id)
        if data.get("error"):
            return JsonResponse({"error": data["error"]}, status=400)
        return JsonResponse(data)
    except Exception as ex:
        return JsonResponse({"error": str(ex)}, status=500)


@csrf_exempt
def api_pre_reserva(request):
    """
    Endpoint: /api/reservas/precrear/
    Crea una pre-reserva (bloqueo temporal de espacios) usando el servicio SOAP.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        lista_espacios = body.get("ListaEspacios", [])
        usuario_id = body.get("UsuarioId")
        usuario_ext = body.get("UsuarioExternoId")
        fecha_inicio = body.get("FechaInicio")
        fecha_fin = body.get("FechaFinal")
        comentarios = body.get("Comentarios", "")

        logger.info(f"Solicitud de pre-reserva recibida: usuario={usuario_id}, espacios={lista_espacios}")

        resultado = crearPreReserva(
            listaEspacios=lista_espacios,
            usuarioId=usuario_id,
            usuarioExternoId=usuario_ext,
            fechaInicio=fecha_inicio,
            fechaFin=fecha_fin,
            comentarios=comentarios
        )

        if "error" in resultado:
            return JsonResponse(resultado, status=400)
        return JsonResponse(resultado)

    except Exception as ex:
        logger.exception("Error en api_pre_reserva:")
        return JsonResponse({"error": str(ex)}, status=500)

@csrf_exempt
def api_confirmar_reserva(request):
    """
    Endpoint: POST /api/reservas/confirmar/
    Llama a confirmarReserva() del backend SOAP y retorna JSON.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido."}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        reserva_id = body.get("ReservaId")
        datos_pago = body.get("DatosPago", "")
        monto = body.get("Monto")

        if not reserva_id:
            return JsonResponse({"error": "Falta el ID de la reserva."}, status=400)

        resultado = ws.confirmarReserva(
            reservaId=reserva_id,
            pagoId=None,  # El procedure lo genera
            datosPago=datos_pago,
            monto=monto
        )
        return JsonResponse(resultado)

    except Exception as ex:
        return JsonResponse({"error": str(ex)}, status=500)

class DashboardView(View):
    """Vista principal del panel administrativo con accesos a los CRUDs."""

    def get(self, request, *args, **kwargs):
        # Puedes validar aquí que sea admin antes de mostrar
        return render(request, "webapp/dashboard/dashboard.html")


class PoliticasDashboardView(View):
    """Vista del CRUD de Políticas en el panel admin."""

    def get(self, request, *args, **kwargs):
        return render(request, "webapp/dashboard/politicas.html")



# ========================================================
#  GET → Seleccionar todas las políticas
# ========================================================
@require_http_methods(["GET"])
def api_seleccionar_politicas(request):
    try:
        logger.info("Consultando todas las políticas...")
        respuesta = seleccionarPoliticas()
        return JsonResponse({
            "exito": True,
            "politicas": respuesta.get("politicas", [])
        })
    except Exception as e:
        logger.exception("Error al consultar políticas: %s", e)
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ========================================================
#  POST → Insertar nueva política
# ========================================================
@csrf_exempt
@require_http_methods(["POST"])
def api_insertar_politica(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
        politica = {
            "DescripcionPolitica": body.get("DescripcionPolitica"),
            "FechaRegistro": body.get("FechaRegistro"),
            "UltimaFechaCambio": body.get("UltimaFechaCambio"),
            "EsActivo": body.get("EsActivo", True)
        }
        logger.info("Insertando nueva política: %s", politica)
        resultado = insertarPolitica(politica)
        return JsonResponse(resultado)
    except Exception as e:
        logger.exception("Error al insertar política: %s", e)
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ========================================================
#  PUT → Actualizar política existente
# ========================================================
@csrf_exempt
@require_http_methods(["PUT"])
def api_actualizar_politica(request, id):
    try:
        body = json.loads(request.body.decode("utf-8"))
        politica = {
            "Id": id,
            "DescripcionPolitica": body.get("DescripcionPolitica"),
            "UltimaFechaCambio": body.get("UltimaFechaCambio"),
            "EsActivo": body.get("EsActivo", True)
        }
        logger.info("Actualizando política ID=%s", id)
        resultado = actualizarPolitica(politica)
        return JsonResponse(resultado)
    except Exception as e:
        logger.exception("Error al actualizar política: %s", e)
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ========================================================
#  DELETE → Eliminar política
# ========================================================
@csrf_exempt
@require_http_methods(["DELETE"])
def api_eliminar_politica(request, id):
    try:
        logger.info("Eliminando política ID=%s", id)
        resultado = eliminarPolitica({"Id": id})
        return JsonResponse(resultado)
    except Exception as e:
        logger.exception("Error al eliminar política: %s", e)
        return JsonResponse({"exito": False, "error": str(e)}, status=500)
class UsuariosDashboardView(View):
    """Vista del CRUD de Usuarios en el panel admin."""

    def get(self, request, *args, **kwargs):
        return render(request, "webapp/dashboard/usuarios.html")


import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webapp.servicios.wsUsuarios.wsUsuarios import (
    seleccionarUsuarios,
    insertarUsuario,
    actualizarUsuario,
    eliminarUsuario,
)

logger = logging.getLogger(__name__)

# ==========================================================
# GET → Listar todos los usuarios
# ==========================================================
@require_http_methods(["GET"])
def api_usuarios_listar(request):
    try:
        datos = seleccionarUsuarios()
        if "error" in datos:
            raise Exception(datos["error"])
        return JsonResponse({"exito": True, "usuarios": datos.get("usuarios", [])})
    except Exception as e:
        logger.error(f"Error al listar usuarios: {e}")
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ==========================================================
# POST → Insertar nuevo usuario
# ==========================================================
@csrf_exempt
@require_http_methods(["POST"])
def api_usuarios_insertar(request):
    try:
        body = json.loads(request.body)
        resultado = insertarUsuario(body)
        return JsonResponse(resultado)
    except Exception as e:
        logger.error(f"Error al insertar usuario: {e}")
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ==========================================================
# PUT → Actualizar usuario
# ==========================================================
@csrf_exempt
@require_http_methods(["PUT"])
def api_usuarios_actualizar(request, id):
    try:
        body = json.loads(request.body)
        body["Id"] = id
        resultado = actualizarUsuario(body)
        return JsonResponse(resultado)
    except Exception as e:
        logger.error(f"Error al actualizar usuario: {e}")
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ==========================================================
# DELETE → Eliminar usuario
# ==========================================================
@csrf_exempt
@require_http_methods(["DELETE"])
def api_usuarios_eliminar(request, id):
    try:
        resultado = eliminarUsuario(id)
        return JsonResponse(resultado)
    except Exception as e:
        logger.error(f"Error al eliminar usuario: {e}")
        return JsonResponse({"exito": False, "error": str(e)}, status=500)





class ReservasDashboardView(View):
    """Vista para el panel de gestión de reservas."""
    def get(self, request, *args, **kwargs):
        return render(request, "webapp/dashboard/reservas.html")



import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from webapp.servicios.wsReservas.wsReservas import (
    seleccionarReservas,
    insertarReserva,
    actualizarReserva,
    eliminarReserva,
)

logger = logging.getLogger(__name__)

# ==========================================================
# GET → Listar reservas
# ==========================================================
@require_http_methods(["GET"])
def api_reservas_listar(request):
    try:
        datos = seleccionarReservas()
        if "error" in datos:
            raise Exception(datos["error"])
        return JsonResponse({"exito": True, "reservas": datos.get("reservas", [])})
    except Exception as e:
        logger.error(f"Error al listar reservas: {e}")
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ==========================================================
# POST → Insertar nueva reserva
# ==========================================================
@csrf_exempt
@require_http_methods(["POST"])
def api_reservas_insertar(request):
    try:
        body = json.loads(request.body)
        resultado = insertarReserva(body)
        return JsonResponse(resultado)
    except Exception as e:
        logger.error(f"Error al insertar reserva: {e}")
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ==========================================================
# PUT → Actualizar reserva
# ==========================================================
@csrf_exempt
@require_http_methods(["PUT"])
def api_reservas_actualizar(request, id):
    try:
        body = json.loads(request.body)
        body["Id"] = id
        resultado = actualizarReserva(body)
        return JsonResponse(resultado)
    except Exception as e:
        logger.error(f"Error al actualizar reserva: {e}")
        return JsonResponse({"exito": False, "error": str(e)}, status=500)

# ==========================================================
# DELETE → Eliminar reserva
# ==========================================================
@csrf_exempt
@require_http_methods(["DELETE"])
def api_reservas_eliminar(request, id):
    try:
        resultado = eliminarReserva(id)
        return JsonResponse(resultado)
    except Exception as e:
        logger.error(f"Error al eliminar reserva: {e}")
        return JsonResponse({"exito": False, "error": str(e)}, status=500)



import json
import logging
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from webapp.servicios.wsEspacios.wsEspacios import (
    insertarEspacio,
    actualizarEspacio,
    eliminarEspacio,
    seleccionarEspacios,
)

logger = logging.getLogger(__name__)


# ======================================================
# DASHBOARD VIEW: Espacios
# ======================================================
class EspaciosDashboardView(View):
    """
    Renderiza el panel del dashboard para la gestión de espacios.
    """
    template_name = "webapp/dashboard/espacios.html"

    def get(self, request):
        logger.info("Cargando vista de dashboard para ESPACIOS.")
        return render(request, self.template_name)


# ======================================================
# API - LISTAR ESPACIOS
# ======================================================
def api_espacios_listar(request):
    """
    Obtiene todos los espacios activos mediante el servicio SOAP.
    URL: /api/espacios/
    Método: GET
    """
    if request.method != "GET":
        return JsonResponse({"exito": False, "mensaje": "Método no permitido."}, status=405)

    try:
        logger.info("Consultando lista de espacios activos...")
        resultado = seleccionarEspacios()
        return JsonResponse(resultado)
    except Exception as ex:
        logger.error(f"Error en api_espacios_listar(): {ex}")
        return JsonResponse({"exito": False, "mensaje": str(ex)})


# ======================================================
# API - INSERTAR ESPACIO
# ======================================================
def api_espacios_insertar(request):
    """
    Inserta un nuevo espacio usando el servicio SOAP.
    URL: /api/espacios/
    Método: POST
    """
    if request.method != "POST":
        return JsonResponse({"exito": False, "mensaje": "Método no permitido."}, status=405)

    try:
        datos = json.loads(request.body)
        logger.info(f"Insertando nuevo espacio: {datos.get('Nombre')}")
        resultado = insertarEspacio(datos)
        return JsonResponse(resultado)
    except Exception as ex:
        logger.error(f"Error en api_espacios_insertar(): {ex}")
        return JsonResponse({"exito": False, "mensaje": str(ex)})


# ======================================================
# API - ACTUALIZAR ESPACIO
# ======================================================
def api_espacios_actualizar(request, id):
    """
    Actualiza un espacio existente.
    URL: /api/espacios/<id>/
    Método: PUT
    """
    if request.method != "PUT":
        return JsonResponse({"exito": False, "mensaje": "Método no permitido."}, status=405)

    try:
        datos = json.loads(request.body)
        datos["Id"] = id
        logger.info(f"Actualizando espacio ID={id}")
        resultado = actualizarEspacio(datos)
        return JsonResponse(resultado)
    except Exception as ex:
        logger.error(f"Error en api_espacios_actualizar(): {ex}")
        return JsonResponse({"exito": False, "mensaje": str(ex)})


# ======================================================
# API - ELIMINAR ESPACIO
# ======================================================
def api_espacios_eliminar(request, id):
    """
    Elimina un espacio (soft delete) mediante SOAP.
    URL: /api/espacios/<id>/
    Método: DELETE
    """
    if request.method != "DELETE":
        return JsonResponse({"exito": False, "mensaje": "Método no permitido."}, status=405)

    try:
        logger.info(f"Eliminando espacio ID={id}")
        resultado = eliminarEspacio(id)
        return JsonResponse(resultado)
    except Exception as ex:
        logger.error(f"Error en api_espacios_eliminar(): {ex}")
        return JsonResponse({"exito": False, "mensaje": str(ex)})
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View

# Importamos el servicio SOAP
from webapp.servicios.wsPagos.wsPagos import (
    seleccionarPagos,
    insertarPago,
    actualizarPago,
    eliminarPago,
)

logger = logging.getLogger(__name__)


# ======================================================
# DASHBOARD - PAGOS
# ======================================================
class PagosDashboardView(View):
    template_name = "webapp/dashboard/pagos.html"

    def get(self, request):
        logger.info("Renderizando vista de Dashboard para Pagos...")
        return render(request, self.template_name)


# ======================================================
# API - LISTAR PAGOS
# ======================================================
def api_pagos_listar(request):
    if request.method != "GET":
        return JsonResponse({"exito": False, "mensaje": "Método no permitido."}, status=405)
    try:
        logger.info("Consultando lista de pagos desde WS_GestionPagos...")
        resultado = seleccionarPagos()

        if "error" in resultado:
            return JsonResponse({"exito": False, "mensaje": resultado["error"]})

        return JsonResponse({"exito": True, "pagos": resultado.get("pagos", []), "mensaje": resultado.get("mensaje", "")})
    except Exception as ex:
        logger.error(f"Error en api_pagos_listar(): {ex}")
        return JsonResponse({"exito": False, "mensaje": str(ex)})


# ======================================================
# API - INSERTAR PAGO
# ======================================================
def api_pagos_insertar(request):
    if request.method != "POST":
        return JsonResponse({"exito": False, "mensaje": "Método no permitido."}, status=405)

    try:
        datos = json.loads(request.body)
        logger.info(f"Insertando nuevo pago: {datos.get('TransaccionReferencia')}")
        resultado = insertarPago(datos)

        if "error" in resultado:
            return JsonResponse({"exito": False, "mensaje": resultado["error"]})

        return JsonResponse({"exito": True, "mensaje": resultado.get("mensaje", "Pago insertado correctamente.")})
    except Exception as ex:
        logger.error(f"Error en api_pagos_insertar(): {ex}")
        return JsonResponse({"exito": False, "mensaje": str(ex)})


# ======================================================
# API - ACTUALIZAR PAGO
# ======================================================
def api_pagos_actualizar(request, id):
    if request.method != "PUT":
        return JsonResponse({"exito": False, "mensaje": "Método no permitido."}, status=405)
    try:
        datos = json.loads(request.body)
        datos["Id"] = id
        logger.info(f"Actualizando pago ID={id}")
        resultado = actualizarPago(datos)

        if "error" in resultado:
            return JsonResponse({"exito": False, "mensaje": resultado["error"]})

        return JsonResponse({"exito": True, "mensaje": resultado.get("mensaje", "Pago actualizado correctamente.")})
    except Exception as ex:
        logger.error(f"Error en api_pagos_actualizar(): {ex}")
        return JsonResponse({"exito": False, "mensaje": str(ex)})


# ======================================================
# API - ELIMINAR PAGO
# ======================================================
def api_pagos_eliminar(request, id):
    if request.method != "DELETE":
        return JsonResponse({"exito": False, "mensaje": "Método no permitido."}, status=405)
    try:
        logger.info(f"Eliminando pago ID={id}")
        resultado = eliminarPago(id)

        if "error" in resultado:
            return JsonResponse({"exito": False, "mensaje": resultado["error"]})

        return JsonResponse({"exito": True, "mensaje": resultado.get("mensaje", "Pago eliminado correctamente.")})
    except Exception as ex:
        logger.error(f"Error en api_pagos_eliminar(): {ex}")
        return JsonResponse({"exito": False, "mensaje": str(ex)})



