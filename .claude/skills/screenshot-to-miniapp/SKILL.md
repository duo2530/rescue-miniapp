---
name: screenshot-to-miniapp
description: 按一组小程序/App 截图，用 uni-app（常见是若依 RuoYi-App 脚手架）复刻出外观尽量一致的前端演示版，数据先存前端 mock，以后能切到真实后端。覆盖出方案、读图、像素测量、裁素材、mock 数据层、H5 构建、浏览器并排验收。用户说"照着截图复刻""做一个和截图一样的小程序""先做前端演示，以后接后端"时使用。与具体业务无关。
metadata:
  version: "1.0.0"
  date: "2026-10-28"
---

# 截图复刻小程序 SOP

目标：截图里的每个页面在 390 宽视口下和原图并排看基本重合，主要业务流程能在前端点通，以后接后端时页面代码不用改。

## 0. 读图规则（最重要，先读）

Read 工具读图时好时坏，可能只返回 `(no output)` 加一行 `[Image: original WxH ...]`。`(no output)` 只说明结果里没有文字，不能据此判断图片读取成功或失败。

- **每读一张图，立刻写下看到的具体内容**（文字、颜色、布局）。写不出具体内容，就按没看到处理，**不要说"已看清/已核对"**。上次因为这个，凭印象写的文案被当成原文，后来只能逐条更正。
- **必须逐字准确的内容（说明文字、协议、价格），直接请用户贴图或给原文。** 用户直接粘贴进对话的图片一直能正常显示。
- **尺寸、颜色、边界用脚本读像素**（`scripts/measure.py`），不靠看图估。
- 重读裁剪图时换一个新文件名；并排对比图在每轮代码修改后只读一次，代码没改就不要重读。

## 1. 出方案，先确认再写代码

先逐张读截图，列出页面清单和每页元素，然后给出方案，列出需要确认的问题。通常要问：
1. **主要在哪个端演示**（H5 还是微信小程序）。这决定地图、导航栏、ActionSheet 等怎么实现。
2. **截图里没给的业务规则**，例如某项服务没显示价格时怎么计价。先给一个默认值，写进配置，之后可以改。
3. **截图里没有的页面**（详情页、空状态下的列表卡片、协议文案）：按现有风格自己设计，还是只做空状态。
4. **第三方 key**（地图等）：让用户写进 `.env`，不要贴进对话。检查时只看变量名和长度，值打码输出。

## 2. 尺寸换算

- iPhone 截图常见宽度 1170px（3 倍图）或 750px（2 倍图）。按 `宽 ÷ 倍数` 得到设计宽度 390pt / 375pt。
- 在 `uni.scss` 里加换算函数，所有样式写 `r(pt)`：
  ```scss
  /* 设计稿按 390pt 宽（截图 1170px ÷ 3）标注 */
  @function r($pt) { @return $pt * 750 / 390 * 1rpx; }
  ```
- 用 `measure.py` 测量（加 `--scale 3`，输出直接是 pt）：
  ```bash
  M=~/.claude/skills/screenshot-to-miniapp/scripts/measure.py
  python -I $M color IMG 585,600 100,2000          # 取色
  python -I $M col   IMG 585 --scale 3 --th 40     # 纵向扫一列：各区块的 top 和高度
  python -I $M row   IMG 1200 --scale 3            # 横向扫一行：Tab 宽度、间距
  python -I $M bbox  IMG 0,800,1170,1100 --scale 3 # 区域内元素的包围盒（字号、图标大小）
  python -I $M crop  IMG 0,0,1170,600 OUT.png      # 裁剪放大，用来看细节
  python -I $M side  原图 实现截图 OUT.png          # 并排对比
  ```
- 字号：用 bbox 量汉字高度，字号约为高度 ÷ 0.9 再取整。
- 渐变：沿渐变方向扫一行或一列，取首尾颜色。

## 3. 素材

- logo、图标、头图、地图标记这类图片，用 PIL 从截图里裁出来，放到 `static/images/<项目>/`。
- 裁完把所有素材拼成一张图检查一遍。上次有图标带进了地图背景，还有一个带进了相邻的文字。
- 像素扫描找到的"图标"，可能其实是一个字（上次把"车"字和数字"3"当成了箭头）。要用裁剪图确认。
- 通用小图标优先用 uni-icons，找不到再裁图。
- 最后告诉用户哪些素材是裁出来的、清晰度有限，有原始素材可以替换。

## 4. 工程结构

**若依 RuoYi-App 脚手架**是 HBuilderX 目录结构，没有 `package.json`。要用命令行构建 H5：
- `package.json` 里的 `@dcloudio/*` 包统一用同一个版本号，配 vue 3.4.x、vite 5.x、sass 1.63.x、pinia。
- `scripts/uni.js`：
  ```js
  // 源码在项目根目录（HBuilderX 结构），uni CLI 默认读 ./src，这里改成根目录再启动
  const path = require('path')
  process.env.UNI_INPUT_DIR = path.resolve(__dirname, '..')
  require('@dcloudio/vite-plugin-uni/bin/uni.js')
  ```
  scripts 里写：`"dev:h5": "node scripts/uni.js"`、`"build:h5": "node scripts/uni.js build"`、`"dev:mp-weixin": "node scripts/uni.js -p mp-weixin"`。
