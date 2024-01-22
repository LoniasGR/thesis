import {
  useState, useRef, useCallback, useEffect,
} from 'react';
import HelpIcon from '@mui/icons-material/Help';

import { IconButton } from '@mui/material';
import Header from '../../components/Header/Header';
import SwipeableCard from '../../components/SwipeableCard/SwipeableCard';
import { GENERATE_URL } from '../../utils/urls';

import Loader from '../../components/Loader/Loader';
import Overlay from '../../components/Overlay/Overlay';
import useFetch from '../../hooks/useFetch';
import Footer from '../Footer/Footer';

import './Main.css';

function Main() {
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

  const onSwipe = () => {
    setCurrentIndex(currentIndex - 1);
  };

  const swipe = useCallback(async (dir) => {
    const refs = getRefs();
    await refs[currentIndex].swipe(dir); // Swipe the card!
  }, [currentIndex]);

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
      setCurrentIndex(dialogues.length - 1);
    }
  }, [loading, dialogues]);

  useEffect(() => {
    if (currentIndex === -1) {
      setBatch((prevState) => prevState + 1);
    }
  }, [currentIndex]);

  useEffect(() => {
    const handleArrowPress = (event) => {
      event.preventDefault();

      if (event.key === 'ArrowRight') {
        swipe('right');
      }
      if (event.key === 'ArrowLeft') {
        swipe('left');
      }
    };

    if (!showOverlay) {
    // Add event listener when the component mounts
      document.addEventListener('keydown', handleArrowPress);
    }
    // Clean up the event listener when the component unmounts
    return () => {
      document.removeEventListener('keydown', handleArrowPress);
    };
  });

  return (
    <>
      <IconButton className="help-button" onClick={() => setShowOverlay(true)}><HelpIcon /></IconButton>
      <main className="main-content">
        {showOverlay ? <Overlay setShow={setShowOverlay} /> : null}
        <Header />
        {error ? <p>{error}</p> : null}
        <section className="card-section">
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
          <Footer swipe={swipe} />
        )}
      </main>
    </>
  );
}

export default Main;
