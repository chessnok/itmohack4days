import { EnrichmentResult, ExtractionResult } from './types';

const DADATA_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party';

export async function enrichWithDadata(
	items: ExtractionResult[],
	token: string | undefined
): Promise<EnrichmentResult[]> {
	const headers: HeadersInit = token
		? { 'Content-Type': 'application/json', Authorization: `Token ${token}` }
		: { 'Content-Type': 'application/json' };

	async function queryOne(item: ExtractionResult): Promise<EnrichmentResult> {
		if (!token || !item.party.inn) {
			// fallback mock enrichment
			return {
				documentId: item.documentId,
				party: {
					...item.party,
					validatedInn: Boolean(item.party.inn && item.party.inn.length === 10),
					fullName: item.party.name || 'ООО «Неизвестно»',
					status: 'ACTIVE',
					founded: '2016-09-12',
					okved: '62.01',
				},
			};
		}
		try {
			const body = JSON.stringify({ query: item.party.inn });
			const res = await fetch(DADATA_URL, { method: 'POST', headers, body });
			const json = await res.json();
			const s = json?.suggestions?.[0]?.data;
			return {
				documentId: item.documentId,
				party: {
					...item.party,
					validatedInn: Boolean(s?.inn === item.party.inn),
					fullName: s?.name?.full_with_opf ?? s?.name?.short_with_opf,
					status: s?.state?.status?.toUpperCase(),
					founded: s?.state?.registration_date
						? new Date(s.state.registration_date).toISOString().slice(0, 10)
						: undefined,
					okved: s?.okved,
				},
			};
		} catch {
			return {
				documentId: item.documentId,
				party: { ...item.party },
			};
		}
	}

	return Promise.all(items.map(queryOne));
}


