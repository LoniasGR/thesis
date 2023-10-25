import React from 'react';
import PropTypes from 'prop-types';

import './Overlay.css';

function Overlay({ setShow }) {
  return (
    <div
      role="presentation"
      className="overlay"
      onClick={() => setShow(false)}
      onKeyDown={() => setShow(false)}
    >
      <div className="overlay-inside">
        <p className="overlay-text">
          Σκοπός αυτής της ιστοσελίδας είναι η συλλογή δεδομένων σχετικά με το ποιές συστάσεις
          είναι καλές και ποιές όχι. Το σύστημα παράγει αυτόματα τυχαίους διαλόγους, από τους
          οποίος κρατήσαμε μόνο τα ερωτήματα του χρήστη. Μετά από κάποιο αριθμό διαλόγων, η
          ΘΕΑΝΩ παράγει μια πρόταση για συνέχεια της συζήτησης. Εσείς πρέπει να αξιολογήσετε
          την ποιότητα της πρότασης της Θεανώς. Μπορείτε να χρησιμοποιήσετε το πληκτρολόγιο
          ή το ποντίκι.
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
