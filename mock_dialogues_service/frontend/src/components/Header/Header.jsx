import KeyboardArrowRightTwoToneIcon from '@mui/icons-material/KeyboardArrowRightTwoTone';
import KeyboardArrowLeftTwoToneIcon from '@mui/icons-material/KeyboardArrowLeftTwoTone';

import './Header.css';

function Header() {
  return (
    <header className="header">
      <h1>Αξιολόγηση Προτάσεων</h1>
      <div className="legend">
        <span className="arrow-left">
          <KeyboardArrowLeftTwoToneIcon />
          Όχι
        </span>
        <span className="arrow-right">
          Ναί
          <KeyboardArrowRightTwoToneIcon />
        </span>
      </div>
    </header>
  );
}

export default Header;
