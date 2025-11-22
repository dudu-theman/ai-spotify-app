import {useState} from "react";
import LoginForm from "../components/LoginForm";
import SignupForm from "../components/SignupForm";

function AuthPage() {
  const [mode, setMode] = useState("login");

  const handleSignupSuccess = () => {
    setMode("login")
  }

  return (
    <>

      {mode === "login" ? <LoginForm/> : <SignupForm onSignupSuccess={handleSignupSuccess}/>}

      <button onClick = {() => {
        setMode(mode === "login" ? "signup" : "login")
      }}>
        {mode === "login" ? "Don't have an account?" : "Already have an account?"}
      </button>

    </>
  );

}

export default AuthPage;