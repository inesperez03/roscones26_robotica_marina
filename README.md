# ROSCON 2026 · Robótica marina

## 1. Iniciar Docker

```bash
docker compose up -d
docker compose exec roscones26 bash
```

## 2. Compilar los retos (dentro del contenedor)

```bash
cd /root/roscones26_roboticamarina
source /opt/ros/humble/setup.bash
colcon build --merge-install --symlink-install --packages-select challenge_1 challenge_2 challenge_3
source install/setup.bash
```

## 3. Challenge 1

**Terminal 1 — Simulación**

```bash
docker compose exec roscones26 bash
source /opt/ros/humble/setup.bash
source /root/roscones26_roboticamarina/install/setup.bash
ros2 launch roscon2026_bringup challenge1.launch.py
```

**Terminal 2 — Reto**

```bash
docker compose exec roscones26 bash
source /opt/ros/humble/setup.bash
source /root/roscones26_roboticamarina/install/setup.bash
ros2 run challenge_1 gotopose
```

## 4. Challenge 2

**Terminal 1 — Simulación**

```bash
docker compose exec roscones26 bash
source /opt/ros/humble/setup.bash
source /root/roscones26_roboticamarina/install/setup.bash
ros2 launch roscon2026_bringup challenge2.launch.py
```

**Terminal 2 — Reto**

```bash
docker compose exec roscones26 bash
source /opt/ros/humble/setup.bash
source /root/roscones26_roboticamarina/install/setup.bash
ros2 run challenge_2 visual_servoing
```

## 5. Challenge 3

**Terminal 1 — Simulación**

```bash
docker compose exec roscones26 bash
source install/setup.bash
ros2 launch roscon2026_bringup challenge3.launch.py
```

**Terminal 2 — Reto**

```bash
docker compose exec roscones26 bash
source install/setup.bash
ros2 run challenge_3 surface_following
```

## 6. Comprobaciones

```bash
ros2 topic list
ros2 control list_controllers -c /blueboat/controller/controller_manager
ros2 control list_controllers -c /bluerov/controller/controller_manager
```

## 7. Detener Docker (desde el ordenador)

```bash
docker compose down
```
