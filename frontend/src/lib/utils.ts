import { type ClassValue, clsx } from "clsx";

/**
 * Merges Tailwind class names
 */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}
