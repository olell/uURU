import { type PublicSettings, type UserPublic } from './client';

export const user_info = $state<{ val: UserPublic | undefined }>({ val: undefined });
export const settings = $state<{ val: PublicSettings | undefined }>({ val: undefined });

export const isMobile = $state({ val: false });
