import React from 'react';
import PropTypes from 'prop-types';

import './Overlay.css';

function Overlay({ setShow }) {
  React.useEffect(() => {
    const deactivateOverlay = () => setShow(false);
    document.addEventListener('keydown', deactivateOverlay);

    return () => {
      document.removeEventListener('keydown', deactivateOverlay);
    };
  });

  return (
    <div
      role="presentation"
      className="overlay"
      onClick={() => setShow(false)}
    >
      <div className="overlay-inside">
        <h1>Οδηγίες χρήσης</h1>
        <p className="overlay-text">
          Αυτή η σελίδα δημιουργήθηκε ως μέρος της διπλωματικής μου.
        </p>
        <p className="overlay-text">
          Σκοπός της είναι η συλλογή δεδομένων σχετικά με το ποιές συστάσεις
          είναι καλές και ποιές όχι. Στις κάρτες παρουσιάζονται διάλογοι μεταξύ ενός φανταστικού
          χρήστη και της
          {' '}
          <span className="bold">Θεανώς, ενός ψηφιακού βοηθού για τον COVID-19</span>
          . Οι διάλογοι έχουν
          δημιουργηθεί τυχαία (δεν είναι πραγματικοί διάλογοι δηλαδή, οπότε μπορεί να μην βγάζουν
          απόλυτα νοήμα).
        </p>
        <p className="overlay-text">
          <span className="bold">
            Κλικάροντας
            πάνω στις ερωτήσεις του χρήστη, εμφανίζονται οι απαντήσεις από την Θεανώ.
          </span>
          {' '}
          Μετά από κάποιο αριθμό διαλόγων, η Θεανώ παράγει μια πρόταση για συνέχεια της συζήτησης.
          Εσείς καλείστε να αξιολογήσετε την ποιότητα της πρότασης της Θεανώς.
        </p>
        <p className="overlay-text">
          Μπορείτε να χρησιμοποιήσετε το πληκτρολόγιο ή το ποντίκι.
        </p>
        <p className="overlay-text">Καντε κλικ για να συνεχίσετε.</p>
      </div>
    </div>
  );
}

Overlay.propTypes = {
  setShow: PropTypes.func.isRequired,
};

export default Overlay;
