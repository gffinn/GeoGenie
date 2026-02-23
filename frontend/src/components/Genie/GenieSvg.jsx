import { useMemo } from 'react';
import { EXPRESSIONS } from './expressions';

export default function GenieSvg({ expression = 'idle' }) {
  const expr = EXPRESSIONS[expression] || EXPRESSIONS.idle;

  const mouthElements = useMemo(() => {
    switch (expr.mouth) {
      case 'grin':
        return (
          <g className="genie-mouth">
            <path d="M 75,126 Q 100,152 125,126" fill="#1a1a3a" stroke="#0f1a3a" strokeWidth="1.5" />
            <path d="M 79,126 L 82,132 L 90,132 L 93,126" fill="white" />
            <path d="M 93,126 L 96,132 L 104,132 L 107,126" fill="white" />
            <path d="M 107,126 L 110,132 L 118,132 L 121,126" fill="white" />
          </g>
        );
      case 'hmm':
        return (
          <g className="genie-mouth">
            <path d="M 84,130 Q 100,126 116,130" fill="none" stroke="#1a1a3a" strokeWidth="3" strokeLinecap="round" />
          </g>
        );
      case 'frown':
        return (
          <g className="genie-mouth">
            <path d="M 80,135 Q 100,124 120,135" fill="none" stroke="#1a1a3a" strokeWidth="3" strokeLinecap="round" />
          </g>
        );
      case 'smile':
      default:
        return (
          <g className="genie-mouth">
            <path d="M 76,126 Q 100,148 124,126" fill="#1a1a3a" stroke="#0f1a3a" strokeWidth="1.5" />
            <path d="M 84,126 Q 100,133 116,126" fill="white" />
          </g>
        );
    }
  }, [expr.mouth]);

  return (
    <svg
      viewBox="-40 0 340 520"
      xmlns="http://www.w3.org/2000/svg"
      style={{ width: '100%', height: '100%', overflow: 'visible' }}
    >
      <defs>
        {/* Mask fades the entire genie to transparent at the tail */}
        <linearGradient id="fadeGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="white" />
          <stop offset="55%" stopColor="white" />
          <stop offset="100%" stopColor="black" />
        </linearGradient>
        <mask id="ghostFade">
          <rect x="-40" y="0" width="340" height="520" fill="url(#fadeGrad)" />
        </mask>

        <linearGradient id="goldGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#e8a817" />
          <stop offset="30%" stopColor="#fcd34d" />
          <stop offset="60%" stopColor="#f0b429" />
          <stop offset="100%" stopColor="#c6880b" />
        </linearGradient>
      </defs>

      {/* Single opacity group + fade mask — no overlap darkening */}
      <g opacity="0.75" mask="url(#ghostFade)">

        {/* ============================================ */}
        {/* BODY SILHOUETTE — wide shoulders, V-taper,   */}
        {/* narrow waist flowing into long S-curve tail   */}
        {/* ============================================ */}
        <path
          d={`
            M 100,30
            C 130,28 148,58 142,95
            C 138,125 132,142 120,155
            C 148,158 182,168 200,184
            C 215,198 218,215 212,232
            C 205,252 180,268 152,280
            C 132,290 120,308 115,332
            C 110,358 118,385 145,405
            C 168,422 172,445 158,465
            C 148,480 130,488 118,482
            Q 108,476 115,462
            C 125,450 128,435 118,418
            C 105,398 88,372 82,345
            C 78,322 68,302 50,288
            C 25,270 2,252 -8,235
            C -15,218 -12,200 0,186
            C 15,172 50,160 80,155
            C 68,142 62,125 58,95
            C 52,58 70,28 100,30
            Z
          `}
          fill="#4a90e2"
        />

        {/* Sash / waist belt */}
        <path
          d="M 55,280 Q 100,296 148,280"
          fill="none"
          stroke="url(#goldGrad)"
          strokeWidth="5"
          strokeLinecap="round"
        />

        {/* ============================================ */}
        {/* LEFT ARM — crosses to RIGHT (drawn first,    */}
        {/* sits behind right arm)                       */}
        {/* ============================================ */}
        <g
          className="genie-left-arm"
          style={{
            transformOrigin: '50px 180px',
            transform: `rotate(${expr.leftArm.rotate}deg)`,
            transition: 'transform 0.4s ease',
          }}
        >
          {/* Outline for definition */}
          <path
            d="M 50,180 Q 75,200 105,215"
            fill="none" stroke="#2a62b8" strokeOpacity="0.3" strokeWidth="27" strokeLinecap="round"
          />
          <path
            d="M 105,215 Q 122,222 135,218"
            fill="none" stroke="#2a62b8" strokeOpacity="0.3" strokeWidth="21" strokeLinecap="round"
          />
          {/* Arm fill */}
          <path
            d="M 50,180 Q 75,200 105,215"
            fill="none" stroke="#4a90e2" strokeWidth="24" strokeLinecap="round"
          />
          <path
            d="M 105,215 Q 122,222 135,218"
            fill="none" stroke="#4a90e2" strokeWidth="18" strokeLinecap="round"
          />
          <ellipse cx="135" cy="218" rx="12" ry="11" fill="#4a90e2" stroke="#2a62b8" strokeOpacity="0.3" strokeWidth="1.5" />
          {/* Cuff */}
          <ellipse cx="105" cy="215" rx="14" ry="6" fill="url(#goldGrad)" />
          <ellipse cx="105" cy="215" rx="14" ry="6" fill="none" stroke="#c6880b" strokeWidth="1" />
        </g>

        {/* ============================================ */}
        {/* RIGHT ARM — crosses to LEFT (drawn second,   */}
        {/* sits in front of left arm)                   */}
        {/* ============================================ */}
        <g
          className="genie-right-arm"
          style={{
            transformOrigin: '150px 180px',
            transform: `rotate(${expr.rightArm.rotate}deg)`,
            transition: 'transform 0.4s ease',
          }}
        >
          {/* Outline for definition */}
          <path
            d="M 150,180 Q 125,198 95,210"
            fill="none" stroke="#2a62b8" strokeOpacity="0.3" strokeWidth="27" strokeLinecap="round"
          />
          <path
            d="M 95,210 Q 78,217 65,213"
            fill="none" stroke="#2a62b8" strokeOpacity="0.3" strokeWidth="21" strokeLinecap="round"
          />
          {/* Arm fill */}
          <path
            d="M 150,180 Q 125,198 95,210"
            fill="none" stroke="#4a90e2" strokeWidth="24" strokeLinecap="round"
          />
          <path
            d="M 95,210 Q 78,217 65,213"
            fill="none" stroke="#4a90e2" strokeWidth="18" strokeLinecap="round"
          />
          <ellipse cx="65" cy="213" rx="12" ry="11" fill="#4a90e2" stroke="#2a62b8" strokeOpacity="0.3" strokeWidth="1.5" />
          {/* Cuff */}
          <ellipse cx="95" cy="210" rx="14" ry="6" fill="url(#goldGrad)" />
          <ellipse cx="95" cy="210" rx="14" ry="6" fill="none" stroke="#c6880b" strokeWidth="1" />
        </g>

        {/* ============================================ */}
        {/* FACE DETAILS                                 */}
        {/* ============================================ */}

        {/* Pointed ears */}
        <path d="M 62,90 Q 47,76 44,66 Q 46,78 52,90 Q 57,98 62,100" fill="#4a90e2" />
        <path d="M 138,90 Q 153,76 156,66 Q 154,78 148,90 Q 143,98 138,100" fill="#4a90e2" />
        {/* Gold earring */}
        <circle cx="48" cy="78" r="4" fill="url(#goldGrad)" />

        {/* Thick eyebrows */}
        <path
          d="M 70,74 Q 76,66 90,68"
          fill="none" stroke="#1a3a6e" strokeWidth="4.5" strokeLinecap="round"
          className="genie-left-brow"
          style={{
            transformOrigin: '80px 70px',
            transform: `translateY(${expr.leftBrow.translateY}px) rotate(${expr.leftBrow.rotate}deg)`,
            transition: 'transform 0.4s ease',
          }}
        />
        <path
          d="M 110,68 Q 124,66 130,74"
          fill="none" stroke="#1a3a6e" strokeWidth="4.5" strokeLinecap="round"
          className="genie-right-brow"
          style={{
            transformOrigin: '120px 70px',
            transform: `translateY(${expr.rightBrow.translateY}px) rotate(${expr.rightBrow.rotate}deg)`,
            transition: 'transform 0.4s ease',
          }}
        />

        {/* Eyes */}
        <g
          className="genie-left-eye"
          style={{
            transformOrigin: '83px 85px',
            transform: `scaleY(${expr.leftEye.scaleY}) translateY(${expr.leftEye.translateY}px)`,
            transition: 'transform 0.4s ease',
          }}
        >
          <ellipse cx="83" cy="85" rx="11" ry="12" fill="white" />
          <circle cx="85" cy="85" r="6" fill="#1a1a2e" />
          <circle cx="87" cy="82" r="2.5" fill="white" />
        </g>

        <g
          className="genie-right-eye"
          style={{
            transformOrigin: '117px 85px',
            transform: `scaleY(${expr.rightEye.scaleY}) translateY(${expr.rightEye.translateY}px)`,
            transition: 'transform 0.4s ease',
          }}
        >
          <ellipse cx="117" cy="85" rx="11" ry="12" fill="white" />
          <circle cx="119" cy="85" r="6" fill="#1a1a2e" />
          <circle cx="121" cy="82" r="2.5" fill="white" />
        </g>

        {/* Nose */}
        <path
          d="M 98,88 Q 96,100 90,108 Q 95,112 100,113 Q 105,112 110,108 Q 104,100 102,88"
          fill="#3a78c8" opacity="0.5"
        />
        <circle cx="94" cy="108" r="2" fill="#2a5a9e" opacity="0.3" />
        <circle cx="106" cy="108" r="2" fill="#2a5a9e" opacity="0.3" />

        {/* Mouth */}
        {mouthElements}

        {/* Goatee */}
        <path d="M 93,148 Q 96,156 100,158 Q 104,156 107,148" fill="#2a62b8" opacity="0.5" />

        {/* Cheek lines */}
        <path d="M 70,110 Q 73,120 74,126" fill="none" stroke="#2a5a9e" strokeOpacity="0.12" strokeWidth="1.5" />
        <path d="M 130,110 Q 127,120 126,126" fill="none" stroke="#2a5a9e" strokeOpacity="0.12" strokeWidth="1.5" />
      </g>
    </svg>
  );
}
