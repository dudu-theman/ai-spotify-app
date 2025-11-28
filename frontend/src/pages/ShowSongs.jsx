import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import SignOutButton from "../components/SignOutButton";
import { useAudioPlayer } from "../contexts/AudioPlayerContext";

function ShowSongs() {
    const [songs, setSongs] = useState([]);
    const location = useLocation();
    const navigate = useNavigate();
    const { playSong, currentSong, isPlaying } = useAudioPlayer();

    // read the query param: "private" or "public"
    const params = new URLSearchParams(location.search);
    const type = params.get("type") || "private"; // default private

    useEffect(() => {
        async function loadSongs() {
            const endpoint =
                type === "public"
                    ? "/api/songs/public"
                    : "/api/songs/private";

            const res = await fetch(
                `https://lofi-app-dc75.onrender.com${endpoint}`,
                { credentials: "include" }
            );

            const data = await res.json();
            setSongs(data);
        }

        loadSongs();
    }, [type]); // reload when type changes

    const styles = {
        container: {
            padding: '40px 20px 100px',
            backgroundColor: '#0a0a0a',
            minHeight: '100vh'
        },
        header: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '20px',
            marginBottom: '48px',
            flexWrap: 'wrap',
            position: 'relative'
        },
        backButton: {
            padding: '10px 24px',
            backgroundColor: 'rgba(29, 185, 84, 0.1)',
            border: '2px solid #1db954',
            color: '#ffffff',
            fontSize: '14px',
            fontWeight: '600'
        },
        titleContainer: {
            position: 'absolute',
            left: '50%',
            transform: 'translateX(-50%)',
            textAlign: 'center'
        },
        title: {
            fontSize: '48px',
            fontWeight: 'bold',
            margin: 0,
            color: '#ffffff'
        },
        songsGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '24px'
        },
        songCard: {
            backgroundColor: '#1a1a1a',
            padding: '24px',
            borderRadius: '8px',
            transition: 'transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
            cursor: 'pointer',
            border: '2px solid transparent'
        },
        songCardActive: {
            border: '2px solid #1db954',
            boxShadow: '0 4px 12px rgba(29, 185, 84, 0.3)'
        },
        songTitle: {
            fontSize: '18px',
            fontWeight: '600',
            marginBottom: '16px',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
        },
        playIcon: {
            color: '#1db954',
            fontSize: '16px'
        },
        emptyState: {
            textAlign: 'center',
            padding: '60px 20px',
            color: '#ffffff',
            fontSize: '18px'
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <button
                    style={styles.backButton}
                    onClick={() => navigate("/home")}
                >
                    ← Back to Home
                </button>

                <div style={styles.titleContainer}>
                    <h2 style={styles.title}>{type === "public" ? "Public Songs" : "Your Songs"}</h2>
                </div>

                <SignOutButton />
            </div>

            {songs.length === 0 ? (
                <div style={styles.emptyState}>
                    <p>No songs found. Start creating some music!</p>
                </div>
            ) : (
                <div style={styles.songsGrid}>
                    {songs.map(song => {
                        const isCurrentSong = currentSong?.id === song.id;
                        const cardStyle = isCurrentSong
                            ? {...styles.songCard, ...styles.songCardActive}
                            : styles.songCard;

                        return (
                            <div
                                key={song.id}
                                style={cardStyle}
                                onClick={() => playSong(song)}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.transform = 'translateY(-4px)';
                                    e.currentTarget.style.boxShadow = isCurrentSong
                                        ? '0 8px 20px rgba(29, 185, 84, 0.4)'
                                        : '0 8px 20px rgba(0, 0, 0, 0.5)';
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'translateY(0)';
                                    e.currentTarget.style.boxShadow = isCurrentSong
                                        ? '0 4px 12px rgba(29, 185, 84, 0.3)'
                                        : '0 4px 12px rgba(0, 0, 0, 0.3)';
                                }}
                            >
                                <h3 style={styles.songTitle}>
                                    {isCurrentSong && isPlaying && <span style={styles.playIcon}>♫</span>}
                                    {song.title}
                                </h3>
                                <p style={{color: '#b3b3b3', fontSize: '14px', margin: 0}}>
                                    Click to play
                                </p>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

export default ShowSongs;
