import React, { useCallback, forwardRef, useState } from 'react'
import TinderCard from 'react-tinder-card';
import { EVALUATE_URL } from '../../utils/urls';

import './SwipeableCard.css';

const SwipeableCard = forwardRef(function SwipeableCard({ dialogueData, swipe }, ref) {
  const { user, user_intents, suggestions, suggestion_intent } = dialogueData;
  const [hidden, setHidden] = useState(false);
  const hide = hidden ? 'hidden' : '';

  const handleResponse = useCallback(
    (isRelevant) => {
      const data = { user: user_intents, suggestion: suggestion_intent, answer: isRelevant };
      fetch(EVALUATE_URL, {
        method: "POST",
        body: JSON.stringify(data),
        mode: 'cors',
        headers: {
          "Content-type": "application/json",
          'Access-Control-Allow-Origin': '*'
        },
      }).catch((err) => {
        console.error(err);
      });
    },
    [user_intents, suggestion_intent],
  );

  const handleOnCardLeftScreen = (dir) => {
    setHidden(true);
    const relevant = dir === "right" ? true : false;
    handleResponse(relevant);
  }


  return (
    <TinderCard
      className={`card swipe ${hide}`}
      ref={ref}
      onCardLeftScreen={handleOnCardLeftScreen}
    >
      <ul>
        {user.map((item, index) => (
          <li key={item}><span className="bold">User said:</span> {item}</li>
        ))}
      </ul>

      <p><span className='bold'>THEANO suggests: </span>{suggestions}</p>

      <div>
        <p className='bold'>Was the suggestion useful?</p>
        <div className='swipableCardsButtons'>
          <button onClick={() => swipe("left")}>
            No
          </button>
          <button onClick={() => swipe("right")}>
            Yes
          </button>
        </div>
      </div>
    </TinderCard>
  )
});



export default SwipeableCard;
