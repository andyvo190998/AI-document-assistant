import { HttpAgent } from "@ag-ui/client";
import { CopilotRuntime } from "@copilotkit/runtime/v2";

const backendUrl = process.env.BACKEND_URL;

if (!backendUrl) {
	throw new Error("BACKEND_URL is not defined");
}

export const runtime = new CopilotRuntime({
	agents: {
		default: new HttpAgent({
			url: `${backendUrl}/agent`,
		}),
	},
});
