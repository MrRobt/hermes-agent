# [REQ-DASH-20260515-01] Hermes Dashboard 改造验收与回归验证

## 验证范围

- 仓库：`/usr/local/lib/hermes-agent`
- 前端目录：`/usr/local/lib/hermes-agent/web`
- 当前分支：`fix/anthropic-non-claude-dot-normalization`
- 验证对象：Hermes Dashboard 样式与关键页面回归
- 验证时间：2026-05-15

## 执行命令

```bash
cd /usr/local/lib/hermes-agent/web
npm run lint
npm run build

cd /usr/local/lib/hermes-agent
hermes dashboard --host 127.0.0.1 --port 9119 --no-open --skip-build
curl -sS -m 8 -o /tmp/hermes_dash_home.html -w '%{http_code} %{content_type}\n' http://127.0.0.1:9119/
curl -sS -m 8 -o /tmp/hermes_dash_config.html -w '%{http_code} %{content_type}\n' http://127.0.0.1:9119/config
```

截图使用本地 Playwright Chromium 兼容模式完成：

```bash
PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 node <截图脚本>
```

## 验证结果

| 检查项 | 结果 | 说明 |
|---|---:|---|
| Dashboard 服务启动 | 通过 | `http://127.0.0.1:9119/` 返回 `200 text/html` |
| 配置页路由 | 通过 | `/config` 返回 `200 text/html` |
| 前端构建 | 通过 | `tsc -b && vite build` 成功，产物写入 `hermes_cli/web_dist` |
| 关键页面截图 | 通过 | 首页、配置页、模型页、会话页、技能页均可渲染并截图 |
| 页面运行错误 | 通过 | 截图脚本捕获页面错误数均为零 |
| 静态代码检查 | 未通过 | `npm run lint` 存在二十三个错误、四个警告，多数为既有 React 钩子规则与刷新规则问题 |
| 明显样式破损 | 基本通过 | 未发现大面积空白、布局重叠、红色报错弹窗 |

## 截图产物

- `/tmp/hermes-dashboard-qa/home.png`
- `/tmp/hermes-dashboard-qa/config.png`
- `/tmp/hermes-dashboard-qa/models.png`
- `/tmp/hermes-dashboard-qa/sessions.png`
- `/tmp/hermes-dashboard-qa/skills.png`

## 视觉检查发现

1. 首页整体布局完整，左侧导航、会话列表、平台连接状态均正常显示。
2. 配置页整体布局完整，分类栏、搜索、保存按钮、字段表单均正常显示。
3. 配置页 `Fallback Providers` 字段显示为 `[object Object], [object Object]`，疑似对象渲染错误，需要后续修复。
4. 首页部分会话预览中出现方块字符，疑似字体或字符集覆盖不足；不阻断主流程，但影响可读性。
5. 页面没有发现明显布局重叠、异常空白或前端错误弹窗。

## 风险点

1. `npm run lint` 当前失败，不能作为通过门禁；需单独安排修复 React 钩子规则、未使用变量和多语言转义问题。
2. 构建成功但产物体积提示超过五百千字节，属于既有性能风险。
3. Ubuntu 二十六点零四暂未被当前 Playwright 官方识别，截图时使用 `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64` 下载兼容浏览器；后续建议升级 Playwright 或固定浏览器二进制来源。
4. 本次未验证真实交互保存配置、登录授权断连等写操作，只做只读页面与视觉回归。

## 结论

Dashboard 关键页面可启动、可构建、可访问、可截图，未见明显样式破损或运行时报错；但静态检查未通过，且配置页存在对象渲染为 `[object Object]` 的可见问题。建议本验收任务标记为“完成验证但带风险”，后续单独创建修复任务处理 lint 与配置字段渲染问题。
