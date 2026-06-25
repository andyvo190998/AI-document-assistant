import { HttpAgent } from "@ag-ui/client";
import { CopilotRuntime, createCopilotRuntimeHandler } from "@copilotkit/runtime/v2";

const backendUrl = process.env.BACKEND_URL;

if (!backendUrl) {
	throw new Error("BACKEND_URL is not defined");
}

const runtime = new CopilotRuntime({
	agents: {
		default: new HttpAgent({
			url: `${backendUrl}/agent`,
		}),
	},
});

const handler = createCopilotRuntimeHandler({
	runtime,
	basePath: "/api/copilotkit",
});

export { handler as GET, handler as POST };
