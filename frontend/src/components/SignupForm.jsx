import { useState } from "react";
const BASE_URL =  import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

function SignupForm () {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        const res = await fetch(`${BASE_URL}/signup`, {
            method: "POST",
            headers: {"Content-Type:": "application/json"},
            body: JSON.stringify({ username, password})
        });

        const data = await res.json();
        console.log("Account created!", data); 
    }

    return (
       <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Choose a username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            
            <input
                type="password"
                placeholder="Choose a password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Create Account</button>
        </form>
    );
}

export default SignupForm;