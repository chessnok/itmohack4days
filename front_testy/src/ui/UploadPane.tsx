import React from 'react';
import { UploadedDoc } from './pipeline/types';

type Props = {
	uploaded: UploadedDoc[];
	onUpload: (docs: UploadedDoc[]) => void;
};

export const UploadPane: React.FC<Props> = ({ uploaded, onUpload }) => {
	function onFiles(files: FileList | null) {
		if (!files) return;
		const docs: UploadedDoc[] = Array.from(files).map((f, i) => ({ id: `${Date.now()}-${i}`, name: f.name }));
		onUpload([...uploaded, ...docs]);
	}

	return (
		<div className="upload-pane">
			<h3>Загрузка документов</h3>
			<input type="file" multiple onChange={e => onFiles(e.target.files)} />
			<ul>
				{uploaded.map(d => (
					<li key={d.id}>{d.name}</li>
				))}
			</ul>
		</div>
	);
};


