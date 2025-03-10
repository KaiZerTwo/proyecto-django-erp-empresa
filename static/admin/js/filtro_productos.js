document.addEventListener("DOMContentLoaded", function () {
    function actualizarProductos() {
        let proveedorSelect = document.querySelector("#id_proveedor");
        let productoSelects = document.querySelectorAll("select[name$='-producto']");

        if (!proveedorSelect || !productoSelects.length) {
            return;
        }

        let proveedorId = proveedorSelect.value;
        productoSelects.forEach(function (productoSelect) {
            let url = `/admin/obtener_productos/?proveedor_id=${proveedorId}`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    productoSelect.innerHTML = "";
                    data.forEach(function (producto) {
                        let option = document.createElement("option");
                        option.value = producto.id;
                        option.textContent = producto.nombre;
                        productoSelect.appendChild(option);
                    });
                })
                .catch(error => console.error("Error cargando productos:", error));
        });
    }

    document.querySelector("#id_proveedor")?.addEventListener("change", actualizarProductos);
    actualizarProductos();
});
