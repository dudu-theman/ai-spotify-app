import { useEffect, useState } from "react";

function ShowSongs () {

    const [songs, setSongs] = useState([]);

    useEffect(() => {
        fetch("https://lofi-app-dc75.onrender.com/api/songs")
        .then(res => res.json())
        .then(data => setSongs(data));
    }, []);

    return (
        <>
            {songs.map(song => (
                <div key={song.id}>
                    <h3>{song.title}</h3>
                    <audio src={song.audio_url} controls />
                </div>
            ))

            }
        </>
    );
}

export default ShowSongs;