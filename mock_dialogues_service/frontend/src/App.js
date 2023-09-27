import React, { useState, useEffect, useCallback } from 'react';
import SwipeableCard from './components/SwipeableCard/SwipeableCard';
import { GENERATE_URL } from './utils/urls';
import './App.css';
import Loader from './components/Loader/Loader';
import ArrowSVG from './components/ArrowSVG/ArrowSVG';


const App = () => {
  const [dialogues, setDialogues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
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
    }
    else {
      arr[index] = null;
    }
  }

  const updateCurrentIndex = (val) => {
    console.log("Updating to " + val);
    setCurrentIndex(val);
  }

  const swipe = useCallback(async (dir) => {
    const refs = getRefs();
    console.log(refs, currentIndex);
    await refs[currentIndex].swipe(dir) // Swipe the card!
    updateCurrentIndex(currentIndex - 1);
  }, [currentIndex]);


  const fetchData = () => {
    fetch(`${GENERATE_URL}?dialogues=5`, {
      method: "GET",
      mode: "cors",
      redirect: 'follow',
    })
      .then(response => response.json())
      .then(data => {
        setDialogues(data);
      })
      .catch(error => {
        console.error('Error fetching dialogues:', error);
      });
  }

  const handleArrowPress = useCallback((event) => {
    if (event.key === 'ArrowRight') {
      swipe('right');

    }
    if (event.key === 'ArrowLeft') {
      swipe('left');
    }
  }, [swipe]);


  useEffect(() => {
    // Fetch dialogues from the backend API
    fetchData();
    setLoading(false);
    updateCurrentIndex(dialogues.length - 1);
  }, [dialogues.length])

  useEffect(() => {
    // Add event listener when the component mounts
    document.addEventListener('keydown', handleArrowPress);

    // Clean up the event listener when the component unmounts
    return () => {
      document.removeEventListener('keydown', handleArrowPress);
    };
  }, [handleArrowPress]);

  useEffect(() => {
    if (currentIndex === -1) {
      setLoading(true);
      fetchData();
      setLoading(false);
      setCurrentIndex(dialogues.length - 1);
    }
  }, [currentIndex, dialogues.length]);

  return (
    <>
      <h1>Αξιολόγηση Προτάσεων</h1>
      <p className='legend'>
        <ArrowSVG /> Όχι, <ArrowSVG right /> Ναι </p>
      <main>
        {loading ? <Loader /> :
          dialogues.map((dialogue, i) => (
            <SwipeableCard
              ref={(el) => setRefs(el, i)}
              key={dialogue.uid}
              dialogueData={dialogue}
              swipe={swipe}
            />
          ))}
      </main>
    </>
  );
};

export default App;
