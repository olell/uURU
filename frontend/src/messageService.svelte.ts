interface Message {
	color: 'primary' | 'success' | 'warning' | 'danger';
	title: string;
	message: string;
}

interface MessageWithKey extends Message {
	key: number;
}

export const messages = $state<MessageWithKey[]>([]);
let msg_count = 0;

export const push_message = (msg: Message) => {
	const key = ++msg_count;
	const _msg = { ...msg, key };
	messages.push(_msg);
	setTimeout(() => {
		const idx = messages.findIndex((e) => e.key === _msg.key);
		messages.splice(idx, 1);
	}, 5000);
};
