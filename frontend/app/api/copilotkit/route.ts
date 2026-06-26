import { createCopilotRuntimeHandler } from "@copilotkit/runtime/v2";

import { runtime } from "./runtime";

const handler = createCopilotRuntimeHandler({
	runtime,
	basePath: "/api/copilotkit",
	mode: "single-route",
});

export const GET = handler;
export const POST = handler;
export const OPTIONS = handler;
