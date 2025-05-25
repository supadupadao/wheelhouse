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
