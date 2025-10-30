import { EnrichmentResult, Finding } from './types';

export function validate(enriched: EnrichmentResult[]): Finding[] {
	const findings: Finding[] = [];
	for (const item of enriched) {
		const { party } = item;
		if (!party.inn) {
			findings.push({ id: `f-${item.documentId}-inn-missing`, severity: 'error', message: 'Не найден ИНН контрагента', documentId: item.documentId });
		}
		if (party.inn && party.inn.length !== 10) {
			findings.push({ id: `f-${item.documentId}-inn-len`, severity: 'error', message: 'ИНН должен состоять из 10 цифр', documentId: item.documentId });
		}
		if (party.status && party.status !== 'ACTIVE') {
			findings.push({ id: `f-${item.documentId}-status`, severity: 'warn', message: `Статус контрагента: ${party.status}`, documentId: item.documentId });
		}
		if (!party.okved) {
			findings.push({ id: `f-${item.documentId}-okved`, severity: 'info', message: 'OKVED не определён — проверьте соответствие виду деятельности', documentId: item.documentId });
		}
	}
	return findings;
}


