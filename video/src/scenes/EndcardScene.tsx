import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME, SPRING_BOUNCY } from '../theme';

export const EndcardScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const logoSpring = spring({
    frame,
    fps,
    config: SPRING_BOUNCY,
  });

  // Pulse animation on CTA button
  const ctaScale = interpolate(Math.sin(frame / 8), [-1, 1], [0.98, 1.02]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: THEME.bgPrimary,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: THEME.fontFamily,
      }}
    >
      {/* Background radial emerald pulse */}
      <div
        style={{
          position: 'absolute',
          width: 900,
          height: 900,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(16, 185, 129, 0.22) 0%, rgba(9, 13, 22, 0) 70%)',
        }}
      />

      <div style={{ textAlign: 'center', maxWidth: 900, zIndex: 2 }}>
        {/* Shield Logo */}
        <div
          style={{
            transform: `scale(${logoSpring})`,
            width: 96,
            height: 96,
            background: THEME.emerald,
            borderRadius: 24,
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 54,
            fontWeight: 900,
            margin: '0 auto 28px auto',
            boxShadow: '0 8px 35px rgba(16, 185, 129, 0.6)',
          }}
        >
          ✓
        </div>

        {/* Title */}
        <h1
          style={{
            fontSize: 72,
            fontWeight: 900,
            color: '#fff',
            margin: '0 0 12px 0',
            letterSpacing: -2,
          }}
        >
          TrueVerdict
        </h1>

        <p
          style={{
            fontSize: 26,
            fontWeight: 600,
            color: THEME.textMuted,
            margin: '0 0 36px 0',
            letterSpacing: -0.5,
          }}
        >
          Never get tricked by fake reviews again.
        </p>

        {/* Feature Pill Tags */}
        <div style={{ display: 'flex', gap: 14, justifyContent: 'center', marginBottom: 40 }}>
          <span
            style={{
              background: 'rgba(16, 185, 129, 0.15)',
              color: '#34d399',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              fontSize: 14,
              fontWeight: 700,
              padding: '8px 18px',
              borderRadius: 9999,
            }}
          >
            🔒 100% Client-Side Private
          </span>
          <span
            style={{
              background: 'rgba(255, 255, 255, 0.08)',
              color: '#f8fafc',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              fontSize: 14,
              fontWeight: 700,
              padding: '8px 18px',
              borderRadius: 9999,
            }}
          >
            🚫 Zero Affiliate Bias
          </span>
          <span
            style={{
              background: 'rgba(59, 130, 246, 0.15)',
              color: '#60a5fa',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              fontSize: 14,
              fontWeight: 700,
              padding: '8px 18px',
              borderRadius: 9999,
            }}
          >
            ⚡ Works On Any Store
          </span>
        </div>

        {/* CTA Button */}
        <div>
          <div
            style={{
              transform: `scale(${ctaScale})`,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 12,
              background: THEME.emerald,
              color: '#000',
              fontWeight: 900,
              fontSize: 22,
              padding: '16px 36px',
              borderRadius: 14,
              boxShadow: '0 8px 30px rgba(16, 185, 129, 0.5)',
              cursor: 'pointer',
            }}
          >
            <span>Add TrueVerdict to Chrome</span>
            <span style={{ fontSize: 26 }}>➔</span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
