import React from 'react';
import { Finding } from './pipeline/types';

type Props = { findings: Finding[]; dealSummary?: string; };

export const FindingsPane: React.FC<Props> = ({ findings, dealSummary }) => {
	return (
		<section className="info-pane">
			<h3>Потенциальные ошибки и улучшения</h3>
			{dealSummary && <div style={{marginBottom:8}}>{dealSummary}</div>}
			{findings.length === 0 ? (
				<div className="muted">Замечаний нет</div>
			) : (
				<ul>
					{findings.map(f => (
						<li key={f.id}>
							{f.severity === 'error' ? '❌' : f.severity === 'warn' ? '⚠️' : 'ℹ️'} {f.message}
						</li>
					))}
				</ul>
			)}
		</section>
	);
};


