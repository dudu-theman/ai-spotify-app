import {useState} from "react";
import {useNavigate} from "react-router-dom";

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

function LoginForm() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        try {
            const res = await fetch(`${BASE_URL}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json"}, 
                body: JSON.stringify({username, password}),
            });

            const data = await res.json();

            if (res.status != 200) {
                console.log(data.message);
                setError(data.message);
                return;
            } else {
                console.log(data.message);
                setError("");
                navigate("/home");
            }
        } catch {
            console.error(err);
            setError("Unexpected error occurred");
        }
    }



    return(
        <>
            <form onSubmit={handleSubmit}>
                <h3>Login</h3>
                
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
                <button type="submit">Log in </button>
            </form>

            {error && <p>{error}</p>}
        </>
    );
}

export default LoginForm