/* eslint-disable react/jsx-props-no-spreading */
import {
  useLayoutEffect, useState, useRef, useEffect, React,
} from 'react';
import PropTypes from 'prop-types';
import Collapse from '@mui/material/Collapse';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';

import './UserPrompt.css';

function UserPrompt({
  description, response, demonstrate, className,
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const collapsible = useRef();

  useEffect(() => {
    if (demonstrate) {
      setTimeout(() => {
        setIsExpanded(true);
        setTimeout(() => {
          setIsExpanded(false);
        }, 2000);
      }, 2000);
    }
  }, [demonstrate]);

  useLayoutEffect(() => {
    let startTouchPosX;
    let startTouchPosY;
    const elem = collapsible.current;
    const onClick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsExpanded(!isExpanded);
    };

    const onTouchEnd = (e) => {
      e.preventDefault();
      const endTouchPosY = e.changedTouches[0].clientY;
      const endTouchPosX = e.changedTouches[0].clientX;
      const movement = Math.abs(endTouchPosX - startTouchPosX)
      + Math.abs(endTouchPosY - startTouchPosY);
      if (movement < 10) {
        setIsExpanded(!isExpanded);
      }
      elem.removeEventListener(('touchend'), onTouchEnd);
    };

    const onTouchStart = (e) => {
      e.preventDefault();
      startTouchPosY = e.changedTouches[0].clientY;
      startTouchPosX = e.changedTouches[0].clientX;

      elem.addEventListener(('touchend'), onTouchEnd);
    };

    elem.addEventListener(('click'), onClick);
    elem.addEventListener(('touchstart'), onTouchStart);
    return () => {
      elem.removeEventListener(('click'), onClick);
      elem.removeEventListener(('touchstart'), onTouchStart);
    };
  }, [collapsible, isExpanded, setIsExpanded]);

  return (
    <li className={`${className} ${isExpanded ? 'user user-open' : 'user'}`} ref={collapsible}>
      <div className="clickable">
        {isExpanded ? <ArrowRightIcon className="rotated" /> : <ArrowRightIcon /> }
        <div>
          <span className="bold user-question">Ο χρήστης ρώτησε: </span>
          {description}
        </div>
      </div>
      <Collapse in={isExpanded}>
        <div className="reply">
          <span className="bold">Η Θεανώ απάντησε: </span>
          {response}
        </div>
      </Collapse>
    </li>
  );
}
UserPrompt.propTypes = {
  description: PropTypes.string.isRequired,
  response: PropTypes.string.isRequired,
  demonstrate: PropTypes.bool,
  className: PropTypes.string,
};

UserPrompt.defaultProps = {
  demonstrate: false,
  className: '',
};

export default UserPrompt;
