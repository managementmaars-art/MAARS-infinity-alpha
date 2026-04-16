import { ProxyAgent, setGlobalDispatcher } from "undici";

export function setupProxy(): void {
  const proxyUrl = process.env.HTTP_PROXY || process.env.HTTPS_PROXY;
  if (!proxyUrl) {
    return;
  }

  const proxyAgent = new ProxyAgent(proxyUrl);
  setGlobalDispatcher(proxyAgent);
}
