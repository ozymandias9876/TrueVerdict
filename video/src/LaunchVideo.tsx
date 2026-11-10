import React from 'react';
import { Sequence } from 'remotion';
import { HookScene } from './scenes/HookScene';
import { ProblemScene } from './scenes/ProblemScene';
import { MoneyShotScene } from './scenes/MoneyShotScene';
import { DurabilityRedditScene } from './scenes/DurabilityRedditScene';
import { EndcardScene } from './scenes/EndcardScene';

/**
 * 20-Second Product Launch Video for TrueVerdict
 * 600 frames @ 30fps
 *
 * Sequence:
 *   1. Hook (0-90 frames / 0-3s): The 5-star illusion
 *   2. Problem (90-180 frames / 3-6s): Dead in 2 months & review syndicates
 *   3. Money Shot (180-360 frames / 6-12s): TrueVerdict recalculation & DO NOT BUY slam
 *   4. Durability & Reddit (360-480 frames / 12-16s): 6-month timeline & Reddit consensus
 *   5. Endcard (480-600 frames / 16-20s): Brand aura & Add to Chrome CTA
 */
export const LaunchVideo: React.FC = () => {
  return (
    <>
      {/* Beat 1: Hook */}
      <Sequence from={0} durationInFrames={90}>
        <HookScene />
      </Sequence>

      {/* Beat 2: Problem */}
      <Sequence from={90} durationInFrames={90}>
        <ProblemScene />
      </Sequence>

      {/* Beat 3: Money Shot */}
      <Sequence from={180} durationInFrames={180}>
        <MoneyShotScene />
      </Sequence>

      {/* Beat 4: Durability & Reddit */}
      <Sequence from={360} durationInFrames={120}>
        <DurabilityRedditScene />
      </Sequence>

      {/* Beat 5: Endcard & CTA */}
      <Sequence from={480} durationInFrames={120}>
        <EndcardScene />
      </Sequence>
    </>
  );
};
