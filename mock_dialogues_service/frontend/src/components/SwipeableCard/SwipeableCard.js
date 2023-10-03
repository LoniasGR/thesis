import React, { useCallback, forwardRef, useState } from 'react'
import TinderCard from 'react-tinder-card';
import { EVALUATE_URL } from '../../utils/urls';

import './SwipeableCard.css';

const SwipeableCard = forwardRef(function SwipeableCard({ dialogueData, onSwipe, swipe }, ref) {
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
      preventSwipe={["up", "down"]}
      onSwipe={onSwipe}
      swipeRequirementType='position'
    >
      <ul>
        {user.map((item, index) => (
          <li key={item}><span className="bold">Ο χρήστης ρωτάει:</span> {item}</li>
        ))}
      </ul>

      <p className='prompt'><span className='bold'>Η ΘΕΑΝΩ προτείνει: </span>{suggestions}</p>

      <div>
        <p className='bold prompt'>Ήταν η πρόταση σχετική/χρήσιμη;</p>
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
