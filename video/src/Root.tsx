import { Composition } from 'remotion';
import { LaunchVideo } from './LaunchVideo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 16:9 Landscape (Twitter / X, LinkedIn, YouTube Standard) */}
      <Composition
        id="TrueVerdictLaunch-16x9"
        component={LaunchVideo}
        durationInFrames={600}
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 9:16 Vertical (TikTok, Instagram Reels, YouTube Shorts) */}
      <Composition
        id="TrueVerdictLaunch-9x16"
        component={LaunchVideo}
        durationInFrames={600}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
