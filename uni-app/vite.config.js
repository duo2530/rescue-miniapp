import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

export default defineConfig({
  // 让 .env 中的 TECENT_MAP_KEY 可通过 import.meta.env 读取
  envPrefix: ['VITE_', 'UNI_', 'TECENT_'],
  plugins: [uni()]
})
