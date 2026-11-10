import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME, SPRING_BOUNCY } from '../theme';

export const ProblemScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const enterSpring = spring({
    frame,
    fps,
    config: SPRING_BOUNCY,
  });

  // Ticking day counter: Day 1 -> Day 60
  const dayCount = Math.min(60, Math.floor(interpolate(frame, [15, 60], [1, 60], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  })));

  // Exit transition
  const exitOpacity = interpolate(frame, [75, 90], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#0d090d',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: THEME.fontFamily,
        opacity: exitOpacity,
      }}
    >
      {/* Red danger glow */}
      <div
        style={{
          position: 'absolute',
          width: 900,
          height: 900,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(239, 68, 68, 0.18) 0%, rgba(13, 9, 13, 0) 70%)',
        }}
      />

      <div style={{ textAlign: 'center', maxWidth: 1200, zIndex: 2 }}>
        {/* Punchline Headline */}
        <div
          style={{
            transform: `scale(${enterSpring}) translateY(${(1 - enterSpring) * 30}px)`,
            marginBottom: 36,
          }}
        >
          <span
            style={{
              fontSize: 20,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: 4,
              color: THEME.red,
              display: 'block',
              marginBottom: 10,
            }}
          >
            The 60-Day Reality
          </span>
          <h1
            style={{
              fontSize: 68,
              fontWeight: 800,
              color: '#fff',
              margin: 0,
              lineHeight: 1.15,
              letterSpacing: -1.5,
            }}
          >
            ...that <span style={{ color: THEME.red, textDecoration: 'underline' }}>died completely</span> in 2 months?
          </h1>
        </div>

        {/* Counter and Fake Review Cards */}
        <div style={{ display: 'flex', gap: 24, justifyContent: 'center', alignItems: 'stretch' }}>
          
          {/* Day Counter Box */}
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: `2px solid ${THEME.red}`,
              borderRadius: 16,
              padding: '24px 36px',
              width: 260,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <span style={{ fontSize: 13, fontWeight: 700, color: THEME.textMuted, textTransform: 'uppercase' }}>
              Ownership Timeline
            </span>
            <span style={{ fontSize: 64, fontWeight: 900, color: dayCount >= 60 ? THEME.red : '#fff' }}>
              Day {dayCount}
            </span>
            <span
              style={{
                fontSize: 14,
                fontWeight: 700,
                color: dayCount >= 60 ? '#fca5a5' : THEME.amber,
                background: dayCount >= 60 ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)',
                padding: '4px 10px',
                borderRadius: 9999,
              }}
            >
              {dayCount < 30 ? 'Initial Praise (Day 1)' : (dayCount < 60 ? 'Return Window Expired' : '⚠️ Battery Failed')}
            </span>
          </div>

          {/* Fake Review Syndicate Callout */}
          <div
            style={{
              background: THEME.bgCard,
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 16,
              padding: '24px 32px',
              width: 520,
              textAlign: 'left',
              display: 'flex',
              flexDirection: 'column',
              gap: 12,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 12, fontWeight: 800, color: '#f87171', background: 'rgba(239,68,68,0.2)', padding: '2px 8px', borderRadius: 4 }}>
                ⚠️ Copy-Pasted Review Syndicate
              </span>
              <span style={{ fontSize: 11, color: THEME.textDim }}>Detected across 4 accounts</span>
            </div>

            <div style={{ background: 'rgba(15,23,42,0.8)', padding: '10px 14px', borderRadius: 8, borderLeft: '3px solid #ef4444' }}>
              <div style={{ fontSize: 11, color: '#fbbf24' }}>★★★★★ <span style={{ color: '#94a3b8' }}>Account: Alex K. (Unverified)</span></div>
              <div style={{ fontSize: 13, color: '#fff', fontStyle: 'italic', marginTop: 2 }}>
                "In conclusion, this product exceeded all expectations! A game changer in every sense."
              </div>
            </div>

            <div style={{ background: 'rgba(15,23,42,0.8)', padding: '10px 14px', borderRadius: 8, borderLeft: '3px solid #ef4444' }}>
              <div style={{ fontSize: 11, color: '#fbbf24' }}>★★★★★ <span style={{ color: '#94a3b8' }}>Account: Sarah M. (Unverified)</span></div>
              <div style={{ fontSize: 13, color: '#fff', fontStyle: 'italic', marginTop: 2 }}>
                "In conclusion, this product exceeded all expectations! A game changer in every sense."
              </div>
            </div>
          </div>

        </div>
      </div>
    </AbsoluteFill>
  );
};
