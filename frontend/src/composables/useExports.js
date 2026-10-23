import { apiUrl } from '../utils/api'

export function useExports() {
  const exportTransactionsExcel = () => window.open(apiUrl('/api/export/transactions'), '_blank')
  const exportPartsExcel        = () => window.open(apiUrl('/api/export/parts'), '_blank')
  const exportClientsExcel      = () => window.open(apiUrl('/api/export/clients'), '_blank')
  const downloadDatabaseBackup  = () => window.open(apiUrl('/api/backup/download'), '_blank')
  
  // 🌟 新增这一行
  const downloadPartsTemplate   = () => window.open(apiUrl('/api/export/template/parts'), '_blank')

  // 🌟 这里把 downloadPartsTemplate 导出去
  return { exportTransactionsExcel, exportPartsExcel, exportClientsExcel, downloadDatabaseBackup, downloadPartsTemplate }
}