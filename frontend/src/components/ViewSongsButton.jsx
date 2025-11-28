import { useNavigate } from "react-router-dom";

function ViewSongsButton() {
    const navigate = useNavigate();

    const styles = {
        container: {
            display: 'flex',
            gap: '16px',
            flexWrap: 'wrap',
            justifyContent: 'center'
        },
        primaryButton: {
            padding: '14px 40px',
            fontSize: '16px',
            backgroundColor: '#1db954',
            color: '#000000',
            fontWeight: '700',
            boxShadow: '0 0 20px rgba(29, 185, 84, 0.4), 0 2px 8px rgba(0, 0, 0, 0.3)'
        },
        secondaryButton: {
            padding: '14px 40px',
            fontSize: '16px',
            backgroundColor: 'rgba(29, 185, 84, 0.15)',
            border: '2px solid #1db954',
            color: '#1ed760',
            fontWeight: '600',
            boxShadow: '0 0 20px rgba(29, 185, 84, 0.3), 0 2px 8px rgba(0, 0, 0, 0.3)'
        }
    };

    return (
        <div style={styles.container}>
            <button
                style={styles.primaryButton}
                onClick={() => navigate("/showsongs?type=private")}
            >
                View Your Creations
            </button>

            <button
                style={styles.secondaryButton}
                onClick={() => navigate("/showsongs?type=public")}
            >
                Explore Existing Songs
            </button>
        </div>
    );
}

export default ViewSongsButton;
