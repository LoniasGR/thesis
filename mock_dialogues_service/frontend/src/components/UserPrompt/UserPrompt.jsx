/* eslint-disable react/jsx-props-no-spreading */
import React from 'react';
import PropTypes from 'prop-types';
import { useCollapse } from 'react-collapsed';

import './UserPrompt.css';

function UserPrompt({ description, response }) {
  const { getCollapseProps, getToggleProps, isExpanded } = useCollapse();

  return (

    <li className={isExpanded ? 'user user-open' : 'user'}>
      <div {...getToggleProps()} className="clickable">
        {isExpanded ? 'v ' : '> ' }
        <span className="bold">Ο χρήστης ρώτησε: </span>
        {description}
      </div>
      <section {...getCollapseProps()} className="reply">
        <span className="bold">Η Θεανώ απάντησε: </span>
        {response}
      </section>
    </li>
  );
}
UserPrompt.propTypes = {
  description: PropTypes.string.isRequired,
  response: PropTypes.string.isRequired,
};

export default UserPrompt;
