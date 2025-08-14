import type { SiteInfo, UserPublic } from './client';

export const site_info = $state<{ val: SiteInfo | undefined }>({ val: undefined });
export const user_info = $state<{ val: UserPublic | undefined }>({ val: undefined });
