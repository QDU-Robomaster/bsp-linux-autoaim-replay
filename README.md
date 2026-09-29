# BSP Linux AutoAim Replay

用内录的相机帧和 IMU 数据回放自瞄视觉链路（相机帧同步、装甲板检测、跟踪、Aimer），
不需要 Hik 相机和 DevC。实机 BSP 是 `bsp-linux-autoaim`；两者的模块版本各自锁定，
升级时分别运行 `xrobot setup --update`。

## 目录

```text
Modules/modules.yaml     需要的模块（`xrobot:` 固定 XRobot 版本）
xrobot.lock              模块的精确 commit
User/main.cpp            入口：注册 RamFS 并调用 XROBOT_MAIN()
User/bsp_common.hpp      平台初始化、终端、文件日志
User/xrobot.yaml         回放配置（录像路径、几何、检测和跟踪参数）
libxr/                   LibXR submodule
```

`User/xrobot_main.hpp` 和 `Modules/CMakeLists.txt` 由 `xrobot` 生成，不提交。

## 构建和运行

```bash
git submodule update --init --recursive
pip install xrobot==1.0.0      # 与 Modules/modules.yaml 的 xrobot: 一致
xrobot setup
cmake --preset debug
cmake --build --preset debug --target rm_auto_aim_replay
./build/debug/rm_auto_aim_replay
```

录像和 IMU 文件路径写在 `User/xrobot.yaml` 的 `camera.args.runtime` 中
（默认 `./data/camera_internal_recording_20260428/`），保持录像原始 `1440x1080` 几何。
