import { useState } from "react";
const BASE_URL =  import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

function LoginForm () {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        const res = await fetch(`${BASE_URL}/login`, {
            method: "POST",
            headers: {"Content-Type:": "application/json"},
            body: JSON.stringify({ username, password})
        });

        const data = await res.json();
        console.log("Account Signed in.", data); 
    }

    return (
       <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            
            <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Log in</button>
        </form>
    );
}

export default LoginForm;