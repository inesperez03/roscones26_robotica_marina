# Challenge 1 — Go to Pose

## Objetivo

En este ejercicio harás que el **BlueBoat** navegue hasta un punto elegido en **RViz**, utilizando la arquitectura **SURA** y el simulador **Stonefish**.

El programa `gotopose.py` ya recibe la posición del barco desde `/blueboat/navigator/navigation`, permite seleccionar el destino con un marcador interactivo y calcula la distancia y el error de orientación respecto al objetivo. También detiene el barco cuando está a menos de **1 metro** del destino.

**Tu tarea es completar únicamente los tres `TODO` del archivo.**

## TODO 1 — Activar el controlador

SURA utiliza ROS 2 Control para gestionar los controladores. Antes de enviar órdenes, el nodo debe activar el controlador **`body_force`** a través del servicio:

`/blueboat/controller/controller_manager/switch_controller`

En `switch_controller()` ya están creados el cliente y la petición `SwitchController.Request()`. Completa los campos necesarios para:

- Activar el controlador cuyo nombre llega como parámetro `controller_name` (la petición espera una **lista de nombres**).
- Elegir el nivel de exigencia (`strictness`) del cambio de controlador. Hay dos opciones:
  - **`STRICT`**: exige que se complete correctamente todo el cambio solicitado; si alguna operación falla, el cambio se considera fallido. Es útil cuando necesitas que el conjunto de controladores quede exactamente como has pedido.
  - **`BEST_EFFORT`**: intenta realizar las operaciones posibles aunque alguna falle. **Es el recomendado en este workshop**, porque solo queremos activar `body_force` y no necesitamos que falle toda la petición por otra operación.

Indica en la petición la constante correspondiente del servicio `SwitchController`.

La llamada asíncrona al servicio ya está implementada. No necesitas modificarla.

## TODO 2 — Elegir el tópico de comandos

El controlador `body_force` recibe las órdenes como mensajes **`geometry_msgs/msg/Wrench`**. En `send_force()` ya se rellenan los campos `force.x` (empuje hacia delante) y `torque.z` (giro), así que solo falta indicar **a qué tópico se publican**.

En SURA, el tópico de órdenes de este controlador sigue la estructura:

`/<robot>/controller/<nombre_del_controlador>/command`

En este ejercicio el robot se llama **`blueboat`** y el controlador es **`body_force`**. Sustituye `TODO_CONTROLLER_COMMAND_TOPIC` por el nombre completo resultante.

Puedes comprobar los tópicos disponibles con `ros2 topic list` y consultar su tipo con `ros2 topic info`.

## TODO 3 — Calcular fuerza y par

Implementa `calculate_force(distance_error, angle_error)`. La función debe devolver dos valores: **fuerza longitudinal** y **par de giro**.

Utiliza un controlador **proporcional (P)**: cuanto mayor sea el error, mayor será la orden. Para este challenge toma como referencia:

- Ganancia de distancia: **5.0**.
- Ganancia angular: **3.0**.
- Fuerza permitida: entre **0 y 15** (no queremos marcha atrás).
- Par permitido: entre **−5 y 5** (puede girar en ambos sentidos).
- Si el error angular supera los **45°** en valor absoluto, prioriza el giro y **no avances** hasta orientar el barco.

Recuerda: la fuerza depende de `distance_error` y el par depende de `angle_error`. La función debe devolver ambos valores, en ese orden. Puedes usar `math.pi` para expresar el umbral angular en radianes.

## Comprobación

Con el entorno SURA/Stonefish en marcha, ejecuta el nodo del challenge según las instrucciones de tu workspace. En RViz, mueve el marcador a una nueva posición e inicia la misión.

**El reto está superado cuando** el BlueBoat se orienta hacia el destino, avanza sin superar los límites de mando y se detiene al llegar a menos de un metro.

### ¿Cómo saber si el controlador está activo?

Abre otra terminal con el entorno ROS 2 configurado y consulta los controladores del `controller_manager` del BlueBoat:

```bash
ros2 control list_controllers -c /blueboat/controller/controller_manager
```

Busca `body_force` en la salida:

- **`active`**: el controlador está activado y puede recibir comandos.
- **`inactive`**: está cargado, pero aún no se ha activado.
- **No aparece**: revisa si se ha cargado y si estás consultando el `controller_manager` correcto.

Haz la comprobación **después de arrancar `gotopose.py`**, ya que ese nodo es el que solicita la activación.

Si el barco no se mueve y `body_force` está activo, revisa el tópico de publicación. Si gira o acelera de forma extraña, comprueba los signos y límites de tu controlador proporcional.