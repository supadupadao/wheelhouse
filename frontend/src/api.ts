export interface APIAddress {
  raw: string;
  user_friendly: string;
}

export interface ProposalData {
  id: Number;
  address: APIAddress;
  votes_yes: Number;
  votes_no: Number;
  expires_at: Number;
}

export interface ProposalsResponse {
  proposals: ProposalData[]
}

export async function fetchProposalsList(dao: string): Promise<ProposalsResponse> {
  const params = new URLSearchParams({ dao });
  const result = await fetch("/api/proposals?" + params.toString());
  return await result.json() as ProposalsResponse;
}

export interface DaoItem {
  address: APIAddress;
  jetton_master: APIAddress;
}

export interface DaoListResponse {
  dao: DaoItem[]
}

export async function fetchDaoList(): Promise<DaoListResponse> {
  const result = await fetch("/api/dao");
  return await result.json() as DaoListResponse;
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
  jetton_wallet: WalletState | null;
  lock: WalletState | null;
}

export async function fetchWalletInfo(dao: string, owner: string): Promise<getWalletInfoResponse> {
  const params = new URLSearchParams({ dao });
  const result = await fetch(`/api/wallets/${owner}?` + params.toString());
  return await result.json() as getWalletInfoResponse;
}
