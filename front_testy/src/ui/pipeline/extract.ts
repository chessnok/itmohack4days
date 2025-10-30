import { ExtractionResult, UploadedDoc } from './types';

// Very naive extractor: tries to read INN/KPP/name from file name or text
export async function extractPartiesFromDocs(docs: UploadedDoc[]): Promise<ExtractionResult[]> {
	return docs.map((d): ExtractionResult => {
		const text = (d.content ?? d.name).toLowerCase();
		const innMatch = text.match(/\b(\d{10})\b/);
		const kppMatch = text.match(/kpp[_\s-]?(\d{9})/);
		// Avoid Unicode property escapes for build compatibility; match Cyrillic/Latin letters
		const nameMatch =
			text.match(/ooo\s+([A-Za-zА-Яа-яЁё\s\"\']+)/) ||
			text.match(/ип\s+([A-Za-zА-Яа-яЁё\s\"\']+)/);
		return {
			documentId: d.id,
			party: {
				inn: innMatch?.[1],
				kpp: kppMatch?.[1],
				name: nameMatch?.[1]?.trim(),
			},
		};
	});
}


