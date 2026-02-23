import GenieSvg from './GenieSvg';
import './Genie.css';

export default function Genie({ expression = 'idle' }) {
  return (
    <div className={`genie-wrapper ${expression}`}>
      <GenieSvg expression={expression} />
    </div>
  );
}
