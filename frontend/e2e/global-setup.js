import { execSync } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default async function globalSetup() {
  console.log('\n🛠️  [GlobalSetup] 自动重置测试数据...')
  try {
    const dbPath = path.resolve(__dirname, '../../tostiyk_erp.db')
    // 1. 重置商品库存
    execSync(`sqlite3 "${dbPath}" "UPDATE autopart SET stock = 999 WHERE oem = 'TK-12345';"`)
    // 2. 重置客户欠款并调高信用额度
    execSync(`sqlite3 "${dbPath}" "UPDATE client SET debt = 0, credit_limit = 999999 WHERE name LIKE '%elias%';"`)
    
    console.log('✅ [GlobalSetup] 库存已恢复至 999，客户欠款已清零，信用额度已放宽至 999999\n')
  } catch (e) {
    console.error('⚠️ [GlobalSetup] 自动重置测试数据失败', e.message)
  }
}
