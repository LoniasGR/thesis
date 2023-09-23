import React, { useState, useEffect, useMemo, useCallback } from 'react';
import SwipeableCard from './components/SwipeableCard/SwipeableCard';
import { GENERATE_URL } from './utils/urls';
import './App.css';
import Loader from './components/Loader/Loader';


const App = () => {
  const [dialogues, setDialogues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const childRefs = useMemo(
    () =>
      Array(dialogues.length)
        .fill(0)
        .map((i) => React.createRef()),
    [dialogues.length]
  )

  const updateCurrentIndex = (val) => {
    console.log("Updating to " + val);
    setCurrentIndex(val);
  }

  const swipe = useCallback(async (dir) => {
    await childRefs[currentIndex].current.swipe(dir) // Swipe the card!
    updateCurrentIndex(currentIndex - 1);
  }, [childRefs, currentIndex]);


  const fetchData = () => {
    fetch(GENERATE_URL, {
      method: "GET",
      mode: "no-cors",
      redirect: 'follow',
    })
    .then(response => response.json())
    .then(data => {
      setDialogues(data);
      setLoading(false);
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
    },[swipe]);


    useEffect(() => {
      // Fetch dialogues from the backend API
      fetchData();
      setLoading(false);
      updateCurrentIndex(dialogues.length - 1);
    },[dialogues.length])

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
    }
  }, [currentIndex]);

  return (
    <>
      {!loading && (
        <>
          <h1>Αξιολόγηση Προτάσεων</h1>
          {loading && <Loader />}
          {dialogues.map((dialogue, index) => (
            <>
          <SwipeableCard
            ref={childRefs[index]}
            key={dialogue}
            dialogueData={dialogue}
            swipe={swipe}
          />
          </>
            ))}
        </>
      )
      }
    </>
  );
};

export default App;
