import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME, SPRING_BOUNCY } from '../theme';

export const MoneyShotScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for TrueVerdict badge
  const shieldSpring = spring({
    frame,
    fps,
    config: SPRING_BOUNCY,
  });

  // Card slam entrance
  const cardSpring = spring({
    frame: frame - 15,
    fps,
    config: SPRING_BOUNCY,
  });

  // Slash line animation through 4.9
  const slashProgress = interpolate(frame, [40, 55], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Recalculated true rating: 4.9 down to 1.8
  const recalculatedRating = interpolate(frame, [50, 80], [4.9, 1.8], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }).toFixed(1);

  // Badge slam for DO NOT BUY
  const badgeSlam = spring({
    frame: frame - 80,
    fps,
    config: { damping: 10, mass: 0.6, stiffness: 180 },
  });

  // Exit transition
  const exitOpacity = interpolate(frame, [165, 180], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: THEME.bgPrimary,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: THEME.fontFamily,
        opacity: exitOpacity,
      }}
    >
      {/* Emerald aura */}
      <div
        style={{
          position: 'absolute',
          width: 1000,
          height: 1000,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, rgba(9, 13, 22, 0) 70%)',
        }}
      />

      <div style={{ textAlign: 'center', maxWidth: 1100, zIndex: 2 }}>
        {/* Header Branding */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 16,
            marginBottom: 28,
            transform: `scale(${shieldSpring})`,
          }}
        >
          <div
            style={{
              width: 54,
              height: 54,
              background: THEME.emerald,
              borderRadius: 14,
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 32,
              fontWeight: 900,
              boxShadow: '0 4px 20px rgba(16, 185, 129, 0.5)',
            }}
          >
            ✓
          </div>
          <div style={{ textAlign: 'left' }}>
            <h1 style={{ fontSize: 44, fontWeight: 900, color: '#fff', margin: 0, letterSpacing: -1 }}>
              TrueVerdict
            </h1>
            <span style={{ fontSize: 16, color: THEME.emerald, fontWeight: 700, letterSpacing: 1 }}>
              The Honest Review & Durability Reality
            </span>
          </div>
        </div>

        {/* The Transformed Inspection Card */}
        {frame >= 15 && (
          <div
            style={{
              transform: `scale(${cardSpring})`,
              background: THEME.bgCard,
              borderRadius: 24,
              border: '2px solid rgba(16, 185, 129, 0.4)',
              padding: '36px 48px',
              maxWidth: 820,
              margin: '0 auto',
              boxShadow: '0 30px 80px -15px rgba(0,0,0,0.8), 0 0 40px rgba(16, 185, 129, 0.2)',
              display: 'flex',
              flexDirection: 'column',
              gap: 24,
            }}
          >
            {/* Top comparison bar */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-around',
                background: 'rgba(9, 13, 22, 0.8)',
                padding: '24px 32px',
                borderRadius: 16,
                border: `1px solid ${THEME.border}`,
              }}
            >
              {/* Claimed */}
              <div style={{ textAlign: 'center' }}>
                <span style={{ fontSize: 14, fontWeight: 700, color: THEME.textDim, textTransform: 'uppercase', letterSpacing: 1 }}>
                  Claimed Rating
                </span>
                <div style={{ position: 'relative', display: 'inline-block', marginTop: 4 }}>
                  <div style={{ fontSize: 48, fontWeight: 900, color: THEME.textMuted }}>
                    4.9★
                  </div>
                  {/* Red Slash */}
                  <div
                    style={{
                      position: 'absolute',
                      top: '50%',
                      left: 0,
                      width: `${slashProgress}%`,
                      height: 5,
                      background: THEME.red,
                      transform: 'rotate(-20deg)',
                      boxShadow: '0 0 10px rgba(239,68,68,0.8)',
                    }}
                  />
                </div>
              </div>

              {/* Arrow */}
              <div style={{ fontSize: 36, color: THEME.emerald, fontWeight: 800 }}>➔</div>

              {/* True Rating */}
              <div style={{ textAlign: 'center' }}>
                <span style={{ fontSize: 14, fontWeight: 700, color: THEME.emerald, textTransform: 'uppercase', letterSpacing: 1 }}>
                  Adjusted True Rating
                </span>
                <div style={{ fontSize: 52, fontWeight: 900, color: '#fff', marginTop: 2 }}>
                  {recalculatedRating}★
                </div>
              </div>

              {/* Slamming DO NOT BUY Badge */}
              {frame >= 80 && (
                <div
                  style={{
                    transform: `scale(${Math.max(0, badgeSlam)})`,
                    background: THEME.redDark,
                    border: `2px solid ${THEME.red}`,
                    color: '#fff',
                    fontWeight: 900,
                    fontSize: 20,
                    padding: '12px 24px',
                    borderRadius: 12,
                    boxShadow: '0 0 30px rgba(239, 68, 68, 0.6)',
                    letterSpacing: 1,
                  }}
                >
                  🚫 DO NOT BUY
                </div>
              )}
            </div>

            {/* Authenticity Row */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                background: 'rgba(239, 68, 68, 0.08)',
                padding: '16px 24px',
                borderRadius: 12,
                border: '1px solid rgba(239, 68, 68, 0.3)',
              }}
            >
              <div style={{ textAlign: 'left' }}>
                <span style={{ fontSize: 16, fontWeight: 800, color: '#fca5a5' }}>
                  🛡️ Review Authenticity: Grade D (52%)
                </span>
                <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#cbd5e1' }}>
                  ⚠️ Review Syndicate Detected: Multiple accounts sharing identical copy-pasted praise.
                </p>
              </div>
              <span
                style={{
                  background: THEME.red,
                  color: '#fff',
                  fontWeight: 900,
                  fontSize: 14,
                  padding: '6px 14px',
                  borderRadius: 8,
                }}
              >
                Grade D
              </span>
            </div>
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
