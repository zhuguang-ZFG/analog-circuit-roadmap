import {Config} from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer("angle");
// 快乐体等自定义字体加载完毕才允许采帧
Config.setDelayRenderTimeoutInMilliseconds(30000);
