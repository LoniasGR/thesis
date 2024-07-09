export interface Comparison {
  uuid: string;
  response: null;
  user: User[];
  random_intent: string;
  random_utterance: string;
  smart_intent: string;
  smart_utterance: string;
}

export interface User {
  intent: string;
  description: string;
  response: string;
}
