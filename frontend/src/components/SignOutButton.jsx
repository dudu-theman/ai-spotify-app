import { useNavigate } from "react-router-dom";

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

function SignOutButton() {
    const navigate = useNavigate();

    const handleSignOut = async () => {
        console.log("Sign Out button clicked!");
        console.log("BASE_URL:", BASE_URL);

        try {
            const res = await fetch(`${BASE_URL}/logout`, {
                method: "POST",
                credentials: "include"
            });

            console.log("Response status:", res.status);
            console.log("Response ok:", res.ok);

            if (res.ok) {
                console.log("Navigating to /auth");
                navigate("/auth");
            } else {
                console.error("Sign out failed with status:", res.status);
                const data = await res.json();
                console.error("Error data:", data);
            }
        } catch (err) {
            console.error("Error signing out:", err);
        }
    };

    const styles = {
        button: {
            padding: '10px 24px',
            backgroundColor: 'transparent',
            border: '2px solid var(--error-color)',
            color: 'var(--error-color)',
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
