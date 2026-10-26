# ROSCON 2026 · Robótica marina

## 1. Iniciar Docker

```bash
docker compose up -d
docker compose exec roscones26 bash
```

## 2. Challenge 1

**Terminal 1 — Simulación**

```bash
docker compose exec roscones26 bash
source install/setup.bash
ros2 launch roscon2026_bringup challenge1.launch.py
```

**Terminal 2 — Reto**

```bash
docker compose exec roscones26 bash
colcon build --merge-install --symlink-install --packages-select challenge_1
source install/setup.bash
ros2 run challenge_1 gotopose
```

## 3. Challenge 2

**Terminal 1 — Simulación**

```bash
docker compose exec roscones26 bash
source install/setup.bash
ros2 launch roscon2026_bringup challenge2.launch.py
```

**Terminal 2 — Reto**

```bash
docker compose exec roscones26 bash
colcon build --merge-install --symlink-install --packages-select challenge_2
source install/setup.bash
ros2 run challenge_2 visual_servoing
```

## 4. Challenge 3

**Terminal 1 — Simulación**

```bash
docker compose exec roscones26 bash
source install/setup.bash
ros2 launch roscon2026_bringup challenge3.launch.py
```

**Terminal 2 — Reto**

```bash
docker compose exec roscones26 bash
colcon build --merge-install --symlink-install --packages-select challenge_3
source install/setup.bash
ros2 run challenge_3 surface_following
```

## 5. Challenge 4

**Terminal 1 — Simulación**

```bash
docker compose exec roscones26 bash
source install/setup.bash
ros2 launch roscon2026_bringup challenge4.launch.py
```

**Terminal 2 — Reto**

```bash
docker compose exec roscones26 bash
colcon build --merge-install --symlink-install --packages-select challenge_4
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
