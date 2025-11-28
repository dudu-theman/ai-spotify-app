import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import SignOutButton from "../components/SignOutButton";

function ShowSongs() {
    const [songs, setSongs] = useState([]);
    const location = useLocation();
    const navigate = useNavigate();

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
            padding: '40px 20px',
            maxWidth: '1200px',
            margin: '0 auto'
        },
        header: {
            display: 'flex',
            alignItems: 'center',
            gap: '20px',
            marginBottom: '32px',
            flexWrap: 'wrap'
        },
        headerLeft: {
            display: 'flex',
            alignItems: 'center',
            gap: '20px',
            flex: 1,
            flexWrap: 'wrap'
        },
        backButton: {
            padding: '10px 24px',
            backgroundColor: 'transparent',
            border: '2px solid var(--border-color)',
            color: 'var(--text-secondary)',
            fontSize: '14px'
        },
        title: {
            fontSize: '48px',
            fontWeight: 'bold',
            margin: 0
        },
        songsGrid: {
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '24px'
        },
        songCard: {
            backgroundColor: 'var(--bg-secondary)',
            padding: '24px',
            borderRadius: '8px',
            transition: 'transform 0.2s ease, box-shadow 0.2s ease',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
            cursor: 'pointer'
        },
        songTitle: {
            fontSize: '18px',
            fontWeight: '600',
            marginBottom: '16px',
            color: 'var(--text-primary)'
        },
        audioPlayer: {
            width: '100%',
            borderRadius: '4px'
        },
        emptyState: {
            textAlign: 'center',
            padding: '60px 20px',
            color: 'var(--text-secondary)'
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <div style={styles.headerLeft}>
                    <button
                        style={styles.backButton}
                        onClick={() => navigate("/home")}
                    >
                        ← Back to Home
                    </button>
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
                    {songs.map(song => (
                        <div
                            key={song.id}
                            style={styles.songCard}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-4px)';
                                e.currentTarget.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.5)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)';
                                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
                            }}
                        >
                            <h3 style={styles.songTitle}>{song.title}</h3>
                            <audio
                                style={styles.audioPlayer}
                                src={song.audio_url}
                                controls
                            />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default ShowSongs;
