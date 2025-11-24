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


    return(
        <>
            <form onSubmit={handleSubmit}>
                <h3>Sign Up</h3>
                
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit">
                    Create Account
                </button>
            </form>

            {error && <p>{error}</p>}
        </>
    );
}

export default SignupForm