import React from 'react';
import { Button } from '@mui/material';

import Header from '../components/Header/Header';
import SwipeableCard from '../components/SwipeableCard/SwipeableCard';
import { GENERATE_URL } from '../utils/urls';

import Loader from '../components/Loader/Loader';
import Overlay from '../components/Overlay/Overlay';
import useFetch from '../hooks/useFetch';

import './Main.css';

function Main() {
  const [currentIndex, setCurrentIndex] = React.useState(0);
  const [showOverlay, setShowOverlay] = React.useState(true);
  const [batch, setBatch] = React.useState(0);
  const childRefs = React.useRef(null);

  function getRefs() {
    // Child refs is null
    if (!childRefs.current) {
      childRefs.current = [];
    }
    return childRefs.current;
  }

  function setRefs(el, index) {
    const arr = getRefs();
    if (el) {
      arr[index] = el;
    } else {
      arr[index] = null;
    }
  }

  const updateCurrentIndex = React.useCallback((val) => {
    setCurrentIndex(val);
  }, []);

  const swipe = React.useCallback(async (dir) => {
    const refs = getRefs();
    await refs[currentIndex].swipe(dir); // Swipe the card!
  }, [currentIndex]);

  const onSwipe = React.useCallback(() => {
    updateCurrentIndex(currentIndex - 1);
  }, [updateCurrentIndex, currentIndex]);

  const { data: dialogues, error, loading } = useFetch(
    `${GENERATE_URL}?dialogues=5`,
    {
      method: 'GET',
      mode: 'cors',
      redirect: 'follow',
    },
    [batch],
  );

  React.useEffect(() => {
    if (!loading) {
      updateCurrentIndex(dialogues.length - 1);
    }
  }, [loading, dialogues, updateCurrentIndex]);

  React.useEffect(() => {
    if (currentIndex === -1) {
      setBatch(batch + 1);
    }
  }, [batch, currentIndex]);

  React.useEffect(() => {
    const handleArrowPress = (event) => {
      event.preventDefault();

      if (event.key === 'ArrowRight') {
        swipe('right');
      }
      if (event.key === 'ArrowLeft') {
        swipe('left');
      }
    };

    // Add event listener when the component mounts
    document.addEventListener('keydown', handleArrowPress);

    // Clean up the event listener when the component unmounts
    return () => {
      document.removeEventListener('keydown', handleArrowPress);
    };
  });

  return (
    <>
      {showOverlay ? <Overlay setShow={setShowOverlay} /> : null}
      <Header />
      <main>
        {error ? <p>{error}</p> : null}
        <section>
          {loading ? <Loader />
            : (
              dialogues?.map((dialogue, i) => (
                <SwipeableCard
                  ref={(el) => setRefs(el, i)}
                  key={dialogue.uuid}
                  dialogueData={dialogue}
                  swipe={swipe}
                  onSwipe={onSwipe}
                />
              ))
            )}
        </section>
        {!error
        && (
        <div className="bottom">
          <p className="bold">Ήταν η πρόταση σχετική/χρήσιμη;</p>
          <div className="swipableCardsButtons">
            <Button
              type="button"
              variant="contained"
              onClick={(e) => swipe(e, 'left')}
            >
              ΟΧΙ
            </Button>
            <Button
              variant="contained"
              type="button"
              onClick={(e) => swipe(e, 'right')}
            >
              ΝΑΙ
            </Button>
          </div>
        </div>
        )}
      </main>
    </>
  );
}

export default Main;
