export interface APIAddress {
  raw: string;
  user_friendly: string;
}

export interface ProposalData {
  id: number;
  address: APIAddress;
  votes_yes: number;
  votes_no: number;
  expires_at: number;
  receiver: APIAddress;
  payload: string;
}

export interface ProposalsList {
  proposals: ProposalData[]
}

export async function fetchProposalsList(dao: string): Promise<ProposalsList> {
  const params = new URLSearchParams({ dao });
  const result = await fetch("/api/proposals?" + params.toString());
  return await result.json() as ProposalsList;
}

export async function fetchProposalItem(dao: string, proposalId: number): Promise<ProposalData> {
  const params = new URLSearchParams({ dao });
  const result = await fetch(`/api/proposals/${proposalId}?` + params.toString());
  return await result.json() as ProposalData;
}

export interface DaoItem {
  address: APIAddress;
  jetton_master: APIAddress;
}

export interface DaoList {
  dao: DaoItem[]
}

export async function fetchDaoList(): Promise<DaoList> {
  const result = await fetch("/api/dao");
  return await result.json() as DaoList;
}

export async function fetchDaoItem(dao: string): Promise<DaoItem> {
  const result = await fetch(`/api/dao/${dao}`);
  return await result.json() as DaoItem;
}

export interface WalletState {
  address: APIAddress;
  balance: number;
}

export interface getWalletInfoResponse {
  address: APIAddress;
  is_participant: boolean;
  jetton_wallet: WalletState | null;
  lock: WalletState | null;
}

export async function fetchWalletInfo(dao: string, owner: string): Promise<getWalletInfoResponse> {
  const params = new URLSearchParams({ dao });
  const result = await fetch(`/api/wallets/${owner}?` + params.toString());
  return await result.json() as getWalletInfoResponse;
}
