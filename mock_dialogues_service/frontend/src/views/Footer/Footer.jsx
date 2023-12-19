import { Button } from '@mui/material';
import PropTypes from 'prop-types';

import './Footer.css';

function Footer({ swipe }) {
  return (
    <div className="bottom">
      <p className="bold">Ήταν η πρόταση σχετική/χρήσιμη;</p>
      <div className="swipable-cards-buttons">
        <Button
          type="button"
          variant="contained"
          onClick={() => swipe('left')}
        >
          ΟΧΙ
        </Button>
        <Button
          variant="contained"
          type="button"
          onClick={() => swipe('right')}
        >
          ΝΑΙ
        </Button>
      </div>
    </div>
  );
}

Footer.propTypes = {
  swipe: PropTypes.func.isRequired,
};

export default Footer;
