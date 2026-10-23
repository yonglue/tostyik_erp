import { apiUrl } from '../utils/api'

export function useExports() {
  const exportTransactionsExcel = () => window.open(apiUrl('/api/export/transactions'), '_blank')
  const exportPartsExcel        = () => window.open(apiUrl('/api/export/parts'), '_blank')
  const exportClientsExcel      = () => window.open(apiUrl('/api/export/clients'), '_blank')
  const downloadDatabaseBackup  = () => window.open(apiUrl('/api/backup/download'), '_blank')

  return { exportTransactionsExcel, exportPartsExcel, exportClientsExcel, downloadDatabaseBackup }
}
