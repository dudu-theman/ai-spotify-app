import { useAudioPlayer } from '../contexts/AudioPlayerContext';

function MusicPlayer() {
    const { currentSong, isPlaying, currentTime, duration, togglePlayPause, seekTo } = useAudioPlayer();

    if (!currentSong) {
        return null;
    }

    const formatTime = (seconds) => {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handleProgressClick = (e) => {
        const progressBar = e.currentTarget;
        const rect = progressBar.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        const newTime = percent * duration;
        seekTo(newTime);
    };

    const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

    const styles = {
        container: {
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            backgroundColor: '#181818',
            borderTop: '1px solid #282828',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            zIndex: 1000,
            boxShadow: '0 -2px 10px rgba(0, 0, 0, 0.3)'
        },
        songInfo: {
            minWidth: '180px',
            maxWidth: '250px'
        },
        songTitle: {
            color: '#ffffff',
            fontSize: '14px',
            fontWeight: '600',
            marginBottom: '4px',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
        },
        songArtist: {
            color: '#b3b3b3',
            fontSize: '12px'
        },
        controls: {
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
        },
        playButton: {
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: '#ffffff',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'transform 0.1s ease',
            padding: 0
        },
        progressContainer: {
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
        },
        progressBar: {
            flex: 1,
            height: '4px',
            backgroundColor: '#404040',
            borderRadius: '2px',
            cursor: 'pointer',
            position: 'relative'
        },
        progressFill: {
            height: '100%',
            backgroundColor: '#1db954',
            borderRadius: '2px',
            transition: 'width 0.1s ease'
        },
        time: {
            color: '#b3b3b3',
            fontSize: '12px',
            minWidth: '40px'
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.songInfo}>
                <div style={styles.songTitle}>{currentSong.title}</div>
                <div style={styles.songArtist}>AI Generated</div>
            </div>

            <div style={styles.controls}>
                <button
                    style={styles.playButton}
                    onClick={togglePlayPause}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.06)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                >
                    {isPlaying ? (
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <rect x="3" y="2" width="3" height="12" fill="#000000" />
                            <rect x="10" y="2" width="3" height="12" fill="#000000" />
                        </svg>
                    ) : (
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M4 2L13 8L4 14V2Z" fill="#000000" />
                        </svg>
                    )}
                </button>
            </div>

            <div style={styles.progressContainer}>
                <span style={styles.time}>{formatTime(currentTime)}</span>
                <div style={styles.progressBar} onClick={handleProgressClick}>
                    <div style={{...styles.progressFill, width: `${progressPercent}%`}}></div>
                </div>
                <span style={styles.time}>{formatTime(duration)}</span>
            </div>
        </div>
    );
}

export default MusicPlayer;
