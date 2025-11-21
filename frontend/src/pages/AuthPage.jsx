import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from "../firebase"; 
import { createUserWithEmailAndPassword, signInWithEmailAndPassword } from "firebase/auth";

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

function AuthPage() {
  const [mode, setMode] = useState("login"); // "login" or "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // Sign up a new user (Firebase + backend)
  const handleSignup = async () => {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;

      // Add user to backend database
      await fetch(`${BASE_URL}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          firebase_uid: user.uid,
          username: user.email
        })
      });

      setError(""); // clear any previous error
      navigate("/home"); // go to HomePage
    } catch (err) {
      console.error("Signup error:", err);
      setError(err.message); // show error on screen
    }
  };

  // Login an existing user (Firebase only)
  const handleLogin = async () => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      console.log("User logged in:", userCredential.user);
      setError(""); // clear any previous error
      navigate("/home"); // go to HomePage
    } catch (err) {
      console.error("Login error:", err);
      setError("Email or password is incorrect"); // friendly error message
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>{mode === "login" ? "Login" : "Sign Up"}</h2>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      {/* Display error message if there is one */}
      {error && <p style={{ color: "red", marginTop: "8px" }}>{error}</p>}

      <button
        onClick={mode === "login" ? handleLogin : handleSignup}
        style={{ marginTop: "10px" }}
      >
        {mode === "login" ? "Login" : "Sign Up"}
      </button>

      <p style={{ marginTop: "10px" }}>
        {mode === "login" ? "Don't have an account?" : "Already have an account?"}
        <button
          onClick={() => setMode(mode === "login" ? "signup" : "login")}
          style={{ marginLeft: "8px" }}
        >
          {mode === "login" ? "Sign Up" : "Login"}
        </button>
      </p>
    </div>
  );
}

export default AuthPage;
