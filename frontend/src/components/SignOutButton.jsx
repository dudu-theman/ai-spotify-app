import { useNavigate } from "react-router-dom";
import { useAudioPlayer } from "../contexts/AudioPlayerContext";

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

function SignOutButton() {
    const navigate = useNavigate();
    const { pauseSong } = useAudioPlayer();

    const handleSignOut = async () => {
        try {
            const res = await fetch(`${BASE_URL}/logout`, {
                method: "POST",
                credentials: "include"
            });

            if (res.ok) {
                pauseSong();
                navigate("/auth");
            } else {
                console.error("Sign out failed");
            }
        } catch (err) {
            console.error("Error signing out:", err);
        }
    };

    const styles = {
        button: {
            padding: '10px 24px',
            backgroundColor: 'rgba(226, 33, 52, 0.1)',
            border: '2px solid #e22134',
            color: '#ffffff',
            fontSize: '14px',
            fontWeight: '600'
        }
    };

    return (
        <button style={styles.button} onClick={handleSignOut}>
            Sign Out
        </button>
    );
}

export default SignOutButton;
