import React, {
  useState, useEffect, useCallback, useRef,
} from 'react';
import SwipeableCard from './components/SwipeableCard/SwipeableCard';
import { GENERATE_URL } from './utils/urls';

import Loader from './components/Loader/Loader';
import ArrowSVG from './components/ArrowSVG/ArrowSVG';
import Overlay from './components/Overlay/Overlay';
import useFetch from './hooks/useFetch';

import './App.css';

function App() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showOverlay, setShowOverlay] = useState(true);
  const [batch, setBatch] = useState(0);
  const childRefs = useRef(null);

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

  const updateCurrentIndex = useCallback((val) => {
    setCurrentIndex(val);
  }, []);

  const swipe = useCallback(async (e, dir) => {
    e.preventDefault();
    const refs = getRefs();
    await refs[currentIndex].swipe(dir); // Swipe the card!
  }, [currentIndex]);

  const onSwipe = useCallback(() => {
    updateCurrentIndex(currentIndex - 1);
  }, [updateCurrentIndex, currentIndex]);

  const handleArrowPress = useCallback((event) => {
    if (event.key === 'ArrowRight') {
      swipe('right');
    }
    if (event.key === 'ArrowLeft') {
      swipe('left');
    }
  }, [swipe]);

  const { data: dialogues, error, loading } = useFetch(
    `${GENERATE_URL}?dialogues=5`,
    {
      method: 'GET',
      mode: 'cors',
      redirect: 'follow',
    },
    [batch],
  );

  useEffect(() => {
    if (!loading) {
      updateCurrentIndex(dialogues.length - 1);
    }
  }, [dialogues]);

  useEffect(() => {
    if (currentIndex === -1) {
      setBatch(batch + 1);
    }
  }, [currentIndex]);

  useEffect(() => {
    // Add event listener when the component mounts
    document.addEventListener('keydown', handleArrowPress);

    // Clean up the event listener when the component unmounts
    return () => {
      document.removeEventListener('keydown', handleArrowPress);
    };
  }, [handleArrowPress]);

  return (
    <>
      {showOverlay ? <Overlay setShow={setShowOverlay} /> : null}
      <h1>Αξιολόγηση Προτάσεων</h1>
      <p className="legend">
        <ArrowSVG />
        Όχι
        <ArrowSVG right />
        Ναι
      </p>
      <main>
        {error ? <p>{error}</p> : null}
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
        {!error
        && (
        <div className="bottom">
          <p className="bold">Ήταν η πρόταση σχετική/χρήσιμη;</p>
          <div className="swipableCardsButtons">
            <button type="button" onClick={(e) => swipe(e, 'left')}>
              ΟΧΙ
            </button>
            <button
              type="button"
              onClick={(e) => swipe(e, 'right')}
            >
              ΝΑΙ
            </button>
          </div>
        </div>
        )}
      </main>
    </>
  );
}

export default App;
