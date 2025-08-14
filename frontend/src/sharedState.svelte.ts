import type { SiteInfo } from './client';

export const site_info = $state<{ val: SiteInfo | undefined }>({ val: undefined });
