// Stub: send-to-readest conversion not available in this build
const workerContext: DedicatedWorkerGlobalScope = self as unknown as DedicatedWorkerGlobalScope;

workerContext.onmessage = (_event: MessageEvent<{ type: string }>) => {
  const response = { type: 'error', payload: { message: 'Conversion not available', code: 'unavailable' } };
  workerContext.postMessage(response);
};
