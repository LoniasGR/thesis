import { ButtonBase } from "@mui/material";
import { ResponseSelection } from "../../models/response";
import { postResponse } from "../../api/postResponse";

import "./SelectionButton.css";

type SelectionButtonProps = {
  uuid: string;
  selection: ResponseSelection;
  utterance: string;
  updateCounter: () => void;
};

export function SelectionButton({
  uuid,
  selection,
  utterance,
  updateCounter,
}: SelectionButtonProps) {
  const onClick = () => {
    postResponse(uuid, selection)
      .then(() => updateCounter())
      .catch((e: unknown) => {
        console.error(e);
      });
  };

  return (
    <ButtonBase onClick={onClick} className="button-container">
      <p>{utterance}</p>
    </ButtonBase>
  );
}
