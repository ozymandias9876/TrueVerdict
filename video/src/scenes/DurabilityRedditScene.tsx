import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { THEME, SPRING_BOUNCY } from '../theme';

export const DurabilityRedditScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const enterSpring = spring({
    frame,
    fps,
    config: SPRING_BOUNCY,
  });

  // Rising failure bar for 1-3 months
  const barHeight = interpolate(frame, [15, 45], [0, 85], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Reddit card pop-in
  const redditSpring = spring({
    frame: frame - 40,
    fps,
    config: SPRING_BOUNCY,
  });

  // Exit transition
  const exitOpacity = interpolate(frame, [105, 120], [1, 0], {
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
      <div style={{ textAlign: 'center', maxWidth: 1100, zIndex: 2 }}>
        {/* Title */}
        <div style={{ transform: `scale(${enterSpring})`, marginBottom: 32 }}>
          <span
            style={{
              fontSize: 18,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: 4,
              color: THEME.amber,
              display: 'block',
              marginBottom: 8,
            }}
          >
            Long-Term Truth
          </span>
          <h1
            style={{
              fontSize: 56,
              fontWeight: 900,
              color: '#fff',
              margin: 0,
              letterSpacing: -1,
            }}
          >
            Know what breaks <span style={{ color: THEME.emerald }}>BEFORE</span> you checkout.
          </h1>
        </div>

        {/* Side by side: Durability Timeline + Reddit Consensus */}
        <div style={{ display: 'flex', gap: 28, justifyContent: 'center', alignItems: 'stretch' }}>
          
          {/* Durability Card */}
          <div
            style={{
              background: THEME.bgCard,
              borderRadius: 20,
              border: `1px solid ${THEME.border}`,
              padding: '28px 36px',
              width: 480,
              textAlign: 'left',
              display: 'flex',
              flexDirection: 'column',
              gap: 16,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 16, fontWeight: 800, color: '#fff' }}>
                ⏳ When Products Break
              </span>
              <span
                style={{
                  background: 'rgba(239, 68, 68, 0.2)',
                  color: '#f87171',
                  fontWeight: 800,
                  fontSize: 12,
                  padding: '3px 10px',
                  borderRadius: 6,
                }}
              >
                High Early Failure Risk
              </span>
            </div>

            {/* Timeline Bars */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-end',
                height: 120,
                background: 'rgba(9, 13, 22, 0.6)',
                borderRadius: 12,
                padding: '16px 24px',
                border: `1px solid ${THEME.border}`,
              }}
            >
              {/* 0-30d */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 12, color: THEME.textDim }}>0</span>
                <div style={{ width: 36, height: 15, background: '#334155', borderRadius: '4px 4px 0 0' }} />
                <span style={{ fontSize: 11, color: THEME.textMuted }}>0–30d</span>
              </div>

              {/* 1-3 mo (Active alert) */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 14, fontWeight: 900, color: THEME.red }}>⚠️ 24%</span>
                <div style={{ width: 44, height: `${barHeight}%`, background: THEME.red, borderRadius: '4px 4px 0 0', boxShadow: '0 0 15px rgba(239,68,68,0.5)' }} />
                <span style={{ fontSize: 12, fontWeight: 800, color: '#fff' }}>1–3 mo</span>
              </div>

              {/* 3-6 mo */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 12, color: THEME.textDim }}>4%</span>
                <div style={{ width: 36, height: 25, background: '#334155', borderRadius: '4px 4px 0 0' }} />
                <span style={{ fontSize: 11, color: THEME.textMuted }}>3–6 mo</span>
              </div>

              {/* 6+ mo */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 12, color: THEME.textDim }}>1%</span>
                <div style={{ width: 36, height: 10, background: '#334155', borderRadius: '4px 4px 0 0' }} />
                <span style={{ fontSize: 11, color: THEME.textMuted }}>6+ mo</span>
              </div>
            </div>

            <div style={{ fontSize: 13, color: '#fde68a', background: 'rgba(245, 158, 11, 0.1)', padding: '10px 14px', borderRadius: 8, borderLeft: '3px solid #f59e0b' }}>
              <strong>Recurring Fatal Flaw:</strong> Battery stops holding charge after 60 days.
            </div>
          </div>

          {/* Reddit Consensus Card */}
          {frame >= 40 && (
            <div
              style={{
                transform: `scale(${redditSpring})`,
                background: THEME.bgCard,
                borderRadius: 20,
                border: '1px solid rgba(255, 69, 0, 0.3)',
                padding: '28px 36px',
                width: 440,
                textAlign: 'left',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                  <span style={{ background: '#ff4500', color: '#fff', fontSize: 12, fontWeight: 900, padding: '4px 10px', borderRadius: 6 }}>
                    Reddit Consensus
                  </span>
                  <span style={{ fontSize: 13, color: '#fca5a5', fontWeight: 700 }}>Avoid - Cheap E-Waste</span>
                </div>

                <div
                  style={{
                    background: 'rgba(15, 23, 42, 0.8)',
                    padding: '16px 20px',
                    borderRadius: 12,
                    borderLeft: '4px solid #ff4500',
                  }}
                >
                  <p style={{ margin: 0, fontSize: 15, color: '#f8fafc', fontStyle: 'italic', lineHeight: 1.45 }}>
                    "Cheap generic solar power banks are a fire hazard scam. The pouch battery degrades or swells after 2 months."
                  </p>
                  <span style={{ display: 'block', marginTop: 10, fontSize: 12, color: '#94a3b8', fontWeight: 700 }}>
                    — Discussion on r/gadgets (412 upvotes)
                  </span>
                </div>
              </div>

              <div style={{ fontSize: 12, color: THEME.textDim, textAlign: 'center', marginTop: 14 }}>
                🔒 100% Unbiased. Zero Sponsored Reviews.
              </div>
            </div>
          )}

        </div>
      </div>
    </AbsoluteFill>
  );
};
