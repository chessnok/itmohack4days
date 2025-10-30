import { DocumentSummary, EnrichmentResult, Finding, PipelineOutput } from './types';

export function makeDocSummaries(enriched: EnrichmentResult[], findings: Finding[]): DocumentSummary[] {
	return enriched.map(e => {
		const docFindings = findings.filter(f => f.documentId === e.documentId);
		const problems = docFindings.map(f => `${iconFor(f.severity)} ${f.message}`).join('; ') || 'Замечаний нет';
		const line = `${e.party.fullName ?? e.party.name ?? 'Неизвестный контрагент'} — ИНН ${e.party.inn ?? '—'}; ${problems}`;
		return { documentId: e.documentId, text: line };
	});
}

export function makeDealSummary(output: PipelineOutput): string {
	const total = output.extractions.length;
	const errors = output.findings.filter(f => f.severity === 'error').length;
	const warns = output.findings.filter(f => f.severity === 'warn').length;
	return `Обработано документов: ${total}. Ошибки: ${errors}, предупреждения: ${warns}.`;
}

function iconFor(level: Finding['severity']): string {
	switch (level) {
		case 'error': return '❌';
		case 'warn': return '⚠️';
		default: return 'ℹ️';
	}
}


