import type { Metadata } from "next";

import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
	title: "PDF AI Assistant",
	description: "Upload a PDF, summarize it, and ask questions.",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body><Providers>{children}</Providers></body>
		</html>
	);
}
