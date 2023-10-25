import React, { useCallback, forwardRef, useState } from 'react';
import PropTypes from 'prop-types';
import TinderCard from 'react-tinder-card';
import { EVALUATE_URL } from '../../utils/urls';

import './SwipeableCard.css';

const SwipeableCard = forwardRef(({ dialogueData, onSwipe }, ref) => {
  const {
    uuid, user, user_intents: userIntents, suggestions, suggestion_intent: suggestionIntent,
  } = dialogueData;
  const [hidden, setHidden] = useState(false);
  const hide = hidden ? 'hidden' : '';

  const handleResponse = useCallback(
    (isRelevant) => {
      const data = {
        uuid,
        answer: isRelevant,
      };
      fetch(EVALUATE_URL, {
        method: 'POST',
        body: JSON.stringify(data),
        mode: 'cors',
        headers: {
          'Content-type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      }).catch((err) => {
        // eslint-disable-next-line no-console
        console.error(err);
      });
    },
    [userIntents, suggestionIntent],
  );

  const handleOnCardLeftScreen = (dir) => {
    setHidden(true);
    const relevant = dir === 'right';
    handleResponse(relevant);
  };

  return (
    <TinderCard
      className={`card swipe ${hide}`}
      ref={ref}
      onCardLeftScreen={handleOnCardLeftScreen}
      preventSwipe={['up', 'down']}
      onSwipe={onSwipe}
      swipeRequirementType="position"
    >
      <ul>
        {user.map((item) => (
          <li key={`${uuid}-${item}`}>
            <span className="bold">Ο χρήστης ρωτάει: </span>
            {item}
          </li>
        ))}
      </ul>

      <p className="prompt">
        <span className="bold">Η ΘΕΑΝΩ προτείνει: </span>
        {suggestions}
      </p>
    </TinderCard>
  );
});

SwipeableCard.propTypes = {
  dialogueData: PropTypes.shape({
    uuid: PropTypes.string,
    user: PropTypes.arrayOf(PropTypes.string),
    user_intents: PropTypes.arrayOf(PropTypes.string),
    suggestions: PropTypes.string,
    suggestion_intent: PropTypes.string,
  }).isRequired,
  onSwipe: PropTypes.func.isRequired,
};

export default SwipeableCard;
