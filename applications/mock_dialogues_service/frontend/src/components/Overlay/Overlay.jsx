import React from 'react';
import PropTypes from 'prop-types';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';

import './Overlay.css';
import UserPrompt from '../UserPrompt/UserPrompt';

function Overlay({ setShow }) {
  const deactivateOverlay = (e) => {
    e.stopPropagation();
    setShow(false);
  };

  const elemRef = React.useRef();
  React.useEffect(() => {
    const overlayElem = elemRef.current;

    overlayElem.addEventListener('keydown', deactivateOverlay);

    return () => {
      overlayElem.removeEventListener('keydown', deactivateOverlay);
    };
  });

  return (
    <div
      ref={elemRef}
      role="presentation"
      className="overlay"
      onClick={deactivateOverlay}
    >
      <div className="overlay-inside">
        <h1>Οδηγίες χρήσης</h1>
        <p>
          Αυτή η σελίδα δημιουργήθηκε ως μέρος της διπλωματικής μου.
        </p>
        <p>
          Σκοπός της είναι η συλλογή δεδομένων σχετικά με το ποιές συστάσεις
          είναι καλές και ποιές όχι. Στις κάρτες παρουσιάζονται διάλογοι μεταξύ ενός φανταστικού
          χρήστη και της
          {' '}
          <span className="bold">Θεανώς, ενός ψηφιακού βοηθού για τον COVID-19</span>
          . Οι διάλογοι έχουν
          δημιουργηθεί τυχαία (δεν είναι πραγματικοί διάλογοι δηλαδή, οπότε μπορεί να μην βγάζουν
          απόλυτα νοήμα).
        </p>
        <p>
          <span className="bold">
            Κλικάροντας
            πάνω στις ερωτήσεις του χρήστη
            (
            <ArrowRightIcon sx={{ marginBottom: '-0.4rem' }} />
            )
            , εμφανίζονται οι απαντήσεις από την Θεανώ.
          </span>
          <p>
            Για παράδειγμα:
            <ul>
              <UserPrompt description="Παράδειγμα ερωτησης" response="παράδειγμα απάντησης" demonstrate className="override-prompt" />
            </ul>
          </p>
          Μετά από κάποιο αριθμό διαλόγων, η Θεανώ παράγει μια πρόταση για συνέχεια της συζήτησης.
          Εσείς καλείστε να αξιολογήσετε την ποιότητα της πρότασης της Θεανώς.
        </p>
        <p>
          Μπορείτε να χρησιμοποιήσετε το πληκτρολόγιο ή το ποντίκι.
          Μπορείτε επίσης να σύρετε δεξιά ή αριστερά τις κάρτες.
        </p>
        <p>Καντε κλικ για να συνεχίσετε.</p>
      </div>
    </div>
  );
}

Overlay.propTypes = {
  setShow: PropTypes.func.isRequired,
};

export default Overlay;
