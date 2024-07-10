import { useAPI } from "../../hooks";
import { UserPrompt } from "../../components/UserPrompt/UserPrompt";
import { SelectionButton } from "../../components/SelectionButton";
import { Comparison } from "../../models/suggestion";

import "./Main.css";
import { comparisonURL } from "../../utils/constants";
import { ResponseSelection } from "../../models/response";
import { useState } from "react";

const Main = () => {
  const [counter, setCounter] = useState(0);
  const { data: d, loading: loading } = useAPI(comparisonURL, [counter]);
  const data: Comparison = d as unknown as Comparison;

  const incrCounter = () => {
    setCounter(counter + 1);
  };

  return (
    <>
      {!loading && (
        <>
          <h1 className="main-title">Σύγκριση προτάσεων</h1>
          <div className="dialogue-container">
            <ul className="dialogue">
              {data.user.map((u) => (
                <UserPrompt
                  key={u.intent}
                  description={u.description}
                  response={u.response}
                  initialExpansion={true}
                />
              ))}
            </ul>
          </div>
          <h2 className="selection">Ποιά πρόταση είναι πιο σχετική;</h2>
          <div className="suggestions-container">
            <SelectionButton
              uuid={data.uuid}
              selection={ResponseSelection.RANDOM}
              utterance={data.random_utterance}
              updateCounter={incrCounter}
            />
            <SelectionButton
              uuid={data.uuid}
              selection={ResponseSelection.SMART}
              utterance={data.smart_utterance}
              updateCounter={incrCounter}
            />
          </div>
        </>
      )}
    </>
  );
};

export default Main;
