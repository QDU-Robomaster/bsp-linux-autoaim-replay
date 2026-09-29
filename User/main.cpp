// Replay entry: recorded frames only, no DevC USB link. User/xrobot_main.hpp is
// generated from User/xrobot.yaml (xrobot setup / xrobot gen).

#include "bsp_common.hpp"
#include "xrobot_main.hpp"

int main(int, char **)
{
  static LibXR::RamFS ramfs;
  if (!AutoAimBsp::Init(ramfs))
  {
    return 1;
  }

  XR_REGISTER(ramfs, LibXR::RamFS);
  XROBOT_MAIN();
}
