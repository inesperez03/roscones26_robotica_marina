# Challenge 3 — Seguimiento del robot de superficie 🚤🤿

## Objetivo

En este reto el **BlueROV** deberá **seguir al BlueBoat** en el simulador **Stonefish**, utilizando la arquitectura **SURA**. El robot submarino debe mantener su posición horizontal cerca del barco, alcanzar una **profundidad de referencia de 3 m** (coordenada `z = 3.0` en este escenario) y orientar su rumbo de forma similar al del BlueBoat.

El programa `surface_following.py` ya recibe la navegación de ambos robots, comprueba que los datos son recientes, calcula los errores de seguimiento y envía las órdenes de movimiento. **Completa los tres TODOs**. La estrategia de control es libre.

## ¿Cómo funciona?

Ambos robots publican su estado mediante el mensaje `sura_msgs/msg/Navigator`:

- BlueBoat: `/blueboat/navigator/navigation` — posición `x`, `y` y rumbo (`rpy.z`).
- BlueROV: `/bluerov/navigator/navigation` — posición `x`, `y`, `z` y rumbo (`rpy.z`).

El programa calcula la diferencia entre las posiciones de ambos robots (`error_x`, `error_y`), el error respecto a la referencia de profundidad (`depth_error`) y la diferencia de rumbo (`yaw_error`). Para evitar órdenes basadas en información antigua, no utiliza medidas con más de **1 segundo** de antigüedad.

**Importante:** la posición se expresa en el **sistema de referencia global**; en cambio, las fuerzas de avance y desplazamiento lateral se aplican respecto a los **ejes del BlueROV**. Tenlo en cuenta al diseñar el seguimiento.

## TODO 1 — Activar los controladores

Antes de mover el BlueROV, debes solicitar la activación de **`body_force`** y **`depth_hold`**. El programa ya llama a `switch_controller()` para cada uno y prepara el cliente de este servicio:

`/bluerov/controller/controller_manager/switch_controller`

Completa la petición `SwitchController.Request()` indicando el nombre que recibe la función en `controller_name` y el modo de ejecución mediante el campo `strictness`. Existen dos modos:

- **`STRICT`**: exige que todas las operaciones solicitadas se completen correctamente.
- **`BEST_EFFORT`**: intenta completar las operaciones posibles aunque alguna falle. **Es el modo recomendado para el workshop**.

La llamada asíncrona al servicio ya está implementada.

## TODO 2 — Publicar a través del árbitro de SURA

El BlueROV recibe comandos mediante el **árbitro de SURA**, en lugar de recibir directamente un `Wrench` en `body_force`. Completa el tópico del `publisher` siguiendo este patrón:

`/<robot>/controller/arbitrator/wrench`

En este ejercicio, el nombre del robot es **`bluerov`** y el tipo de mensaje es `sura_msgs/msg/SuraWrenchCommand`. La función `send_force()` ya prepara los campos `requester = 'surface_following'`, `controller = 'depth_hold'` y `priority = 90`, además de las fuerzas y el par de giro. No necesitas modificarla.

Para explorar la interfaz puedes utilizar `ros2 topic list` y `ros2 topic info <topico>`.

## TODO 3 — Diseñar el seguimiento

Implementa `calculate_force(error_x, error_y, depth_error, yaw_error, yaw)` para generar los comandos de movimiento del BlueROV. **Puedes elegir cualquier estrategia de control**; no se exige reproducir un algoritmo concreto.

La función debe devolver exactamente cuatro valores, **en este orden**:

| Salida | Acción |
| --- | --- |
| `force_x` | Avanzar o retroceder respecto al eje longitudinal del BlueROV. |
| `force_y` | Desplazarse lateralmente respecto al BlueROV. |
| `force_z` | Corregir la profundidad. |
| `torque_z` | Corregir el rumbo. |

Los errores `error_x` y `error_y` indican dónde se encuentra el barco respecto al submarino **en coordenadas globales**. El argumento `yaw` es la orientación actual del BlueROV y permite relacionar los ejes globales con los ejes del robot. Como pista, puedes estudiar cómo proyectar un desplazamiento del plano XY sobre los ejes longitudinal y lateral de un vehículo orientado un ángulo `yaw`.

`depth_error` representa la diferencia entre la profundidad de referencia y la medida, mientras que `yaw_error` representa la diferencia de rumbo, normalizada al intervalo **[−π, π]**. Comprueba en Stonefish **el sentido de las fuerzas y del par**: una orden con el signo incorrecto puede aumentar el error.

Para evitar movimientos bruscos, se recomienda limitar la magnitud de las órdenes. Como valores orientativos para este escenario: **±40** en `force_x` y `force_y`, **±25** en `force_z` y **±20** en `torque_z`. También puedes establecer tolerancias pequeñas cerca del objetivo para reducir oscilaciones; por ejemplo, **0,75 m** en posición horizontal, **0,15 m** en profundidad y **0,08 rad** en orientación. Estos parámetros son recomendaciones, no una estrategia obligatoria.

El bucle de control ya impide desplazarse horizontalmente mientras el error de profundidad supere **0,5 m**: primero debe alcanzarse la zona de profundidad deseada. No hace falta implementar de nuevo esta condición dentro de la función.

## Comprobación

Con **SURA y Stonefish** arrancados, ejecuta `surface_following.py` según la configuración de tu workspace. Comprueba que recibes navegación de ambos robots y mueve el BlueBoat para comprobar si el BlueROV **corrige su posición y continúa siguiéndolo**. Cada dos segundos aparecerán en consola la distancia horizontal, la profundidad y el error de orientación.

Para revisar si los controladores están activos, abre otra terminal con ROS 2 configurado y ejecuta:

```bash
ros2 control list_controllers -c /bluerov/controller/controller_manager
```

Los controladores **`body_force`** y **`depth_hold`** deberían aparecer en estado **`active`**. Si alguno aparece como **`inactive`**, está cargado pero no activado. Si no aparece, revisa el gestor de controladores correspondiente y la configuración del simulador.

Si el robot no se mueve, verifica el tópico del árbitro y que esté recibiendo comandos. Si se aleja del barco, cambia de profundidad en sentido contrario o gira incorrectamente, revisa la relación entre **coordenadas globales y locales**, así como los signos de las órdenes.

**Reto superado:** el BlueROV mantiene una profundidad próxima a la referencia y sigue los desplazamientos y cambios de rumbo del BlueBoat sin movimientos excesivamente bruscos.