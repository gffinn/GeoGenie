import { Link, NavLink } from 'react-router-dom';
import './NavBar.css';

export default function NavBar() {
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <span className="navbar-geo">GEO</span>
        <span className="navbar-genie">Genie</span>
      </Link>
      <ul className="navbar-links">
        <li>
          <NavLink to="/" end className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
            Home
          </NavLink>
        </li>
        <li>
          <NavLink to="/about" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
            About Us
          </NavLink>
        </li>
        <li>
          <NavLink to="/how-it-works" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
            How It Works
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}
