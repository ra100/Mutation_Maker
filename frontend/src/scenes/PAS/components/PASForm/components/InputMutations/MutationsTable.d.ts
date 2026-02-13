import { ComponentType } from 'react'

interface MutationsTableProps {
  mutations: any[]
  onChange?: (newMutations: any) => void
}

declare const MutationsTable: ComponentType<MutationsTableProps>
export default MutationsTable
