# Challenge 2 — Visual Servoing con ArUco 🤿

## Objetivo

En este reto controlarás el **BlueROV** en **Stonefish**, utilizando **SURA** y una cámara frontal para aproximarte a un marcador **ArUco ID 0** y orientarte frente a él.

El programa `visual_servoing.py` **ya detecta el marcador**, estima su posición y orientación a partir de la cámara y proporciona su pose para calcular los errores respecto al objetivo. También comprueba cuándo se alcanza el objetivo. **Completa los cuatro `TODO` indicados en el código**.

## ¿Cómo funciona?

La cámara publica las imágenes en `/bluerov/front_camera/camera/image_raw` y su calibración en `/bluerov/stonefish/front_camera/camera_info`. El nodo detecta marcadores del diccionario **`DICT_4X4_50`**, busca el **ID 0** y utiliza un tamaño real de **0,5 m** para estimar su pose.

A partir de esa estimación, tendrás que obtener cuatro errores: distancia, desplazamiento horizontal, desplazamiento vertical y orientación. El objetivo es situarse a **1 m** del marcador, centrado y orientado frente a él. Si el marcador deja de detectarse durante más de **0,5 s**, el nodo deja de calcular y enviar nuevas órdenes hasta volver a verlo.

## TODO 1 — Activar los controladores

Antes de controlar el robot, debes solicitar la activación de **`body_force`** y **`depth_hold`**. El programa ya llama dos veces a `switch_controller()`, una por cada controlador, y crea el cliente del servicio:

`/bluerov/controller/controller_manager/switch_controller`

En la petición `SwitchController.Request()` completa:

- La lista de controladores que se quieren activar, utilizando el nombre recibido en `controller_name`.
- El modo de activación (`strictness`), que admite **`STRICT`** (exige que se cumpla todo el cambio) y **`BEST_EFFORT`** (intenta completar las operaciones posibles). **Para este workshop se recomienda `BEST_EFFORT`.**

La llamada asíncrona al servicio ya está escrita; no la modifiques.

## TODO 2 — Publicar órdenes a través del árbitro

A diferencia del Challenge 1, ahora el nodo no publica un `Wrench` directamente en `body_force`: envía un **`sura_msgs/msg/SuraWrenchCommand`** al **árbitro de SURA**, encargado de gestionar las solicitudes de control.

El tópico del árbitro sigue el patrón:

`/<robot>/controller/arbitrator/wrench`

El robot de este ejercicio se llama **`bluerov`**. Sustituye `TODO_ARBITRATOR_WRENCH_TOPIC` por el tópico completo.

La función `send_force()` ya construye el mensaje. Fíjate en los campos `requester = 'pbvs'`, `controller = 'depth_hold'` y `priority = 90`: identifican la solicitud, el controlador asociado y su prioridad. No necesitas modificar esos valores.

Puedes comprobar el tópico y su tipo con `ros2 topic list` y `ros2 topic info <topico>`.

## TODO 3 — Calcular los errores respecto al marcador

Completa el bloque `# TODO 3` del bucle de control. Al detectar el ArUco, el programa ya dispone de `aruco_x`, `aruco_y`, `aruco_z` y `aruco_yaw`, calculados respecto a la cámara frontal.

La pose deseada es **a 1 metro de distancia**, con el marcador **centrado horizontal y verticalmente** y **sin error de orientación**. Calcula y guarda estas cuatro variables, que usa el resto del programa:

- `distance_error`: diferencia entre la distancia observada (`aruco_z`) y la distancia deseada (**1.0 m**).
- `horizontal_error`: desplazamiento horizontal observado (`aruco_x`), respecto al centro de la imagen (referencia **0**).
- `vertical_error`: desplazamiento vertical observado (`aruco_y`), respecto al centro de la imagen (referencia **0**).
- `yaw_error`: error de orientación estimado (`aruco_yaw`), respecto a la orientación deseada (**0 rad**).

**Pista:** trabaja con diferencias entre medida y referencia, conservando el signo de los errores. No modifiques la función que detecta el marcador.

## TODO 4 — Diseñar el control de movimiento

Implementa `calculate_force(distance_error, horizontal_error, vertical_error, yaw_error)` para que el BlueROV reduzca los errores de posición y orientación respecto al ArUco. **Puedes elegir libremente la estrategia de control** y ajustar sus parámetros durante las pruebas.

La función recibe los cuatro errores calculados en el TODO 3 y debe devolver, **en este orden**, `force_x`, `force_y`, `force_z` y `torque_z`:

| Salida | Movimiento que controla | Error de referencia |
| --- | --- | --- |
| `force_x` | Avance y retroceso | `distance_error` |
| `force_y` | Desplazamiento lateral | `horizontal_error` |
| `force_z` | Subida y bajada | `vertical_error` |
| `torque_z` | Giro sobre el eje vertical | `yaw_error` |

Ten en cuenta **el sentido de cada eje** y comprueba en el simulador que las órdenes reducen los errores en lugar de aumentarlos. Para evitar movimientos bruscos, es recomendable acotar las órdenes; como límites orientativos para este escenario puedes usar **±60** en X, **±40** en Y y Z y **±25** para el par de giro.

El objetivo no es reproducir una fórmula concreta, sino conseguir que el robot llegue a la pose deseada de manera estable. Compara el comportamiento en Stonefish y ajusta tu solución según los resultados.

## Comprobación

Con **SURA y Stonefish** en marcha, ejecuta `visual_servoing.py` según la configuración de tu workspace y coloca el BlueROV de forma que su cámara frontal pueda ver el **ArUco ID 0**. Observa los errores y las fuerzas que imprime el programa.

**El reto está superado cuando** el BlueROV se aproxima al marcador, corrige la posición lateral, la altura y la orientación, y muestra `¡Objetivo alcanzado!` al entrar en las tolerancias programadas. Para la comprobación actual se exige: error de distancia menor de **1,5 m**, error horizontal y vertical menores de **0,25 m** y error de orientación menor de **0,15 rad**.

### ¿Cómo comprobar si los controladores están activos?

En otra terminal con ROS 2 configurado, ejecuta:

```bash
ros2 control list_controllers -c /bluerov/controller/controller_manager
```

Comprueba que **`body_force`** y **`depth_hold`** aparecen como **`active`** después de iniciar el nodo. Si alguno figura como **`inactive`**, está cargado pero no activado; si no aparece, revisa su carga y el `controller_manager` utilizado.

Si los controladores están activos pero el robot no responde, comprueba el tópico del árbitro y sus mensajes. Si se mueve en dirección incorrecta o demasiado rápido, revisa el cálculo de errores del TODO 3, el sentido de las órdenes y los límites que hayas establecido en el TODO 4.