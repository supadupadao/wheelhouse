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

export interface DaoData {
  address: APIAddress;
}

export interface DaoListResponse {
  dao: DaoData[]
}

export async function fetchDaoList(): Promise<DaoListResponse> {
  const result = await fetch("/api/dao");
  return await result.json() as DaoListResponse;
}

export interface getWalletAddressResponse {
  address: APIAddress;
}

export async function fetchWalletAddress(dao: string, owner: string): Promise<getWalletAddressResponse> {
  const params = new URLSearchParams({ dao, owner });
  const result = await fetch("/api/getters/get_wallet_address?" + params.toString());
  return await result.json() as getWalletAddressResponse;
}

export interface getLockAddressResponse {
  address: APIAddress;
}

export async function fetchLockAddress(dao: string, owner: string): Promise<getLockAddressResponse> {
  const params = new URLSearchParams({ dao, owner });
  const result = await fetch("/api/getters/get_lock_address?" + params.toString());
  return await result.json() as getLockAddressResponse;
}

export interface getJettonMasterResponse {
  address: APIAddress;
}

export async function fetchJettonMaster(dao: string): Promise<getJettonMasterResponse> {
  const params = new URLSearchParams({ dao });
  const result = await fetch("/api/getters/get_jetton_master?" + params.toString());
  return await result.json() as getJettonMasterResponse;
}
