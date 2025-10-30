export type Company = { id: string; name: string };
export type Deal = { id: string; companyId: string; number: string };
export type DocumentItem = {
	id: string;
	dealId: string;
	title: string;
	type: string;
	date: string;
	amount: string;
	status: 'Проверено' | 'Черновик' | 'Отправлено';
	previewUrl: string;
};

export type MockData = {
	companies: Company[];
	deals: Deal[];
	documents: DocumentItem[];
};

export function loadMock(): MockData {
	const companies: Company[] = [
		{ id: 'c1', name: 'ООО "Альфа"' },
		{ id: 'c2', name: 'ООО "Вектор Плюс"' },
		{ id: 'c3', name: 'ООО "ТехСнаб"' },
	];
	const deals: Deal[] = [
		{ id: 'd1', companyId: 'c1', number: '199' },
		{ id: 'd2', companyId: 'c1', number: '214' },
		{ id: 'd3', companyId: 'c2', number: '124' },
	];
	const documents: DocumentItem[] = [
		{
			id: 'doc1',
			dealId: 'd1',
			title: 'Платежное_поручение_3145.pdf',
			type: 'Платежное поручение',
			date: '25.10.2025',
			amount: '15 312 ₽',
			status: 'Проверено',
			previewUrl: 'https://dummyimage.com/900x1200/ffffff/7f7f7f.png&text=%D0%9F%D0%9B%D0%90%D0%A2%D0%95%D0%96%D0%9D%D0%9E%D0%95+%D0%9F%D0%9E%D0%A0%D0%A3%D0%A7%D0%95%D0%9D%D0%98%D0%95',
		},
		{
			id: 'doc2',
			dealId: 'd1',
			title: 'Договор_№118_ООО_Альфа.pdf',
			type: 'Договор',
			date: '12.09.2016',
			amount: '—',
			status: 'Черновик',
			previewUrl: 'https://dummyimage.com/900x1200/f8f8f8/7f7f7f.png&text=%D0%94%D0%9E%D0%93%D0%9E%D0%92%D0%9E%D0%A0',
		},
		{
			id: 'doc3',
			dealId: 'd2',
			title: 'Счет-фактура_№893.pdf',
			type: 'Счет-фактура',
			date: '10.10.2025',
			amount: '250 000 ₽',
			status: 'Отправлено',
			previewUrl: 'https://dummyimage.com/900x1200/ffffff/7f7f7f.png&text=%D0%A1%D0%A7%D0%95%D0%A2-%D0%A4%D0%90%D0%9A%D0%A2%D0%A3%D0%A0%D0%90',
		},
	];
	return { companies, deals, documents };
}


