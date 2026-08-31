import { assets } from '$app/paths';
import { PUBLIC_SITE_URL } from '$env/static/public';

/** Set at build time via PUBLIC_SITE_URL (GitHub Actions / npm run build:pages). */
export const siteUrl = PUBLIC_SITE_URL.replace(/\/$/, '');

/** Absolute URL for a path under the site root (e.g. `/og.png`). */
export function absoluteUrl(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  if (siteUrl) return `${siteUrl}${normalized}`;
  return `${assets || ''}${normalized}`;
}
