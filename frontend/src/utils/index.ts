import type { Address } from "@ton/core";

export function cropTonAddress(address: Address): string {
  const str = address.toString();
  return `${str.slice(0, 6)}...${str.slice(-4)}`;
}

export function nanoTonToTon(nano: number): string {
  return (Number(nano) / 1_000_000_000).toFixed(9);
}
