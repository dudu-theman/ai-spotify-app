import {useState} from "react";
import LoginForm from "../components/LoginForm";
import SignupForm from "../components/SignupForm";

function AuthPage() {
  const [mode, setMode] = useState("login");

  const handleSignupSuccess = () => {
    setMode("login")
  }

  const styles = {
    container: {
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)'
    },
    card: {
      backgroundColor: '#242424',
      padding: '48px',
      borderRadius: '8px',
      boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
      border: '1px solid #333333',
      maxWidth: '450px',
      width: '100%'
    },
    logo: {
      textAlign: 'center',
      marginBottom: '32px',
      fontSize: '48px',
      fontWeight: 'bold',
      background: 'linear-gradient(135deg, #1db954 0%, #1ed760 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text'
    },
    toggleButton: {
      marginTop: '24px',
      width: '100%',
      backgroundColor: 'transparent',
      border: '2px solid #535353',
      color: '#e0e0e0'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.logo}>AI Music</div>

        {mode === "login" ? <LoginForm/> : <SignupForm onSignupSuccess={handleSignupSuccess}/>}

        <button
          style={styles.toggleButton}
          onClick = {() => {
            setMode(mode === "login" ? "signup" : "login")
          }}
        >
          {mode === "login" ? "Don't have an account?" : "Already have an account?"}
        </button>
      </div>
    </div>
  );

}

export default AuthPage;