export let backendURL: string;

if (import.meta.env.PROD) {
  backendURL = "http://localhost:8104";
} else {
  backendURL = "http://localhost:8006";
}

export const comparisonURL = `${backendURL}/comparison`;
export const responseURL = `${backendURL}/selection`;
