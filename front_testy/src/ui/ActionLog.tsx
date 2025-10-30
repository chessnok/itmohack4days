import React, { useState } from 'react';

export const ActionLog: React.FC = () => {
	const [messages, setMessages] = useState<string[]>([
		'Открой все документы по сделке 199',
		'Открываю все документы по сделке №А-199 ООО "Альфа"',
		'В платёжном поручении проверь реквизиты',
		'Проверяю реквизиты... Реквизиты введены верно',
		'Отправь проверенный документ клиенту',
		'Документ отправлен',
	]);
	const [input, setInput] = useState('');

	function send() {
		if (!input.trim()) return;
		setMessages(prev => [...prev, input.trim()]);
		setInput('');
	}

	return (
		<section className="action-log">
			<div className="log">
				{messages.map((m, i) => (
					<div key={i} className={i % 2 === 0 ? 'msg user' : 'msg bot'}>
						{m}
					</div>
				))}
			</div>
			<div className="composer">
				<input
					placeholder="Введите запрос..."
					value={input}
					onChange={e => setInput(e.target.value)}
					onKeyDown={e => e.key === 'Enter' && send()}
				/>
				<button onClick={send}>➤</button>
			</div>
		</section>
	);
};


