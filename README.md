# BSP Linux AutoAim Replay

用录像回放自瞄视觉链路（装甲板检测、跟踪、Aimer 与网页预览），不需要海康相机和 DevC。实机 BSP 是 `bsp-linux-autoaim`；两者的模块版本各自锁定，升级时分别运行 `xrobot setup --update`。

录像为统一录像格式：一个目录里有 `frames.csv` 与逐帧 640×512 BayerRG8 PGM，由车上的 VisionRecorder 写出。CaptureFileCamera 按录制的时间节奏读出每一帧，带着录制的 IMU（没有 IMU 列时用静止姿态）直接发布同步帧 `gimbal_synced`，后面的检测、跟踪、瞄准与车上相同。

## 目录

```text
Modules/modules.yaml     需要的模块（`xrobot:` 固定 XRobot 版本）
xrobot.lock              模块的精确 commit
User/main.cpp            入口：初始化平台并调用 XROBOT_MAIN()
User/xrobot.yaml         回放配置，检测用 OpenVINO（.onnx）
User/RunConfig/hailo.yaml 同一配置，检测用 Hailo（.hef），在 Raspberry Pi 5 + Hailo-8 上运行
tools/convert_rawcap.py  旧格式 rawcap 录像转为统一录像格式
libxr/                   LibXR submodule
```

`User/xrobot_main.hpp` 和 `Modules/CMakeLists.txt` 由 `xrobot` 生成，不提交；模型目录 `armor-models/` 与录像链接 `recording` 也不进仓库。

## 构建和运行

```bash
git submodule update --init --recursive
pip install xrobot==1.0.0      # 与 Modules/modules.yaml 的 xrobot: 一致
xrobot setup
xrobot gen -c User/xrobot.yaml
cmake --preset release
cmake --build --preset release --target rm_auto_aim_replay
```

模型与车上 BSP 相同，放在 `armor-models/model_private/`：

```bash
git clone https://github.com/QDU-Robomaster/armor-models.git
armor-models/scripts/fetch_model.sh det-v7.0 armor-models/model_private
armor-models/scripts/fetch_model.sh num-v1.0 armor-models/model_private
```

配置读取仓库根目录下的 `recording`，把要回放的录像目录链接到这里后运行：

```bash
ln -sfn <录像目录> recording
./build/release/rm_auto_aim_replay
```

浏览器打开 `http://<主机>:8080/` 查看各层结果；终端每秒打印各模块的统计。`speed` 为 1 时按录制速度播放，0 为不限速；`loop` 为 `true` 时播完从头开始。录像的相机标定写在配置的 `constexprs` 段，需与录制的相机一致。

## 旧格式录像

rawcap 早期的录像 `frames.csv` 为 `frame,dev_ts,host_ms`，没有 IMU。转换后可以直接回放（PGM 以硬链接放进新目录）：

```bash
python3 tools/convert_rawcap.py <旧录像目录> <新目录>
```

脚本把 `session.txt` 里跳采后的偏移换算成原生 ROI，并由整段录像的设备时间与主机时间之比定出设备时间戳的单位。
