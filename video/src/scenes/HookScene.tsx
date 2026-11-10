import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME, SPRING_BOUNCY } from '../theme';

export const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for headline
  const titleSpring = spring({
    frame,
    fps,
    config: SPRING_BOUNCY,
  });

  // Entrance spring for product card
  const cardSpring = spring({
    frame: frame - 15,
    fps,
    config: SPRING_BOUNCY,
  });

  // Stars glow pulse
  const starPulse = Math.sin(frame / 6) * 0.15 + 1;

  // Fade out transition near frame 85
  const exitOpacity = interpolate(frame, [75, 90], [1, 0], {
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
      {/* Background radial glow */}
      <div
        style={{
          position: 'absolute',
          width: 800,
          height: 800,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, rgba(9, 13, 22, 0) 70%)',
        }}
      />

      <div style={{ textAlign: 'center', maxWidth: 1200, zIndex: 2 }}>
        {/* Hook text */}
        <div
          style={{
            transform: `scale(${titleSpring}) translateY(${(1 - titleSpring) * 40}px)`,
            opacity: Math.min(1, frame / 10),
            marginBottom: 36,
          }}
        >
          <span
            style={{
              fontSize: 20,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: 4,
              color: THEME.amber,
              display: 'block',
              marginBottom: 12,
            }}
          >
            The E-Commerce Illusion
          </span>
          <h1
            style={{
              fontSize: 68,
              fontWeight: 800,
              color: THEME.textMain,
              margin: 0,
              lineHeight: 1.15,
              letterSpacing: -1.5,
            }}
          >
            Ever bought a <span style={{ color: '#fbbf24' }}>5-Star Product</span>...
          </h1>
        </div>

        {/* Gleaming Product Card */}
        {frame >= 15 && (
          <div
            style={{
              transform: `scale(${cardSpring}) translateY(${(1 - cardSpring) * 60}px)`,
              background: THEME.bgCard,
              borderRadius: 20,
              border: `1px solid ${THEME.border}`,
              padding: '32px 48px',
              maxWidth: 820,
              margin: '0 auto',
              boxShadow: '0 25px 60px -15px rgba(0,0,0,0.7)',
              display: 'flex',
              alignItems: 'center',
              gap: 36,
              textAlign: 'left',
            }}
          >
            {/* Fake Product Icon */}
            <div
              style={{
                width: 120,
                height: 120,
                borderRadius: 16,
                background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
                border: '1px solid rgba(255,255,255,0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 54,
              }}
            >
              🔋
            </div>

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <span
                  style={{
                    background: '#232f3e',
                    color: '#ff9900',
                    fontSize: 12,
                    fontWeight: 800,
                    padding: '3px 8px',
                    borderRadius: 4,
                    letterSpacing: 0.5,
                  }}
                >
                  Amazon's Choice
                </span>
                <span style={{ color: THEME.textDim, fontSize: 13 }}>#1 Best Seller</span>
              </div>

              <h2
                style={{
                  fontSize: 26,
                  fontWeight: 700,
                  color: '#fff',
                  margin: '0 0 10px 0',
                }}
              >
                UltraMax 100W Magnetic Wireless Power Bank
              </h2>

              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <span
                  style={{
                    color: '#fbbf24',
                    fontSize: 24,
                    transform: `scale(${starPulse})`,
                    display: 'inline-block',
                  }}
                >
                  ★★★★★
                </span>
                <span style={{ fontSize: 24, fontWeight: 800, color: '#fff' }}>4.9</span>
                <span style={{ fontSize: 16, color: THEME.textMuted }}>(12,480 ratings)</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};
