let BASE_URL;

if (import.meta.env.PROD) {
  BASE_URL = 'https://test.lavdelas.me';
} else {
  BASE_URL = 'http://localhost:8000';
}

const GENERATE_URL = `${BASE_URL}/generate`;
const EVALUATE_URL = `${BASE_URL}/evaluate`;

export {
  GENERATE_URL,
  EVALUATE_URL,
};
