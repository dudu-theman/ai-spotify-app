import {useState} from "react";

const BASE_URL = import.meta.env.VITE_BACKEND_URL;


function SignupForm(props) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const res = await fetch(`${BASE_URL}/signup`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
                credentials: "include"
            });

            const data = await res.json();

            if (res.status != 200) {
                console.log(data.message);
                setError(data.message);
                return;
            } else {
                console.log(data.message);
                setError("");
                props.onSignupSuccess();
            }

        } catch (err) {
            setError("Unexpected error ocurred");
        }
    }


    const styles = {
        form: {
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
        },
        title: {
            textAlign: 'center',
            marginBottom: '8px',
            fontSize: '24px',
            color: '#ffffff'
        },
        input: {
            backgroundColor: '#2a2a2a',
            border: '2px solid #444444',
            color: '#ffffff',
            padding: '12px 16px',
            borderRadius: '4px',
            fontSize: '16px',
            width: '100%'
        },
        submitButton: {
            marginTop: '8px',
            width: '100%'
        },
        error: {
            color: '#ff4444',
            textAlign: 'center',
            marginTop: '16px',
            fontSize: '14px',
            fontWeight: '500'
        }
    };

    return(
        <>
            <form onSubmit={handleSubmit} style={styles.form}>
                <h3 style={styles.title}>Sign Up</h3>

                <input
                    style={styles.input}
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    style={styles.input}
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit" style={styles.submitButton}>
                    Create Account
                </button>
            </form>

            {error && <p style={styles.error}>{error}</p>}
        </>
    );
}

export default SignupForm