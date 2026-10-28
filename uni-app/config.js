// 应用全局配置
export default {
  // true：接口由 /mock 在前端模拟，数据存在本地 storage；false：请求 baseUrl 的真实后端
  useMock: true,
  baseUrl: 'http://localhost:8080',
  // 腾讯地图 WebService key，构建时从 .env 的 TECENT_MAP_KEY 注入
  qqMapKey: import.meta.env.TECENT_MAP_KEY || '',
  // 应用信息
  appInfo: {
    name: '中道救援',
    version: '1.0.0',
    // 客服电话
    servicePhone: '021-66898194'
  }
}
