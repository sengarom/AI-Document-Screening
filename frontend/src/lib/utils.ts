import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCaseId(uuid: string): string {
  if (!uuid) return 'VRX-DEMO-0000';
  if (uuid.startsWith('VRX')) return uuid;
  if (typeof window === 'undefined') return "VRX-2026-" + uuid.substring(0, 4).toUpperCase();

  let mapStr = sessionStorage.getItem('vrx_case_map');
  let map: Record<string, string> = mapStr ? JSON.parse(mapStr) : {};
  if (map[uuid]) return map[uuid];

  const count = Object.keys(map).length + 1;
  const newId = "VRX-2026-" + count.toString().padStart(4, '0');
  map[uuid] = newId;
  sessionStorage.setItem('vrx_case_map', JSON.stringify(map));
  return newId;
}
