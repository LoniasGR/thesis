import {
  useCallback, forwardRef, useState, useRef, useLayoutEffect,
} from 'react';
import PropTypes from 'prop-types';
import TinderCard from 'react-tinder-card';
import { EVALUATE_URL } from '../../utils/urls';

import './SwipeableCard.css';
import UserPrompt from '../UserPrompt/UserPrompt';

const SwipeableCard = forwardRef(({ dialogueData, onSwipe }, ref) => {
  const scrollRef = useRef();
  const {
    uuid, user, suggestion_utterance: suggestionUtterance,
  } = dialogueData;
  const [hidden, setHidden] = useState(false);

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
    [uuid],
  );

  const handleOnCardLeftScreen = (dir) => {
    setHidden(true);
    const relevant = dir === 'right';
    handleResponse(relevant);
  };

  useLayoutEffect(() => {
    let touchPosX;
    let touchPosY;
    const currentRef = scrollRef.current;
    let isPropagating = false;

    const onTouchMove = (e) => {
      const newTouchPosY = e.changedTouches[0].clientY;
      const newTouchPosX = e.changedTouches[0].clientX;

      if (Math.abs(newTouchPosX - touchPosX) < 50) {
        if (!isPropagating) {
          e.stopPropagation();
        }
        e.preventDefault();
        currentRef.scrollTop -= 0.05 * (newTouchPosY - touchPosY);
      } else {
        isPropagating = true;
      }
    };

    const onTouchEnd = () => {
      currentRef.removeEventListener(('touchmove'), onTouchMove);
      currentRef.removeEventListener(('touchend'), onTouchEnd);
    };

    const onTouchStart = (e) => {
      isPropagating = false;
      e.preventDefault();
      touchPosY = e.changedTouches[0].clientY;
      touchPosX = e.changedTouches[0].clientX;

      currentRef.addEventListener(('touchmove'), onTouchMove);
      currentRef.addEventListener(('touchend'), onTouchEnd);
    };

    currentRef.addEventListener(('touchstart'), onTouchStart);

    return () => {
      currentRef.removeEventListener(('touchstart'), onTouchStart);
    };
  }, [scrollRef]);

  return (
    <TinderCard
      className={`pressable swipe ${hidden ? 'hidden' : ''}`}
      ref={ref}
      onCardLeftScreen={handleOnCardLeftScreen}
      preventSwipe={['up', 'down']}
      onSwipe={onSwipe}
      swipeRequirementType="position"
    >
      <div className="card" ref={scrollRef}>
        <ul>
          {user.map((item) => (
            <UserPrompt key={`${uuid}-${item.intent}`} description={item.description} response={item.response} />
          ))}
        </ul>

        <p className="prompt">
          <span className="bold">Η ΘΕΑΝΩ προτείνει: </span>
          {suggestionUtterance}
        </p>
      </div>
    </TinderCard>
  );
});

SwipeableCard.propTypes = {
  dialogueData: PropTypes.shape({
    uuid: PropTypes.string,
    user: PropTypes.arrayOf(PropTypes.shape({
      intent: PropTypes.string,
      description: PropTypes.string,
      response: PropTypes.string,
    })),
    suggestion: PropTypes.string,
    suggestion_utterance: PropTypes.string,
  }).isRequired,
  onSwipe: PropTypes.func.isRequired,
};
SwipeableCard.displayName = 'SwipeableCard';
export default SwipeableCard;
