export type UploadedDocument = {
	document_id: string;
	filename: string;
	page_count: number;
	chunk_count: number;
	summary: string;
};

type ApiErrorResponse = {
	detail?: string;
};

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

if (!backendUrl) {
	throw new Error("NEXT_PUBLIC_BACKEND_URL is not configured.");
}

export async function uploadDocument(file: File): Promise<UploadedDocument> {
	const formData = new FormData();
	formData.append("file", file);

	const response = await fetch(`${backendUrl}/api/documents/upload`, {
		method: "POST",
		body: formData,
	});

	if (!response.ok) {
		const error = (await response.json().catch(() => {})) as ApiErrorResponse;

		throw new Error(error.detail);
	}

	return (await response.json()) as UploadedDocument;
}

export async function deleteDocument(documentId: string) {
	const response = await fetch(`${backendUrl}/api/documents/${documentId}`, {
		method: "DELETE",
	});

	if (!response.ok) {
		throw new Error("The document could not be deleted.");
	}
}
