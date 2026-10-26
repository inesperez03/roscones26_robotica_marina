# Retos ROS 2

Cada reto es un paquete independiente. El primer reto incluye el nodo `gotopose`; los retos 2, 3 y 4 siguen como plantillas. Puedes desarrollar un reto sin compilar el código de los otros.

Desde la raíz del workspace (`/home/usuario/roscones26_robotica_marina`):

```bash
source /opt/ros/humble/setup.bash
source /home/usuario/roscones26_roboticamarina/install/setup.bash
colcon build --packages-select challenge_1
source install/setup.bash
ros2 run challenge_1 gotopose
```

Cambia `1` por `2`, `3` o `4` para trabajar en otro reto. Si añades dependencias de otros paquetes a un reto, usa `colcon build --packages-up-to challenge_1` para construir también sus dependencias. `colcon build` sin filtros intenta compilar todos los paquetes encontrados y fallará si alguno contiene errores.

Para el taller, edita `src/challenge_1/challenge_1/gotopose.py`: todo el recorrido está en un único bucle dentro de `main()`. El bucle activa `BODY_VELOCITY`, calcula el error y el PID, y pide `HOLD_POSITION` al llegar. Los dos callbacks pequeños reciben la posición del barco y la meta del marcador. Solo el dibujo del marcador de RViz está en `target_marker.py`. Los otros retos siguen en `src/challenge_N/challenge_N/node.py`.

`HOLD_POSITION` mantiene `body_velocity` activo para el feedforward del controlador, pero este nodo deja de publicar velocidad al llegar. El arbitrador descarta automáticamente el último comando de velocidad cuando caduca.

Lanza primero la simulación con `ros2 launch roscon2026_bringup challenge1.launch.py` desde el workspace principal. En otra terminal ejecuta `gotopose` con los comandos anteriores. El propio nodo del reto crea el marcador `challenge1_goal` delante del BlueBoat al recibir la primera posición válida. En RViz mueve y suelta ese marcador: el nodo navega con el controlador de velocidad del BlueBoat y activa `HOLD_POSITION` al llegar. No hace falta configurar ni activar ninguna acción GoToPose de SURA.