- `.env` 里的变量要能通过 `import.meta.env` 读到，需要在 `vite.config.js` 里设 `envPrefix`。把 `.env` 加进 `.gitignore`，另外提交一个 `.env.example`。
- 删掉若依自带的登录、工作台、权限、字典等示例代码，删之前先列清单给用户确认。

**数据层（以后接后端靠这一层）：**
- `config.js` 里加 `useMock: true`。
- `utils/request.js` 按开关分流：`config.useMock ? mockRequest(options) : uni.request(...)`。
- `mock/db.js`：基于 `uni.setStorageSync` 的本地存储，首次运行写入预置数据（演示账号、车辆、历史订单等）。
- `mock/index.js`：按 url 和 method 分发，返回值格式和真实后端一致（`{code, msg, data}`）。
- 业务配置（服务类型、价格、说明文字）单独放一个文件，比如 `mock/services.js`。
- 页面只调用 `api/*.js`，每个接口的入参和出参写在注释里，后端可以照着实现。
- 让演示有动态效果：订单状态按时间推进，兑换码加优惠券，下单时校验必填项。

**导航栏和 Tab 栏：** 如果截图里 tab 页有返回箭头，或者只有部分页面带 Tab 栏，就在 `pages.json` 里用 `navigationStyle: custom`，自己写 nav-bar 和 tab-bar 组件。小程序端要给胶囊按钮留位置。
**H5 和小程序的差异：** 截图顶部的状态栏和胶囊按钮是微信自带的，H5 不用做。`uni.showActionSheet` 等原生弹层在 H5 上样式差别很大，需要像截图时改成自定义弹层。

## 5. 地图（如有）

- 小程序端用 `<map>`；H5 端需要腾讯地图 key（写在 `.env`），没有 key 就用静态底图。
- 写代码前先单独请求一次逆地址解析、地点搜索和路线规划，确认 key 可用。
- **每日配额会用完**（腾讯地图返回 status 121）。路线接口要有降级方案，比如用直线距离 × 1.3 估算里程、画直线。调试时少刷新会请求路线的页面，正式演示前再验证一次配额。

## 6. Windows 环境的坑

- 不要在 `python -c "..."` 里写中文路径，GBK 会把路径弄乱。改用 `python -I - <<'EOF' ... EOF`，或者先 cd 到目录里。
- Python 打印中文前先 `sys.stdout.reconfigure(encoding='utf-8')`。
- 大文件不要用一个超长 heredoc 写，引号不配对会导致只写进一部分。改用 Write 工具，写完检查文件确实存在、内容完整。
- 用 sed 改 scss/vue 不能跨行匹配。多行替换用 Edit 工具，或者用 Python 读文件后做 `str.replace`，并 assert 原文确实存在。

## 7. 浏览器验收

- 用用户指定的浏览器工具。用户没指定时优先用 agent-browser：browser-harness 连接时会弹出"Allow remote debugging?"，需要用户手动点允许。
- agent-browser 的用法：
  ```bash
  S="--session app"
  timeout 30 agent-browser $S set viewport 390 844
  timeout 30 agent-browser $S open "http://localhost:端口/#/pages/index"
  timeout 20 agent-browser $S wait 3000
  timeout 30 agent-browser $S screenshot "$TEMP/shots/home.png"
  timeout 20 agent-browser $S errors        # 看控制台报错
  ```
  每条命令都要加 `timeout`。上次多条命令串在一起时卡死，只能 TaskStop。需要定位就用 `set geo 纬度 经度`。
- 已知的坑：HMR 有时不会更新已经打开的页面，截图前先 reload；`fill` 失败后输入框里会留下旧内容，重填前先清空；单页应用里没关掉的弹窗会一直留着，挡住后续点击，每步截图后先看一眼有没有弹窗。
- **逐页对比**：`measure.py side 原图 实现截图 cmp.png`，读对比图，写下差异，改代码，再截图。每页改到基本重合。
- **流程测试**：切换各个服务看价格、不填必填项提交、正常下单、订单详情和状态推进、取消订单、兑换优惠券后价格是否扣减、退出登录。

## 8. 收尾报告

- 列出哪些页面和截图基本一致、哪些页面是自己设计的（截图里没有）、哪些功能没做（用户说先不做的）。
- 说明 mock 开关怎么切、预置了哪些演示数据（账号、兑换码）、怎么重置（清空 localStorage）。
- 说明 key 放在哪里、是否已被 git 忽略、配额情况。
- 构建命令和开发服务器地址。不要主动提交代码，问用户是否需要提交。
