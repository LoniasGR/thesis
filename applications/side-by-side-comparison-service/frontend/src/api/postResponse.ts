import axios from "axios";
import { ResponseSelection } from "../models/response";
import { responseURL } from "../utils/constants";

export function postResponse(uuid: string, resp: ResponseSelection) {
  return axios.post(responseURL, {
    uuid: uuid,
    response: resp,
  });
}
