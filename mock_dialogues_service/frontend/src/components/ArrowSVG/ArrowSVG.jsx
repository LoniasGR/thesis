import React from 'react';
import PropTypes from 'prop-types';
import './ArrowSVG.css';

function ArrowSVG({ right }) {
  const classes = right ? 'right' : 'left';
  return (
    <svg className={classes} focusable="false" aria-hidden="false" role="img" viewBox="0 0 24 24" width="24px" height="24px" aria-labelledby="52a23891c7de781a">
      <g transform="translate(2 2) rotate(0 10 10)" fill="none" fillRule="evenodd">
        <path d="M5.368 11.041l1.227.985 1.785 1.433 1.226.984c.491.395.893.208.893-.413v-1.908c.743-.106 3.574-.444 4.198-.533.742-.106 1.29-.568 1.29-1.262v-.003c0-.695-.548-1.157-1.29-1.263-.624-.089-3.455-.427-4.198-.533V6.62c0-.621-.401-.807-.892-.413L8.38 7.19 6.595 8.624l-1.227.984c-.49.395-.49 1.04 0 1.433" fill="currentColor" fillRule="nonzero" />
        <rect stroke="currentColor" strokeWidth="2.5" width="20" height="20" rx="3" />
      </g>
      <title id="52a23891c7de781a">Left</title>
    </svg>
  );
}

ArrowSVG.propTypes = {
  right: PropTypes.bool,
};

ArrowSVG.defaultProps = {
  right: false,
};

export default ArrowSVG;
