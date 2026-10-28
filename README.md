# rescue-miniapp

中道救援用户端前端演示版，基于 uni-app（若依 RuoYi-App 脚手架）复刻截图界面。数据保存在前端 mock 中，以后可切换到真实后端。

## 运行

```bash
cd uni-app
cp .env.example .env   # 填入腾讯位置服务 key
npm install
npm run dev:h5         # 默认端口 9090
```

`config.js` 中 `useMock: true` 时，接口由 `uni-app/mock/` 在前端模拟，数据存在浏览器 localStorage。改为 `false` 并填写 `baseUrl` 即可对接后端。

## 目录

- `uni-app/`：前端源码
- `用户端小程序截图/`：复刻所依据的原始截图

## 许可证

MIT，见 [LICENSE](LICENSE)。
