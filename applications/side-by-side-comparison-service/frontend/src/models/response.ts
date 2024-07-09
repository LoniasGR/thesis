export enum ResponseSelection {
  RANDOM = 1,
  SMART = 2,
}

export interface Response {
  uuid: string;
  response: ResponseSelection;
}
