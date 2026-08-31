import raw from './groups.json';

export type Group = {
  slug: string;
  name: string;
  tagline: string;
  icon: string;
  iconCp: string;
  url: string;
};

function cpToChar(cp: string): string {
  return String.fromCodePoint(parseInt(cp.slice(2), 16));
}

const BRAND_ENTRIES = [
  {
    slug: 'mit',
    name: 'MIT',
    tagline: '2023 MIT parent-brand wordmark (M·I·T)',
    iconCp: 'U+E030',
    url: 'https://brand.mit.edu/logos-marks/mit-logo',
  },
  {
    slug: 'media-lab',
    name: 'Media Lab',
    tagline: 'Official Media Lab 7×7 geometric mark',
    iconCp: 'U+E031',
    url: 'https://www.media.mit.edu/',
  },
] as const;

export const BRAND_SYMBOLS: Group[] = BRAND_ENTRIES.map((g) => ({
  ...g,
  icon: cpToChar(g.iconCp),
}));

export const RESEARCH_GROUPS: Group[] = raw
  .map((g) => ({
    ...g,
    icon: cpToChar(g.iconCp),
  }))
  .sort((a, b) => a.name.localeCompare(b.name, 'en', { sensitivity: 'base' }));

/** MIT & Media Lab first, then research groups A–Z. */
export const GROUPS: Group[] = [...BRAND_SYMBOLS, ...RESEARCH_GROUPS];

export const GROUP_ICON_STRING = GROUPS.map((g) => g.icon).join('');
