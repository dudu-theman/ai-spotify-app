import ViewSongsButton from '../components/ViewSongsButton.jsx'
import SignOutButton from '../components/SignOutButton.jsx'

function HomePage() {
  const styles = {
    container: {
      minHeight: 'calc(100vh - 80px)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 20px',
      textAlign: 'center',
      position: 'relative'
    },
    signOutContainer: {
      position: 'absolute',
      top: '20px',
      right: '20px'
    },
    title: {
      fontSize: '72px',
      fontWeight: 'bold',
      marginBottom: '24px',
      background: 'linear-gradient(135deg, #1db954 0%, #1ed760 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
      letterSpacing: '-0.04em'
    },
    subtitle: {
      fontSize: '20px',
      color: 'var(--text-secondary)',
      marginBottom: '48px',
      maxWidth: '600px'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.signOutContainer}>
        <SignOutButton />
      </div>
      <h1 style={styles.title}>AI Music Generator</h1>
      <p style={styles.subtitle}>Create unique, AI-generated music with just a prompt. Explore your creations or discover songs from the community.</p>
      <ViewSongsButton/>
    </div>
  );
}

export default HomePage
