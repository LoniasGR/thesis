import React from 'react'

import './Overlay.css';

function Overlay({ showOverlay, setShowOverlay }) {
  return (
    <>
      {
        showOverlay ?
          (
            <div className='overlay' onClick={() => setShowOverlay(false)}>
              <div className='overlay-inside'>
                <p className='overlay-text'>Σκοπός αυτής της ιστοσελίδας είναι η συλλογή δεδομένων σχετικά με το ποιές συστάσεις είναι καλές και ποιές όχι.
                  Το σύστημα παράγει αυτόματα τυχαίους διαλόγους, από τους οποίος κρατήσαμε μόνο τα ερωτήματα του χρήστη. Μετά από κάποιο αριθμό διαλόγων,
                  η ΘΕΑΝΩ παράγει μια πρόταση για συνέχεια της συζήτησης. Εσείς πρέπει να αξιολογήσετε την ποιότητα της πρότασης της Θεανώς.
                  Μπορείτε να χρησιμοποιήσετε το πληκτρολόγιο ή το ποντίκι.</p>

                <p className='overlay-text'>Καντε κλικ για να συνεχίσετε.</p>
              </div>
            </div >
          )
          : null
      }
    </>
  )
}

export default Overlay;
