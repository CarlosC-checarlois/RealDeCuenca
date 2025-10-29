document.addEventListener("DOMContentLoaded", () => {
    const principal = document.querySelector(".img-principal_index_servicios");
    const miniaturas = document.querySelectorAll(".miniaturas_index_servicios img");

    miniaturas.forEach(miniatura => {
        miniatura.addEventListener("click", () => {
            // Remover la clase activa de todas las miniaturas
            miniaturas.forEach(img => img.classList.remove("activa_index_servicios"));

            // Agregar la clase activa a la miniatura seleccionada
            miniatura.classList.add("activa_index_servicios");

            // Efecto de transición en la imagen principal
            principal.style.opacity = "0";

            setTimeout(() => {
                // Cambiar la imagen principal
                principal.src = miniatura.dataset.full;
                // Reaparecer con efecto
                principal.style.opacity = "1";
            }, 250);
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const btnReservar = document.querySelector(".btn-reservar_index_servicios");
    const modal = new bootstrap.Modal(document.getElementById("modalReserva_index_servicios"));

    btnReservar.addEventListener("click", () => {
        const fechaInicio = localStorage.getItem("fechaInicio") || "2025-10-14";
        const fechaFin = localStorage.getItem("fechaFin") || "2025-10-17";
        const precioDiario = parseFloat(document.getElementById("precioDiario_index_servicios").textContent);

        const dias = calcularDias(fechaInicio, fechaFin);
        const total = dias * precioDiario;

        document.getElementById("fechaInicio_index_servicios").textContent = formatearFecha(fechaInicio);
        document.getElementById("fechaFin_index_servicios").textContent = formatearFecha(fechaFin);
        document.getElementById("diasReserva_index_servicios").textContent = dias;
        document.getElementById("totalReserva_index_servicios").textContent = total.toFixed(2);

        modal.show();
    });

    function calcularDias(inicio, fin) {
        const d1 = new Date(inicio);
        const d2 = new Date(fin);
        const diff = Math.abs(d2 - d1);
        return Math.max(1, Math.ceil(diff / (1000 * 60 * 60 * 24)));
    }

    function formatearFecha(fecha) {
        const d = new Date(fecha);
        return d.toLocaleDateString("es-ES", {year: "numeric", month: "long", day: "numeric"});
    }

    document.getElementById("btnConfirmarReserva_index_servicios").addEventListener("click", () => {
        modal.hide();
        Swal.fire({
            title: "✅ ¡Reserva confirmada!",
            text: "Tu reserva fue guardada con exito, procede ir al carrito de compras",
            icon: "success",
            confirmButtonColor: "#FFD700",
            confirmButtonText: "Aceptar"
        });
    });
});