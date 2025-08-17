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

export const push_api_error = (err: any, default_title: string) => {
	const msg = { color: 'danger', title: default_title, message: 'An Error Occured!' };
	if (typeof err.detail == 'string') {
		msg.message = err.detail;
	}
	push_message(msg);
};
