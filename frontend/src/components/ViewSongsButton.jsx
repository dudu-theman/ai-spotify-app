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
            fontSize: '16px'
        },
        secondaryButton: {
            padding: '14px 40px',
            fontSize: '16px',
            backgroundColor: 'transparent',
            border: '2px solid var(--accent-primary)',
            color: 'var(--accent-primary)'
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
