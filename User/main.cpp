// 回放入口：读统一录像，跑检测、跟踪、瞄准与网页预览，不连 DevC。
// 产品按配置选择：`xrobot gen -c User/xrobot.yaml` 或 `xrobot gen -c User/RunConfig/<name>.yaml`。
//
// Replay entry: reads a unified recording and runs detection, tracking, aiming and the
// web preview, without the DevC link. The product is chosen by configuration.

#include "libxr.hpp"
#include "xrobot_main.hpp"

int main(int, char**)
{
  LibXR::PlatformInit();
  XROBOT_MAIN();
}
